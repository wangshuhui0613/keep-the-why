# 更新记录

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。**[1.2.0] 之前为日期制明细，自 1.2.0 起每节对应一个 semver 版本。**

## [未发布]

### 变更

- **`prompts/一键构建.md` 新增投递自检与安全边界**（对标 obsidian-mind 的 delivery gate 做法）：部分 Agent 对超长注入内容只保留开头一部分且不报错，指令现要求 AI 正式执行前逐字复述两行指定原文，复述不出即判定截断、补发后再开始，并在文首说明「拆两段发」的退路；工作原则新增三条安全边界——写前先读、改前先问、日记与复盘只增不改、迁移是加一层不是洗一遍
- `AGENTS.md` 新增「安全边界」一节（写前先读 / 改前先问 / 日记复盘只增不改 / 迁移加一层 / 批量修改先只读验证），把散在维护规则与必须询问里的要求收成一组开头可见的硬规则
- `README.md`：快速开始三条路径标注预计耗时（10 / 2 / 5 分钟）；新增「哪个 AI 读哪个文件」对照表（编程 Agent 走 Skill 或 AGENTS.md，通用对话 AI 走一键构建指令，国产模型建议中文 prompt）；首屏新增「零插件依赖」声明（不装社区插件、不需要插件市场代理、离线可用——直击国内网络环境痛点）；目录补「路线图」入口，「模板更新了怎么办」补 Watch → Releases 通知一行；徽章行新增 skills.sh
- `Windows使用指南.md` 新增「多设备同步（可选，国内免费方案）」一节：Remotely Save + 坚果云 WebDAV 四步配置，含应用密码陷阱与忽略文件清单（`workspace.json` 等本机状态）
- `CONTRIBUTING.md` 补分流规则一句话：用法疑问走 Discussions Q&A，坏了/缺了走 Issue，安全问题走 SECURITY.md 不开公开 issue

### 变更（承接上一轮，模板收口）

- **模板放置统一收口 `03-复盘与规划/99-模板/`**：删除示例库 `02-周复盘/周复盘模板.md` 与 `03-月复盘/月复盘模板.md` 两个旧副本（与 `99-模板/` 新版仅差 frontmatter，而 frontmatter 正是 v1.1.0 已修复的「插入模板污染新日记」问题；两目录按仓库约定补 `.gitkeep` 保持骨架）；`prompts/一键构建.md` 目录树、`skills/personal-kb/assets/skeleton.txt`、`skills/personal-kb/references/build-brief.md` 映射表三处由「周 / 月复盘模板发去各自子目录」改为五个模板全部进 `99-模板/`——此前与同一份文件里「模板统一收口在 99-模板/」的规则自相矛盾，AI 建库用户插入菜单只有 3 个模板、周 / 月复盘模板不在菜单可达范围。统一后两种建库路径结构一致，插入菜单均 5 个
- `复盘与规划.md` 模板行补全为五个模板链接（均指 `99-模板/`）；`使用说明.md`「两种建库路径模板数差异」注记改为「结构一致」；`Windows使用指南.md` 去掉「clone 路径」限定
- `.gitignore` 补充 `.obsidian/appearance.json` 与 `.obsidian/graph.json`：两者与既有的 workspace.json 同属 Obsidian 本机界面状态，克隆后用 Obsidian 打开不再冒出未跟踪文件
- `demo.gif` 第 5 屏体检数字与实跑对齐（链接 108/108、无敏感信息 33/33）；演示页两版经 `tools/build_demo.py` 重建
- `tools/gif_shots.js` 头部补 Windows Git Bash 的 NODE_PATH 路径写法注意（反斜杠 + 单引号，MSYS 的 `/c/...` 写法 Node 识别不了）
- **结构版本号 `structure_version` 校准为 2026-10-17**：README 与 `prompts/一键构建.md` frontmatter 自 2026-10-15 建库起未随结构变更推进，而 `.obsidian` 开箱配置与模板收口都已改变实际结构；演示页（`docs/_shell.html` 及两版生成物）封面 Structure 日期同步

## [1.2.0] - 2026-10-17

自 v1.1.0 以来的变更（v1.1.0 已含内容见其 Release Notes，不在此重复）。

### 新增

- `commands/` 四个命名斜杠命令（`日报` / `周复盘` / `记一下` / `体检`）：装一次 Skill 后每天打几个字就能触发对应流程，不用复述长指令
- `prompts/可选升级-MCP与CLI.md`：官方 CLI 与 MCP server 两条升级路线，附「五条不变规矩」；不装也能用，立零依赖
- `03-复盘与规划/99-模板/` 新增周复盘、月复盘两个模板（Obsidian 插入模板菜单可用的模板达 5 个）
- `assets/banner.png`（1280×640）社交封面图；`assets/screenshots/` 截图目录与命名/脱敏规范
- `assets/screenshots/` 四张实拍截图就位（行动总览十字段 / 日报模板 / 图谱视图 / 插入模板弹层，Obsidian 1.14.4 实拍，内容为模板自带示例数据天然脱敏）；README 与 README.en 的「截图」节从规划态改为实际展示
- `.github/PULL_REQUEST_TEMPLATE.md`：按 CONTRIBUTING 的 PR 要求做成 checklist（改了什么 / 为什么 / 是否破坏性 / 体检输出 / 已脱敏）
- `CODE_OF_CONDUCT.md`（Contributor Covenant 2.1）、`SECURITY.md`（无服务端、无数据收集；安全问题指脚本误报漏报与示例数据泄露）、`.github/dependabot.yml`（只配 github-actions，weekly）
- `llms.txt`：规定外部 AI 读本仓库的顺序（README → 使用说明 → AGENTS.md → SKILL.md → rules.md）
- `tests/test_vault_health_check.py`：体检脚本单测（stdlib unittest，10 个用例：两种链接语法断链、行动字段与状态、敏感信息模式、退出码语义、模板源资件按目标目录解析）；CI 在体检前先跑单测

### 变更

- **版本号体系统一**：`SKILL.md` metadata.version 由 "1.2" 改为 "1.2.0"，与 release tag、`.claude-plugin/plugin.json` 对齐；`CONTRIBUTING.md` 补充版本约定（semver 同时用于 release tag、plugin.json、SKILL.md，发版时三者必须一致）
- `tools/vault_health_check.py`：`skills/personal-kb/assets/templates/` 下的模板源资件改按目标目录（`03-复盘与规划/99-模板/`）校验相对链接，不再按源仓库位置误判断链
- **链接规则三处口径统一**：`AGENTS.md`、`rules.md`、`一键构建.md` 与 SKILL.md 实际行为对齐为「双链一律用完整相对路径的标准 Markdown 链接，带 `.md` 后缀」——此前文档要求不带后缀、实际文件与体检脚本却要求带，按旧文档建库反而报断链
- `SKILL.md` description 触发词扩充（体检 / 查重 / 整理旧库），新增「命名斜杠命令」表
- README 方式二补 npx 交互菜单预告与非交互参数（`--agent '*' -y`）；「三个 0x- 板块」黑话改全称；新增「模板更新了怎么办」与「截图」两节
- `README.en.md` 同步：Screenshots / Template Updates / Multiple Computers 三节，四口令表，npx 交互提示，链接中文文档统一标 (in Chinese)
- `rules.md` 新增「时效三分」一节（长效 / 时效 / 指针），方法来源致谢 OKM
- `tools/vault_health_check.py` 新增 INFO 行（入口被引用 9/11、行动被提及 2/3）：空模板里「结构存在但没被用」只警告不计 FAIL
- `ROADMAP.md`：「英文 README」「从 issue 沉淀 FAQ」从未完成移入已完成，刷新过期条目
- README / README.en 目录结构图补齐 9 个根级条目，并用分组注释标明「AI 与展示资产」
- 文档口径统一：注明两种建库路径的模板数差异（clone 路径插入菜单 5 个；AI 建库路径 3 个，周 / 月复盘模板在各自子目录）；`Windows使用指南.md` 修正「3 个」说法；纯净库删除命令两版统一（均删 `commands/` 与 `.claude-plugin/`）

### 修复

- **Skill 路径建库模板断链**：`skills/personal-kb/assets/templates/` 五个模板的相对链接深度由 `../../../../` 改为 `../../`——这些模板按 build-brief 会进入用户库 `03-复盘与规划/99-模板/`（周 / 月复盘模板在 `02-周复盘/`、`03-月复盘/`，同深度），此前按源仓库位置写的深度会让 Skill 路径建库的用户第一份日报 / 周复盘 / 决策 / 经验卡片里的链接全断、体检 FAIL
- `EXAMPLES.md` 代码块内被误当成真链接的示例路径改为纯文本；`使用说明.md` 修正脚本错路径、补日期占位符提示、模板清单与事实一致
- `demo.gif` 第 5 屏数字与实跑对齐（111/111、32/32、INFO 行），结尾屏补 Windows 用户指引
- `README.en.md` FAQ 补「库内容中文能否用英文」条

## [2026-10-16] 英文版 / 示例 / 插件市场 / 真问题修复

### 新增

- `README.en.md` 英文版，中文 README 顶部加语言切换
- `EXAMPLES.md`：五篇填好的脱敏示例（日报 / 行动 / 决策 / 经验卡片 / 周复盘）+ 反例对照表
- `Windows使用指南.md`：Windows 特有的是下载方式、Python 安装两个坑（PATH 与商店版「替身」）、纯净库删除命令
- `.claude-plugin/marketplace.json`：上架 Claude Code 插件市场，`claude plugin marketplace add wangshuhui0613/personal-kb-template` 后可按名安装
- `SKILL.md`（v1.2）新增 `/adopt` 老库迁移流程（迁移是加一层，不是洗一遍）与「按角色调整侧重」表；搭建时多问一个角色问题
- README 新增：目录导航、常见问题（FAQ）、「什么情况别用」反向声明、「对 AI 说什么→发生什么」命令速查表
- README 隐私承诺前置到前 20 行
- 仓库设为 GitHub Template repository，topics 扩充到 18 个，homepage 指向在线演示页
- `commands/` 四个命名斜杠命令（`日报` / `周复盘` / `记一下` / `体检`）：装一次 Skill 后每天打几个字就能触发对应流程，不用复述长指令
- `prompts/可选升级-MCP与CLI.md`：官方 CLI 与 MCP server 两条升级路线，附「五条不变规矩」；不装也能用，立零依赖
- `03-复盘与规划/99-模板/` 新增周复盘、月复盘两个模板（Obsidian 插入菜单可用的模板达 5 个）
- `assets/banner.png`（1280×640）社交封面图；`assets/screenshots/` 截图目录与命名/脱敏规范
- `assets/screenshots/` 四张实拍截图就位（行动总览十字段 / 日报模板 / 图谱视图 / 插入模板弹层，Obsidian 1.14.4 实拍，内容为模板自带示例数据天然脱敏）；README 与 README.en 的「截图」节从规划态改为实际展示

### 变更

- 使用说明「写四段」改为模板实际五段并列段名，补上「待确认」段的跨天流转规则
- **链接规则三处口径统一**：`AGENTS.md`、`rules.md`、`一键构建.md` 与 SKILL.md 实际行为对齐为「双链一律用完整相对路径的标准 Markdown 链接，带 `.md` 后缀」——此前文档要求不带后缀、实际文件与体检脚本却要求带，按旧文档建库反而报断链
- `SKILL.md` description 触发词扩充（体检 / 查重 / 整理旧库），新增「命名斜杠命令」表
- README 方式二补 npx 交互菜单预告与非交互参数（`--agent '*' -y`）；「三个 0x- 板块」黑话改全称；新增「模板更新了怎么办」与「截图」两节
- `README.en.md` 同步：Screenshots / Template Updates / Multiple Computers 三节，四口令表，npx 交互提示，链接中文文档统一标 (in Chinese)
- `rules.md` 新增「时效三分」一节（长效 / 时效 / 指针），方法来源致谢 OKM
- `tools/vault_health_check.py` 新增 INFO 行（入口被引用 9/11、行动被提及 2/3）：空模板里「结构存在但没被用」只警告不计 FAIL

### 修复

- 8 个模板（`99-模板/` 3 个 + `skills/personal-kb/assets/templates/` 5 个）全部移除 frontmatter——修复 Obsidian 插入模板时把「title: 日报模板 / tags: [模板, 日报]」原样复制进每一篇新日记的污染
- `tools/health-check.cmd`：先检测 Python，缺失时明确提示「体检是可选步骤，不影响使用」并以退出码 2 退出，与真问题（1）区分
- `tools/vault_health_check.py` 新增 CHECK 摘要行（入口文件 / 链接 / 行动字段 / 敏感信息），实跑输出与 demo.gif 第 5 屏一致；GIF 数字随体检结果重建，不手改
- 纯净库删除命令补 Windows PowerShell 版，并说明删除后链接失效属正常
- CONTRIBUTING 补「提 PR 注意行尾符」与「GIF 数字同步规则」两条
- `EXAMPLES.md` 代码块内被误当成真链接的示例路径改为纯文本；`使用说明.md` 修正脚本错路径、补日期占位符提示、模板清单与事实一致
- `demo.gif` 第 5 屏数字与实跑对齐（111/111、32/32、INFO 行），结尾屏补 Windows 用户指引
- `README.en.md` FAQ 补「库内容中文能否用英文」条

## [2026-10-15] 首个公开版本 + 生态对齐

### 新增

- 三大板块结构（个人 / 工作经历 / 复盘与规划）+ A/W/J/H/E 五类行动编号 + 完成四层 + 三类证据口径
- `skills/personal-kb/`：符合 Agent Skills 规范的 Skill（含 10 个入口文件内容合同与完整 AI 写入规则）
- `prompts/一键构建.md`：不装 Skill 也能用的一段式构建指令
- `tools/vault_health_check.py`：断链 / 字段 / 状态 / 敏感信息体检（CI 每次推送自动跑）
- `.obsidian/` 开箱配置：模板文件夹、日记格式与模板、附件路径
- `docs/` 在线演示页（离线自包含版 + CDN 增强版）
- `npx skills add wangshuhui0613/personal-kb-template` 标准安装命令，与 Agent Skills 生态（Claude Code / Codex / Cursor 等 75+ Agent）对齐
- README 新增「第一天，只做三件事」最小闭环
- README 新增「谁适合用」角色化上手路径（开发者 / 产品经理 / 学生）
- 方法论命名「**行动账本（Action Ledger）**」：一个状态入口、五类科目、四层入账进度、三类凭证
- `tools/health-check.cmd`：Windows 用户双击即可体检
- `docs/demo.gif`：新用户第一天流程演示
- 方法来源与致谢章节（Karpathy 的 LLM wiki 模式、kepano/obsidian-skills、agentskills.io 规范、vercel-labs/skills）
- `CHANGELOG.md` / `ROADMAP.md`

### 变更

- `skill/` 目录改名 `skills/`，与 kepano/obsidian-skills 的组织方式对齐
- `SKILL.md` 版本 1.0 → 1.1：修正两处过时表述（链接规则改为「标准 Markdown 相对路径带 .md」，体检命令改为 Windows 可用的 `python`）
- README 体检章节：「双链」表述改为「链接」
- `AGENTS.md`、`skills/personal-kb/references/rules.md`、`tools/build_demo.py` 里的 `python3` 统一改为 Windows 可用的 `python`

### 修复

- 新用户实测问题：`01-每日记录/` 目录丢失、GitHub 网页双链死链（全量转标准 Markdown 链接）、`python3` 命令在 Windows 不可用、断链检查在双链清零后空转
- 演示页布局四伤：指令框截断、控制条不随缩放且遮挡结尾 URL、封面右侧空白、结尾右栏空虚
