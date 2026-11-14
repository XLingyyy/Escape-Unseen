# Task 11A 交接

## 范围与数据

现有12张游戏地图（含保留的L01）均改为全场灯轨。主线数组沿用任务10B的11关；本次不进行11B求解器复核或11C布局制作。RailZ保持各关现值。

Director新增bEnableFullRail，默认true；LampStartSide为实例可编辑Name字段，允许Left/Right，默认Left。L00/L02/L03按指定Left，其余旧关采用同一默认，后续新关可按v3数据改Right。有限轨范围及原物理灯参考位分别保存在LimitedRailMinX/MaxX、ReferenceLampPos。当前RailMinX/MaxX按实际左右墙内面±60cm录入，开启后使用全轨，关闭后恢复保存的有限轨和参考灯位。

| 地图 | 全轨X cm | 原有限轨X cm | RailZ cm | 回退参考X cm |
|---|---:|---:|---:|---:|
| L00_FirstCut | 60–1440 | 295–390 | 1000 | 320 |
| L01_FirstStep | 60–1440 | 250–750 | 800 | 500 |
| L02_HiddenStair | 60–1440 | 350–1000 | 900 | 500 |
| L03_MatchCut | 60–1440 | 600–1400 | 1000 | 1300 |
| L04_DoubleDuty | 60–1440 | 100–1300 | 1100 | 700 |
| L05_SplitBudget | 60–1440 | 200–1200 | 1100 | 700 |
| L06_CrossedShadows | 60–1440 | 500–1150 | 1080 | 850 |
| L07_ReturnTicket | 60–1440 | 600–1350 | 1110 | 1300 |
| L08_FinalAssembly | 60–1440 | 1298–1380 | 1110 | 1300 |
| L09_NoRetake | 60–1440 | 285–380 | 1000 | 300 |
| L10_FlyRail | 60–1340 | 1020–1155 | 1000 | 1030 |
| L11_LastFerry | 60–2340 | 535–660 | 1050 | 620 |

## 行为

加载关卡和暂停菜单重开时按LampStartSide初始化；RETAKE、R重来、回搭景/重摆灯沿用当前灯位。已有钢管和端座预摆尺寸与全轨一致；没有新建固定场景生成器。运行时总开关切换只更新这些既有Actor的范围和灯位。

琥珀色范围线沿轨道每100cm增加刻度，物理屏幕尺寸6×1px、alpha0.6。Shift微调按鼠标自身位移的0.25倍计算，相机平移增量单独全额叠加；按下/松开Shift不重新对齐鼠标，端点夹紧后反向拖动立即响应。大图复用任务9的60px边缘平移和边界夹紧。

L00摆灯开场提示为 Drag the lamp along the rail.；离初始端严格超过100cm后消失，回到起端不会再次触发。松开鼠标后沿用锁灯提示。菜单重载重置这一教学状态。有限轨模式沿用原教程。

## 灯轨高度附近设施

按灯轨RailZ±30cm及全轨水平范围检查已有逻辑Occluder，移动平台取完整端点扫掠范围，黑旗取布面bounds，排除墙地顶、库存箱和装饰。仅L08_FinalAssembly命中ShadeBar：X1120–1290cm、Z1060–1080cm；RailZ1110cm，顶面间隔30cm，恰在纳入边界。其他11图未命中。此结果只作为后续设计输入，没有调整设施或碰撞规则。

## 实施与验证记录

主会话独占UE修改、编译、保存和提交；离线代理准备地图迁移/高度报告、HUD接线、输入逻辑及定向验证夹具，主会话检查并集成。三个共享蓝图BP_ShotDirector、BP_EscapePC、BP_EscapeHUD已编译。地图迁移报告在EU/Saved/codex_task11a/maps/。

定向PIE验证已完成，L00与L11报告均为complete、cleanup_errors为空：

- 两关加载时灯在左端60cm；全轨钢管及端座范围正确。临时改Right后分别到1440/2340cm。
- L00新提示已显示；偏移100cm仍保留，101cm后消失。
- 生产拖动函数实测鼠标世界位移40cm时，普通模式灯移动40cm、微调模式10cm；微调开关切换不跳位，右端夹紧后反向10cm立即移动。
- L11沿用原生鼠标位置及UpdateCameraInput：左缘平移到1118.776cm，右缘平移到1281.224cm并夹紧。右缘实测鼠标(1854,474)、视口1912×972，距右缘58px；微调时灯和相机同增162.448cm，相机位移未乘0.25。
- FailInspection、StartPlay/Retry、BackToBuild和MoveLightAgain公开入口调用后，立即及下一帧灯位均保留。
- 关闭bEnableFullRail后恢复原范围、钢管/端座及参考灯位：L00为X320cm，L11为X620cm；重开开关恢复全轨。
- L00通过现有HandleMenuAction(6)执行菜单重开，实际OpenLevel后世界时间重置，灯从X260cm回到60cm，教学状态重置。

验证边界：拖动和状态验证使用生产公开函数，临时停用PC Tick并直接传入Fine；Director、世界及移动平台继续正常Tick。实际Shift按键、鼠标按下/松开事件未自动验证，也未进行通关、审批、求解器或全关回归。L11首次右缘样本无平移，原因未确认；增加实际坐标读回后完整通过，未因此修改既有相机输入逻辑。

证据保留在EU/Saved/codex_task11a/verify/：task11a_L00_FirstCut_report.json、task11a_L11_LastFerry_report.json、task11a_menu_restart_report.json。原生截图EU/Saved/review/task11a_L00_fullrail.png与task11a_L11_fullrail.png均为1912×972，已查看；L11截图为沿用边缘平移后的视角，初始保存镜头未改。

最终已保存全部资产、停止PIE、删除临时桥接资产、恢复播放窗口设置并返回L00，无附加窗口。未打包、推送或提交参赛；11B/11C未启动。

参考接口：[Epic Get Mouse Position](https://dev.epicgames.com/documentation/en-us/unreal-engine/BlueprintAPI/Game/Player/GetMousePosition)、[Epic Canvas Draw Line](https://dev.epicgames.com/documentation/unreal-engine/BlueprintAPI/Canvas/DrawLine)。
