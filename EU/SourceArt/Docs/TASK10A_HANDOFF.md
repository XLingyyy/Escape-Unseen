# Task 10A 交接

依据 GPT_LEVEL_DESIGN_V2.md、GPT_LEVEL_AUDIT_ACTOR.md 和 CODEX_TASKS.md 的 Claude 审核决定。单位 B=100 cm。任务 10B 等用户试玩后另行授权。

## 共享实现（随 L00 提交）

- BP_LightFlag：独立预摆 Actor，水平黑布、3 cm 钢框、4 cm C 架及三脚底座。全组件无碰撞；ShadowService 单独读取布面边界，支架不参与逻辑或渲染遮光。角色胶囊重叠时以 0.1 s 从 1 淡到 0.35，离开恢复；逻辑阴影不变。
- L00 新增首次推箱和首次巡视教学；真实推箱后消耗推箱提示，首次五秒预警优先显示藏身教学，结束恢复上下文；重来保留已学状态。各功能总开关继续控制对应提示。
- Director 新增 bUseLevelPatrolMinimum / LevelPatrolMinimum，默认 false / 10 s；PatrolStart 和巡视离窗后的调度都读取同一选择函数。10A 各关均未启用覆盖。
- LevelOrder 移除 L01，保留地图资产；场次号继续来自数组位置。只收录完成的地图。大地图镜头启用阈值按设计改为 >14B，10A 房间查询边界对齐实际内墙 X=0..1500；FOV 沿用现有值。

## 已完成关卡

| 地图 | 改动 | 实际验证 |
|---|---|---|
| L00_FirstCut | 平台/横梁、出生 X75、标记、灯轨；EntryScrim X72..152 / Z165..169；X190、710 粉笔线；看守窗口移至空墙 | A/B 各审批一次通过；出生角色隐藏；原生 phase 0 图已检查 |
| L02_HiddenStair | 灯轨；入口旗 X170..250 / Z160..164；补齐原本未绑定的 DebugProbe；保留空 A 自动进入 B 流程 | A/B 各审批一次通过；出生角色隐藏；门、最高横梁、灯均在画面内 |
| L03_MatchCut | 灯轨；出生 X200→385，同步出生标记 | A/B 各审批一次通过；出生角色隐藏；门、最高横梁、灯均在画面内；灯后提示条按原遮挡规则淡化 |
| L04_DoubleDuty | 灯轨及两条设计提示；固定设施与参考箱不变 | A/B 各审批一次通过；出生角色隐藏；门、最高横梁、灯均在画面内；灯后提示条按原遮挡规则淡化 |
| L05_SplitBudget | 灯轨及两条设计提示；固定设施与参考箱不变 | A/B 各审批一次通过；出生角色隐藏；门、最高横梁、灯均在画面内；灯后提示条按原遮挡规则淡化 |
| L06_CrossedShadows | 灯轨及两条设计提示；固定设施与参考箱不变 | A/B 各审批一次通过；出生角色隐藏；门、最高横梁、灯均在画面内；灯后提示条按原遮挡规则淡化 |
| L07_ReturnTicket | 灯轨；出生 X1300→1120；MarkDeck 底缘 460→480、顶面500；采用新 A#02–04 参考位 | A/B 各审批一次通过；出生角色隐藏；门、最高设施、灯均在镜头内；phase 0 门的左上部分仍被场记板覆盖 |
| L08_FinalAssembly | 灯轨；出生 X1300→1120，同步出生标记 | A/B 各审批一次通过；出生角色隐藏；门、最高设施、灯均在镜头内；phase 0 出口门仍被左上场记板覆盖 |
| L09_NoRetake | 由已完成 L00 复制，改为 No Retake 布局；出生 X120、EntryFlag X87..167 / Z165..169；教程关闭、移除粉笔线；加入主线 | A/B 各审批一次通过；出生角色隐藏；门、最高横梁、灯均在画面内 |

L00 额外 PIE：实际胶囊重叠后 0.1128 s 达到 35%（含帧量化），离开后 0.1000 s 恢复；各组件无碰撞，逻辑布面边界及出生点遮光不变。靠近显示推箱提示，真实推动箱子后提示消失。自然五秒巡视预警、检查开始后的上下文恢复，以及重来后不重复教学均通过。临时验证参数已恢复。

L02 原地图没有 DebugProbe，首次验证在初始化时停止，未执行审批；补齐预摆探针及 Director 引用后通过。保留产品原有的空 A 自动获批流程；验证器在锁灯后调用现有 EnterBuild(0)，再用探针提交一次空 A，未直接写 Approved 或 Phase。

截图位置：`EU/Saved/review/task10_<完整地图名>.png`，均为引擎原生 1920×1080。报告在 `EU/Saved/codex_task10/verify/`，L00 新功能报告在 `tutorial/verify_tutorial_result.json`。截图和临时验证脚本位于 Saved，不进入提交。

## 用户试玩重点

- L07 低台右端两级踏步的折返与头顶净空。
- L00、L02、L06 剪辑点在光里：检查期间站在亮处按 E，应判 RETAKE。
- L09 剪后跳到 B 箱左侧，等看守完整缩回再推箱、后撤起跳和出门；设计给出的联合行动预算 ≤6.2 s 尚未实跑。
- 后续 10B：L10 上下升降台时的净空、B 箱右侧起推到出门 ≤8.5 s 的时限；L11 西码头候船和上船、东岸在最短巡视间隔下的时间。

本任务不执行角色完整跳跃通关、整关推箱路线或巡视时机试玩；参考审批通过不代表以上流程已跑通。

## 实施记录

Codex 主会话独占 UE 写入、编译、验证和 Git 提交。离线代理分别整理地图数据与变更脚本、黑旗蓝图、教学蓝图及定向验证脚本，最终集成和验收由主会话执行。

任务开始时一次 Python 插件访问异常导致编辑器退出，当时尚未修改关卡；已重启恢复。后续使用独立模块和延迟回调执行原生操作，未复现。异常根因未被确定。

## 最终状态

主线数组为 `L00 → L02 → L03 → L04 → L05 → L06 → L07 → L08 → L09`，场次 00–08。L01 资产保留；L10/L11 未建、未入数组。L09 暂为末关，沿用现有 IsFinal 结尾逻辑；10B 完成时再把末关扩展到 L11。本次未实际触发结尾或跨关完整通关。

九关参考 A/B 均已审批通过，出生角色的头胸遮光检查均通过；九张 phase 0 原生截图已检查。L07/L08 出口门的场记板遮挡是沿用的界面限制，不能把“位于镜头范围内”视为“无遮挡可见”。其余关的门、最高设施和参考灯均在截图范围内。

全部保存，PIE 已停止，临时桥接 Actor/资产已删除，播放窗口设置已恢复，编辑器回到 L00。开始时崩溃产生的旧报告窗口和 Message Log 已关闭；当前 UE 仅保留主编辑器窗口。L07 提交后因临时桥接操作产生的再次保存已恢复到该关已验证的提交版本。

本批未打包、未推送、未参赛提交；10B 未开始，等待用户试玩。离线代理未持有 UE 写锁或执行 Git 提交。

## 提交记录

- 64a0adf Task 10: L00_FirstCut rebuild tutorial and light flags
- 4ee9899 Task 10: L02_HiddenStair update v2 layout
- dfb8025 Task 10: L03_MatchCut update v2 layout
- b428471 Task 10: L04_DoubleDuty update v2 layout
- 007af3c Task 10: L05_SplitBudget update v2 layout
- 84d5c6d Task 10: L06_CrossedShadows update v2 layout
- 416c375 Task 10: L08_FinalAssembly update v2 layout
- 3b115cb Task 10: L07_ReturnTicket update v2 layout
- L09 与本交接收口：见本文件所在的 `Task 10: L09_NoRetake update v2 layout` 提交。

材质实现参考 Epic 官方文档：[材质实例与运行时参数](https://dev.epicgames.com/documentation/en-us/unreal-engine/instanced-materials-in-unreal-engine)、[透明材质与 Opacity](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-transparency-in-unreal-engine-materials?lang=en-US)。工程继续使用现有材质体系及蓝图，无新增 C++ 或外部依赖。
