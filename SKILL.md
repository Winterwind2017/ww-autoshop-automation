---
name: ww-autoshop-automation
description: >
  用 autoshopkit 在本机汇川 AutoShop V4.11 上做离线工程分析与在线编程自动化，并**用读数验证结果**。
  当用户要求读 .hcp 工程索引、读符号/变量表/交叉引用、读梯形图元件或 H5U 的 IL、
  跑工程体检、打开/新建工程、读写程序（H3U 指令表）、编译并读诊断、生成离线下载文件，
  或问"AutoShop 某个操作能不能自动化、为什么假成功"时使用。内含实测配方、判据、
  已证伪路径，以及这套 MFC 程序特有的坑（CMFCMenuBar、TVITEMW、自绘输出窗、cid=2 的树）。
  Use for Inovance AutoShop automation, .hcp/.LD/H5U file inspection, H3U instruction-list
  editing, compile diagnostics, and diagnosing silent no-op UI actions.
---

# ww-autoshop-automation

> **这是独立技能仓库**，不随执行内核一起分发。
> 内核是 [autoshopkit](https://github.com/Winterwind2017/autoshopkit)（Python 库 + CLI，24 个 verb），
> 本仓库只负责"**怎么用 + 怎么验证 + 什么别试**"。
> 能力清单以 `capabilities.json` 快照为准（出处：内核 commit + AutoShop 版本）。

## 这个技能解决什么

AutoShop 是 MFC MDI 程序：**没有 COM、没有 DDE、没有脚本接口**，菜单是 `CMFCMenuBar`
（`GetMenu` 返回 NULL），输出窗是自绘 `ListBox`，程序编辑器只有 H3U 才是 `Scintilla`。
于是几乎所有"看起来成功了"的操作都是**假成功**：

- 点了树上一行，程序没打开（**双击文件夹行只是展开**）；
- `SCI_SETTEXT` 写进了缓冲区，切文档就丢；
- 编译"跑完了"，但诊断根本没读到（输出窗取文本返回 NUL）；
- 调用返回 `True`，`.LD` 一个字节没变。

这个技能把它们固化成三样东西：**配方**（怎么调）、**判据**（怎么证明成功）、
**未打通清单**（省得重复踩）。

## 开工前 30 秒

1. `autoshopkit status` —— 连上没有？没连就 `start <工程.hcp>`。
2. `autoshopkit doctor` —— 树/文档/编辑器/输出窗/Frida 五项自检，`dialogs_open` 必须为空。
3. `autoshopkit commands --search <关键词>` —— **先查命令 ID 再发命令**，别猜。
4. 想清楚这次的判据：`program_il(strict=True)` 读回？`compile()` 的错误数？
   `project_check()` 的 findings？`hcp.read_project()` 的字段？说不出来就先别动手。

没装内核时：

```bash
pip install -e <autoshopkit 仓库>        # 或 PYTHONPATH=<repo>/src
autoshopkit status
```

## 铁律（违反必踩坑）

1. **先离线，后在线**：能用文件读到的（工程索引、符号、交叉引用、梯形图文本、H5U 的 IL）
   就不要开界面。离线快、可重复、不动客户工程。
2. **客户工程只读副本**：`sandbox/` 之外一律不写。所有 e2e 都从模板工程复制一份再改。
3. **写入必须"真全选 + 粘贴"**：`SCI_SETTEXT` 只改缓冲区。写完立刻用
   `program_il(strict=True)` 回读。
4. **打开程序看新文档**：`open_program()` 的成功判据是"出现新文档句柄"，
   不是"点了两下"。
5. **读输出窗前先确认 hook 在**：`doctor` 里 `output_pane=true` 才算读得到诊断。
6. **H5U 不要试图写梯形图**：没有指令表编辑器；读法是编译产物 `il_log.log`。
7. **`.hcp` 被打开时独占锁**：要读文件先 `stop`。
8. **一次只跑一套测试**：两个套件并行会抢同一个实例，报 `COMError 事件无法调用任何订户`。

## 两条通道

**离线（推荐先做）**

```bash
autoshopkit hcp --project <工程目录>       # 工程索引：系列/容量/硬件 dll/组件表
autoshopkit illog --project <工程目录> --paths   # H5U：按程序拆分的 IL
autoshopkit check --offline <工程目录>     # 静态体检
```

**在线**

```bash
autoshopkit start <工程.hcp>
autoshopkit open 程序块 MAIN
autoshopkit il                    # H3U 读
autoshopkit apply -f prog.il      # H3U 写（真全选+粘贴）
autoshopkit compile
autoshopkit check
autoshopkit save
```

Python 侧同名能力：`app.open_program` / `app.program_il` / `app.apply_program` /
`app.compile` / `app.project_check`，以及 `projectfile.*`、`hcp.*`。

## 能力清单（自动生成）

<!-- gen:capabilities:BEGIN -->

| 能力 | 族 | 级别 | 证据 |
| --- | --- | --- | --- |
| `proj.hcp_read` | 工程文件（离线） | L1 | test_hcp 17/17（H3U+H5U 两个真工程） |
| `proj.hcp_write` | 工程文件（离线） | L1 | test_hcp：未改动 XML 加解密后字节一致 |
| `proj.hcp_fields` | 工程文件（离线） | L1 | test_hcp：GCMModal/Capbility/HardwareFile/projnameex |
| `proj.hcp_files` | 工程文件（离线） | L1 | test_hcp：H3U 16 条 / H5U 51 条组件记录，且点名文件在盘上 |
| `proj.hcpp_read` | 工程文件（离线） | L1 | test_projectfile + test_hcp：4 个备份样本同形状 |
| `proj.component_chunks` | 工程文件（离线） | L1 | 0x80 头 + 具名 chunk（CLVTItem/CGVTItem/CElemMonItem/CCrossRefInfo） |
| `proj.symbols` | 工程文件（离线） | L1 | test_projectfile：H3U/H5U 两种 CGVTItem 布局 |
| `proj.var_table` | 工程文件（离线） | L1 | test_offline_audit：VarNameAndAddr.csv 1412 行 |
| `proj.monitor` | 工程文件（离线） | L1 | test_projectfile：CElemMonItem |
| `proj.crossref` | 工程文件（离线） | L1 | test_offline_audit：8809 行 / 3692 元件 |
| `proj.ld_text` | 工程文件（离线） | L1 | test_projectfile：元素文本与网络注释 |
| `proj.ld_graph` | 工程文件（离线） | L1 | test_ladder 15/15：kind + 图链接，文件无坐标表 |
| `il.parse` | 指令表 / IL | L1 | test_ilparse 17/17 |
| `il.roles` | 指令表 / IL | L1 | test_ilparse：操作数 r/w/rw 分类，支撑 W150/I120 |
| `il.log_read` | 指令表 / IL | L1 | test_h5u_il：il_log.log 3968 步 |
| `il.log_split` | 指令表 / IL | L1 | test_h5u_il：MAIN 长度 = Compile/*.compile 指令数 |
| `il.ui_read` | 指令表 / IL | L2 | e2e_programs 9/9（H3U Scintilla） |
| `il.ui_write` | 指令表 / IL | L3 | e2e_programs/e2e_apply：真全选 + 剪贴板粘贴 |
| `audit.offline` | 体检与判据 | L1 | test_offline_audit 10/10 |
| `audit.codes` | 体检与判据 | L1 | docs/CHECK.md：W101/W110/W120/W130/W140/W150/I100/I110/I120/I130 |
| `audit.ui` | 体检与判据 | L3 | e2e_check 11/11 |
| `ui.launch` | AutoShop 界面通道 | L2 | e2e 14/14 |
| `ui.attach` | AutoShop 界面通道 | L2 | e2e_cli 17/17 |
| `ui.tree` | AutoShop 界面通道 | L2 | e2e：40 字节 TVITEMW + 折叠行 rect 是邻居；H5U 工程树是 cid=2 |
| `ui.open_program` | AutoShop 界面通道 | L3 | e2e_programs：展开父 → 单击 → 核对 TVGN_CARET → 双击 |
| `ui.documents` | AutoShop 界面通道 | L2 | e2e：Ctrl+Tab 切文档 + 标题/编辑器双判 |
| `ui.compile` | AutoShop 界面通道 | L3 | e2e/e2e_programs：编译并解析诊断 |
| `ui.diagnostics` | AutoShop 界面通道 | L2 | e2e_check：输出窗自绘，靠 Frida hook DrawTextW |
| `ui.screenshot` | AutoShop 界面通道 | L2 | e2e：窗口抓图 |
| `ui.dialogs` | AutoShop 界面通道 | L2 | e2e_cli：枚举/关闭模态框 |
| `ui.doctor` | AutoShop 界面通道 | L2 | e2e：树/文档/编辑器/输出窗/Frida 自检 |
| `ui.stop` | AutoShop 界面通道 | L2 | e2e：关进程、释放 .hcp 锁 |
| `edit.symbols` | 写入（编辑） | L3 | e2e_symbols 9/9 |
| `edit.monitor` | 写入（编辑） | L3 | e2e_monitor 6/6 |
| `edit.new_project` | 写入（编辑） | L3 | e2e_create 6/6 |
| `edit.save` | 写入（编辑） | L3 | e2e：只重写脏部件并报 changed_files |
| `build.check` | 编译与保存 | L3 | e2e_check 11/11 |
| `dl.offline_file` | 下载侧 | L3 | 生成下载文件 → 下载选项 → 生成 → Shell 另存为 |
| `cmd.wm_command` | 命令与目录 | L2 | e2e：菜单是 CMFCMenuBar，命令走 WM_COMMAND + ID |
| `cmd.catalog` | 命令与目录 | L1 | docs/COMMANDS.md：4500 条命令/字符串目录 |
| `cli.verbs` | 命令行 | L1 | e2e_cli 17/17：每个 verb 子进程跑一遍 |

<!-- 由 tools/sync_capabilities.py 生成，勿手改 -->
<!-- gen:capabilities:END -->

## 判据怎么选

| 你改了什么 | 判据 |
| --- | --- |
| 程序文本 | `program_il(strict=True)` 等于写入内容；`compile()` 错误数 0 |
| 符号/监控表 | 重新 `symbols()` / `monitor_table()` 读到该行 |
| 工程结构 | `project_summary()` 的程序数/树规模变化 |
| 落盘 | `save()` 返回的 `changed_files` 里出现该部件 |
| 离线文件 | `hcp.read_project()` 的字段/记录数；`il_log` 的步数 |
| H5U 程序 | `illog` 拆出的 MAIN 步数 == `Compile/MAIN.compile` 里的指令数 |

## 坑与配方

- 配方：[`references/recipes.md`](references/recipes.md)
- 坑：[`references/pitfalls.md`](references/pitfalls.md)
- 开工清单：[`references/checklists.md`](references/checklists.md)

## 什么别试

见内核仓库 [`docs/UNSUPPORTED.md`](https://github.com/Winterwind2017/autoshopkit/blob/main/docs/UNSUPPORTED.md)：
在线监控真值、真正的 PLC 下载、写 H5U 梯形图、点梯形图画布、网格整块导出 —— 这些都不会"成功"，
只会给你一个假的 `True`。
