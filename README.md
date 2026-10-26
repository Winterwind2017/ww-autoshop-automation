# ww-autoshop-automation

汇川 **AutoShop V4.11** 自动化技能：给 agent 的"怎么用 + 怎么验证 + 什么别试"。

> **独立技能仓库**，不随内核分发。执行内核是
> [autoshopkit](https://github.com/Winterwind2017/autoshopkit)（Python 库 + CLI）。

## 装

```bash
git clone git@github.com:Winterwind2017/ww-autoshop-automation.git
python tools/install_skill.py        # 在 ~/.agents/skills/ 下建链接
python tools/check_skill.py --check  # 文档与能力快照一致
```

内核（真正干活的那个）：

```bash
pip install -e <autoshopkit 仓库>
autoshopkit doctor
```

## 里面有什么

| 文件 | 作用 |
| --- | --- |
| `SKILL.md` | 技能正文：铁律、两条通道、判据怎么选、坑 |
| `capabilities.json` | 能力快照（出处：内核 commit + AutoShop 版本），离线可校验 |
| `capabilities.md` | 同一份清单的可读版 |
| `references/recipes.md` | 实测调用序列（读工程 / 读 H5U IL / 写程序 / 编译 / 下载文件） |
| `references/pitfalls.md` | 踩过的坑（CMFCMenuBar、TVITEMW、自绘输出窗、cid=2 的树、假成功） |
| `references/checklists.md` | 开工/收尾清单 |
| `tools/` | 快照同步、文档校验、装技能、装 pre-push 钩子 |
| `tests/test_skill.py` | 技能自检（5 条） |

## 更新流程

```bash
python tools/sync_capabilities.py     # 从本机内核刷新快照 + 重渲染 SKILL.md 里的表
python tools/check_skill.py --check
python -m pytest tests -q
```

## 相关技能

同族：`ww-solidworks-automation`、`ww-nx-automation`、`ww-autocad-automation`、
`ww-gxworks-automation`（PLC 那边的兄弟，三菱 GX Works3）。

MIT © Winterwind2017
