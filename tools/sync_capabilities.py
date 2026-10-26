"""从本机内核生成技能仓库的 `capabilities.json` 快照，并刷新 SKILL.md 里的能力块。

技能是独立仓库：装到别的机器上时可能没装内核。所以能力清单落成**带出处**的 JSON，
技能自带、离线可校验；刷新时在本机跑一次（前提：内核可 import 或是 git 仓库）。

    python tools/sync_capabilities.py            # 刷新快照 + 重渲染 SKILL.md 索引
    python tools/sync_capabilities.py --check    # 只比对，不写
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SNAPSHOT = os.path.join(ROOT, "capabilities.json")
SKILL = os.path.join(ROOT, "SKILL.md")

BEGIN = "<!-- gen:capabilities:BEGIN -->"
END = "<!-- gen:capabilities:END -->"

KERNEL_REPO = "https://github.com/Winterwind2017/autoshopkit"
KERNEL_DIR = os.environ.get("AUTOSHOPKIT_SRC", r"D:\bililive\autoshopkit")

FAMILY_LABEL = {
    "proj": "工程文件（离线）",
    "il": "指令表 / IL",
    "audit": "体检与判据",
    "ui": "AutoShop 界面通道",
    "edit": "写入（编辑）",
    "build": "编译与保存",
    "dl": "下载侧",
    "cmd": "命令与目录",
    "cli": "命令行",
}

# id -> (family, level, 证据)
# L1 只读文件 · L2 只读界面 · L3 写工程 · L4 编译/下载产物
CAPS: dict[str, tuple[str, str, str]] = {
    # ---- 工程文件（离线，不需要 AutoShop） ----
    "proj.hcp_read": ("proj", "L1", "test_hcp 17/17（H3U+H5U 两个真工程）"),
    "proj.hcp_write": ("proj", "L1", "test_hcp：未改动 XML 加解密后字节一致"),
    "proj.hcp_fields": ("proj", "L1", "test_hcp：GCMModal/Capbility/HardwareFile/projnameex"),
    "proj.hcp_files": ("proj", "L1", "test_hcp：H3U 16 条 / H5U 51 条组件记录，且点名文件在盘上"),
    "proj.hcpp_read": ("proj", "L1", "test_projectfile + test_hcp：4 个备份样本同形状"),
    "proj.component_chunks": ("proj", "L1", "0x80 头 + 具名 chunk（CLVTItem/CGVTItem/CElemMonItem/CCrossRefInfo）"),
    "proj.symbols": ("proj", "L1", "test_projectfile：H3U/H5U 两种 CGVTItem 布局"),
    "proj.var_table": ("proj", "L1", "test_offline_audit：VarNameAndAddr.csv 1412 行"),
    "proj.monitor": ("proj", "L1", "test_projectfile：CElemMonItem"),
    "proj.crossref": ("proj", "L1", "test_offline_audit：8809 行 / 3692 元件"),
    "proj.ld_text": ("proj", "L1", "test_projectfile：元素文本与网络注释"),
    "proj.ld_graph": ("proj", "L1", "test_ladder 15/15：kind + 图链接，文件无坐标表"),
    # ---- IL ----
    "il.parse": ("il", "L1", "test_ilparse 17/17"),
    "il.roles": ("il", "L1", "test_ilparse：操作数 r/w/rw 分类，支撑 W150/I120"),
    "il.log_read": ("il", "L1", "test_h5u_il：il_log.log 3968 步"),
    "il.log_split": ("il", "L1", "test_h5u_il：MAIN 长度 = Compile/*.compile 指令数"),
    "il.ui_read": ("il", "L2", "e2e_programs 9/9（H3U Scintilla）"),
    "il.ui_write": ("il", "L3", "e2e_programs/e2e_apply：真全选 + 剪贴板粘贴"),
    # ---- 体检 ----
    "audit.offline": ("audit", "L1", "test_offline_audit 10/10"),
    "audit.codes": ("audit", "L1", "docs/CHECK.md：W101/W110/W120/W130/W140/W150/I100/I110/I120/I130"),
    "audit.ui": ("audit", "L3", "e2e_check 11/11"),
    # ---- 界面 ----
    "ui.launch": ("ui", "L2", "e2e 14/14"),
    "ui.attach": ("ui", "L2", "e2e_cli 17/17"),
    "ui.tree": ("ui", "L2", "e2e：40 字节 TVITEMW + 折叠行 rect 是邻居；H5U 工程树是 cid=2"),
    "ui.open_program": ("ui", "L3", "e2e_programs：展开父 → 单击 → 核对 TVGN_CARET → 双击"),
    "ui.documents": ("ui", "L2", "e2e：Ctrl+Tab 切文档 + 标题/编辑器双判"),
    "ui.compile": ("ui", "L3", "e2e/e2e_programs：编译并解析诊断"),
    "ui.diagnostics": ("ui", "L2", "e2e_check：输出窗自绘，靠 Frida hook DrawTextW"),
    "ui.screenshot": ("ui", "L2", "e2e：窗口抓图"),
    "ui.dialogs": ("ui", "L2", "e2e_cli：枚举/关闭模态框"),
    "ui.doctor": ("ui", "L2", "e2e：树/文档/编辑器/输出窗/Frida 自检"),
    "ui.stop": ("ui", "L2", "e2e：关进程、释放 .hcp 锁"),
    # ---- 写入 ----
    "edit.symbols": ("edit", "L3", "e2e_symbols 9/9"),
    "edit.monitor": ("edit", "L3", "e2e_monitor 6/6"),
    "edit.new_project": ("edit", "L3", "e2e_create 6/6"),
    "edit.save": ("edit", "L3", "e2e：只重写脏部件并报 changed_files"),
    "build.check": ("build", "L3", "e2e_check 11/11"),
    # ---- 下载侧 ----
    "dl.offline_file": ("dl", "L3", "生成下载文件 → 下载选项 → 生成 → Shell 另存为"),
    # ---- 命令目录 ----
    "cmd.wm_command": ("cmd", "L2", "e2e：菜单是 CMFCMenuBar，命令走 WM_COMMAND + ID"),
    "cmd.catalog": ("cmd", "L1", "docs/COMMANDS.md：4500 条命令/字符串目录"),
    # ---- CLI ----
    "cli.verbs": ("cli", "L1", "e2e_cli 17/17：每个 verb 子进程跑一遍"),
}

# 还没打通 / 条件不具备（技能里"别试这些"用）
PENDING = [
    ("dl.to_plc", "真正下载要连机与授权；只到『生成离线下载文件』"),
    ("monitor.live", "在线监控读数需要真实 PLC"),
    ("h5u.ladder_write", "H5U 文档没有指令表编辑器（Scintilla 数为 0），写入通道只对 H3U 成立"),
    ("h5u.ladder_click", "梯形图是自绘画布，UIA 无子元素，只能盲点"),
    ("monitor.grid_export", "网格是 VSFlexGrid8N，没有剪贴板导出，只能逐格读"),
]


def kernel_commit() -> str:
    try:
        out = subprocess.run(["git", "-C", KERNEL_DIR, "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=20)
        return out.stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001 - 快照不需要这个字段也能用
        return "unknown"


def cli_commands() -> list[str]:
    if KERNEL_DIR not in sys.path:
        sys.path.insert(0, os.path.join(KERNEL_DIR, "src"))
    try:
        from autoshopkit import cli  # noqa: F401
        import inspect
        import re
        text = inspect.getsource(cli)
        return sorted(set(re.findall(r'sub\.add_parser\(\s*"([a-z0-9_]+)"', text)))
    except Exception:  # noqa: BLE001
        return []


def build_snapshot() -> dict:
    families = {}
    for cap_id, (family, _level, _evidence) in CAPS.items():
        families[family] = families.get(family, 0) + 1
    return {
        "schema": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "provenance": {
            "kernel": "autoshopkit",
            "kernel_repo": KERNEL_REPO,
            "kernel_commit": kernel_commit(),
            "engine": "AutoShop V4.11.0.5",
        },
        "cli_commands": cli_commands(),
        "counts": {"verified": len(CAPS), "families": len(families), "pending": len(PENDING)},
        "verified": {cap: info[0] for cap, info in CAPS.items()},
        "levels": {cap: info[1] for cap, info in CAPS.items()},
        "evidence": {cap: info[2] for cap, info in CAPS.items()},
        "pending": [{"id": cap, "reason": reason} for cap, reason in PENDING],
    }


def render_block(snapshot: dict) -> str:
    lines = [BEGIN, "", "| 能力 | 族 | 级别 | 证据 |", "| --- | --- | --- | --- |"]
    for family in FAMILY_LABEL:
        for cap, info in CAPS.items():
            if info[0] != family:
                continue
            lines.append("| `%s` | %s | %s | %s |" % (cap, FAMILY_LABEL[family], info[1], info[2]))
    lines += ["", "<!-- 由 tools/sync_capabilities.py 生成，勿手改 -->", END]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="只比对")
    args = parser.parse_args(argv)

    snapshot = build_snapshot()
    rendered = render_block(snapshot)

    skill_text = open(SKILL, encoding="utf-8").read()
    if BEGIN in skill_text and END in skill_text:
        head, rest = skill_text.split(BEGIN, 1)
        _old, tail = rest.split(END, 1)
        new_skill = head + rendered + tail
    else:
        new_skill = skill_text + "\n\n" + rendered + "\n"

    current = open(SNAPSHOT, encoding="utf-8").read() if os.path.exists(SNAPSHOT) else ""
    new_json = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"

    json_same = json.loads(current)["verified"] == snapshot["verified"] if current else False
    skill_same = new_skill == skill_text

    if args.check:
        if json_same and skill_same:
            print("capabilities: 一致（%d 条 verified / %d 条 pending）" %
                  (snapshot["counts"]["verified"], snapshot["counts"]["pending"]))
            return 0
        print("capabilities: **不一致**，跑一次 tools/sync_capabilities.py")
        return 3

    open(SNAPSHOT, "w", encoding="utf-8").write(new_json)
    md = ["# 能力清单（快照）", "",
          "由 `tools/sync_capabilities.py` 从内核生成；出处 `%s@%s`。" % (
              snapshot["provenance"]["kernel"], snapshot["provenance"]["kernel_commit"]),
          "", "## 已打通（%d）" % snapshot["counts"]["verified"], "",
          "| 能力 | 族 | 级别 | 证据 |", "| --- | --- | --- | --- |"]
    for cap, info in CAPS.items():
        md.append("| `%s` | %s | %s | %s |" % (cap, FAMILY_LABEL[info[0]], info[1], info[2]))
    md += ["", "## 未打通（%d）" % snapshot["counts"]["pending"], ""]
    for cap, reason in PENDING:
        md.append("- `%s` — %s" % (cap, reason))
    open(os.path.join(ROOT, "capabilities.md"), "w", encoding="utf-8").write("\n".join(md) + "\n")
    open(SKILL, "w", encoding="utf-8").write(new_skill)
    print("wrote %s (%d verified / %d pending, kernel %s)" % (
        os.path.basename(SNAPSHOT), snapshot["counts"]["verified"],
        snapshot["counts"]["pending"], snapshot["provenance"]["kernel_commit"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
