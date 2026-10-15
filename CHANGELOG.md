# 更新记录

格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。日期即「结构版本」。

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
