# 开工清单

## A. 动手前（2 分钟，不花 AutoShop 的启动时间）

- [ ] `autoshopkit status` —— 有没有已连上的实例？
- [ ] `autoshopkit doctor`（连上时）—— `dialogs_open` 必须为空；`il_editor` 决定能不能写程序。
- [ ] 工程系列确认：`autoshopkit hcp --project DIR` 看 `GCMModal`（H3U / H5U / AM600）。
- [ ] 目标能力是否在 `docs/UNSUPPORTED.md` 里？在就别开始。
- [ ] 数据从哪来：`sandbox/` 里复制一份副本，**不碰原件**。

## B. 只读任务（读工程、读程序、体检）

- [ ] 优先走离线：`hcp` / `illog` / `check --offline`
- [ ] 只有必须"界面读数"时才 `start`（例如输出窗诊断、树规模）
- [ ] 读完 `stop`，释放 `.hcp` 锁

## C. 写入任务（H3U 程序 / 符号表 / 监控表）

- [ ] 已确认 `doctor.il_editor == true`（H3U）
- [ ] 写入前把原程序 `program_il(strict=True)` 存一份到 `sandbox/backup/`
- [ ] 写入后**立刻**回读比对（不要等保存后）
- [ ] `compile()` 0 错误
- [ ] `save()` 的 `changed_files` 里有目标部件
- [ ] 关掉重开，再读一遍（缓存会骗人）

## D. 交付前

- [ ] 判据是**读数**：`program_il` / `compile().summary` / `project_check().counts` / `hcp.fields`
- [ ] 没有"我调用了所以成功了"这种结论
- [ ] 没打通的写进 `docs/UNSUPPORTED.md`，不要偷偷标成能用
- [ ] 客户数据没有进仓库（`python tools/selfcheck.py` 在核仓库里跑一次）
- [ ] 技能快照与内核一致：`python tools/sync_capabilities.py --check`

## E. 出问题时按这个顺序查

1. `.hcp` 被锁？→ `autoshopkit stop`
2. 有模态框？→ `autoshopkit dialogs`
3. 树选错了？→ 确认 `app.tree()` 拿到的是 cid=2 的工程树（H5U）
4. 程序没打开？→ 用 `open_program` 的返回值判断，不要看状态栏
5. 诊断读不到？→ `doctor` 里 `output_pane` 是否 true（Frida hook 在不在）
6. 写入没生效？→ 是不是用了 `SCI_SETTEXT`；改成真全选 + 粘贴
