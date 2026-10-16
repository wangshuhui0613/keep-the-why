# 更新记录

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。日期即「结构版本」。

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
