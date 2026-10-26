# 能力清单（快照）

由 `tools/sync_capabilities.py` 从内核生成；出处 `autoshopkit@93aa245`。

## 已打通（41）

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

## 未打通（5）

- `dl.to_plc` — 真正下载要连机与授权；只到『生成离线下载文件』
- `monitor.live` — 在线监控读数需要真实 PLC
- `h5u.ladder_write` — H5U 文档没有指令表编辑器（Scintilla 数为 0），写入通道只对 H3U 成立
- `h5u.ladder_click` — 梯形图是自绘画布，UIA 无子元素，只能盲点
- `monitor.grid_export` — 网格是 VSFlexGrid8N，没有剪贴板导出，只能逐格读
