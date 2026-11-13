# Escape Unseen 提交材料清单

核对日期：2026-11-13。目标：Unreal Engine Windows 参赛版。此表用于人工准备与提交，不触发打包、上传或自动报名。

依据：本地《Official Rules》PDF（14 页，2026-11-03 保存）及 2026-11-13 的 [官方赛事页](https://itch.io/jam/2026-epic-ai-megajam)。PDF 的规则条款与网站公布的材料要求分别标注；未打开已登录的正式提交表单，不能保证下列栏目名称与表单逐字一致。

## 时间与责任

- 截止：洛杉矶时间 **2026-11-15 17:59 PST**，即 **2026-11-16 01:59 UTC**。以官方截止为准，预留上传时间。来源：PDF §4 第 3 页。
- 由参赛者本人完成提交和确认；AI 可以准备内容，不能代交。来源：PDF §17 第 12 页。
- 所有参赛内容、游戏文字/音频、视频和报名信息使用英文。来源：PDF §7(i) 第 4 页。

## 作品与成员资料

| 字段或材料 | 应准备内容 | 状态与来源 |
|---|---|---|
| Team name | 队伍英文名称 | 待参赛者填写；赛事页 UE 提交段 |
| Game name | Escape Unseen | 已有；赛事页 UE 提交段 |
| Team owner | 明确一名队伍负责人 | 待参赛者填写；PDF §1 第 1 页 |
| Every entrant's full name | 每名队员的真实全名，团队 1–5 人 | 待参赛者填写；PDF §1 |
| Every entrant's email | 每名队员绑定 Epic Games 账号的有效邮箱 | 私下填入正式表单，不放公开文案；PDF §1、赛事页 |
| Epic account / entrant eligibility | 有效 Epic 账号、年龄、居住地等资格；若申报学生类别，所有队员均须符合在读要求 | 由参赛者确认；PDF §5 第 3–4 页 |
| Track / category | Unreal Engine；学生、Solo Driver 等仅按实际身份申报 | 不同时提交 UE 与 UEFN；赛事页 |
| Game page | 自己 itch.io 账号下可供评委访问的作品页 | 本轮提供英文文案，尚未发布；PDF §7(b) |

## 作品文件与展示素材

| 材料 | 要求 | 谁提供 / 当前状态 |
|---|---|---|
| 可玩安装包 | 已打包的 Windows 版本；本项目目标 Win64。不能仅交 UE 工程，不能要求评委安装额外开发工具 | Claude 打包、参赛者上传；本轮未生成。PDF §1、§7(e)(f)，赛事页 |
| ZIP 文件名 | `TeamName_EscapeUnseen.zip`，用实际队伍名替换 TeamName | 打包后命名；赛事页 |
| 文件大小与上传方式 | 网站普通上传目标小于 1 GB；更大包使用平台支持的 butler 或指定上传工具 | 由参赛者根据真实包大小选用；赛事页 |
| Gameplay video link | 30–60 秒真实游戏录像，至少 1920×1080，英文；展示主题如何进入玩法 | Claude/参赛者录制并提供可访问链接；PDF §1(e)、§7(c)(i) |
| Dev log link | Glass Box 类别必须提供；其他情况可选 | 本地 `DEVLOG.md` 已整理，尚无公开链接；赛事页 |
| 封面与截图 | 用于作品页展示的实际游戏截图/封面 | 建议材料，未将其写成 PDF 强制字段；需由实际游戏版本制作 |
| 操作与已知问题 | 说明 W/↑ 跳跃、E 接镜及最终 Enter/Q；列出实际已知问题 | 文案已有，提交者按最终版本核定 |

## 来源和工具披露

| 字段或材料 | 应填写内容 | 证据 / 限制 |
|---|---|---|
| Sourced assets | 列出外部来源资产、作者、链接和许可；AI 自行生成内容另按实际工具使用披露 | PDF §1(d)、§15(c)。不得将生成候选与实际使用混淆 |
| Pre-jam material | 如实披露赛前设计、prompts、scripts、工具和资产；原始 GDD 时间不能写成赛中新创 | PDF §7(h)、赛事 FAQ；旧 GDD 沿用许可尚未明确 |
| Tools used | Claude Code + Unreal MCP、Codex、GPT、Tripo、fal 及实际音频模型；后处理工具按实际使用列明 | `PROVENANCE.csv`、`DEVLOG.md`；赛事页说明该栏与部分合作伙伴奖相关 |
| OpenAI Awards（可选） | 若申报，说明实际使用的 OpenAI 产品/模型及用途；可说明 Codex 的源资产处理与文档工作 | 以真实使用为准，不凭当前助手名称猜测模型版本；赛事页 |
| NVIDIA RTX Award（可选） | 仅勾选实际用到的合资格 NVIDIA 功能，并描述用途 | 当前未取得相应使用证据，不预填；赛事页 |
| 其他合作伙伴奖（可选） | 依实际使用工具与身份选择；例如未使用 Rodin 就不申报其使用奖励 | 不以感谢赞助商代替工具使用证据；赛事页 |
| 来源记录附件/链接 | 完整 prompt、UTC 生成时间、模型名、积分/费用，以及实际入包资产清单 | `PROVENANCE.csv` 已建立。估算费用明确标注，衍生文件不重复计费 |

## 提交时的有限收口

- 由整合负责人提供最终包、实际运行结果、视频和真实已知问题；此清单不新增每日测试或全量回归。
- 确认评委能打开下载、视频和开发日志链接，且公开资料不含 API Key、私人邮箱或登录凭据。
- 由参赛者核对最终规则与表单、完成上传/提交并保留提交结果；本文件不代表已经报名或提交。

## 官方来源

- [Official Rules PDF 分享页](https://epicgames.box.com/s/a7xcgl07fqoieeb99sjtd3juhj4agc4z)
- 本地规则原件：`2026-epic-ai-megajam-prep/sources/official-rules-2026-11-03.pdf`。
- [赛事页及 FAQ](https://itch.io/jam/2026-epic-ai-megajam)，已核对 UE 提交材料、可选奖项字段与截止时间。

网站现已列出 UE 5.9 Preview 的实验性 Web 提交选项；本项目保持既定 UE 5.8.4 / Windows 路线，无需因该选项升级引擎。
