# 参与贡献

欢迎 issue 和 PR。这个模板的价值来自真实使用，所以**最有价值的贡献是"你用的时候哪里卡住了"**。

## 提 issue 之前

先确认你用的是最新版本，然后跑一遍体检：

```bash
python tools/vault_health_check.py --root .
```

如果体检报错，把输出一起贴到 issue 里。

## 几种 issue

| 类型 | 说明 |
|---|---|
| 上手卡住 | 哪一步看不懂、不知道该写什么 —— **这类 issue 最有用**，通常说明模板需要改，而不是你的问题 |
| 规则不合理 | 哪条纪律在实际使用中不成立，欢迎直接反驳，说清你的场景 |
| 缺东西 | 你需要的目录、模板或检查项 |
| Bug | 体检脚本误报或漏报 |

**去哪里提**：「怎么用」的疑问请到 [Discussions](https://github.com/wangshuhui0613/keep-the-why/discussions)（Q&A 分类，别人也能搜到答案）；「坏了 / 缺东西」提 Issue；安全问题见 [SECURITY.md](SECURITY.md)，不要开公开 issue。

## 提 PR

1. Fork 后新建分支：`git checkout -b your-topic`
2. 改动后跑一遍体检，确保 `PASS`
3. **不要提交个人信息**：任何真实姓名、公司名、项目名、令牌都不要进 diff
4. PR 里说清：改了什么、为什么要改、对已有用户有没有破坏性

## 几条硬规矩

- **示例必须脱敏。** 所有示例内容都要用虚构的「产品 A」，并标注「脱敏示例，不代表真实项目」。
- **不引入插件依赖。** 这个模板的一个卖点就是零插件可用，靠插件实现的功能请先开 issue 讨论。
- **统计数字不要写死。** 任何"共 X 篇"这类数字，要么不写，要么让脚本生成。写死的数字一定会腐化。
- **本机状态不进版本库。** `.obsidian/workspace.json` 等文件不要提交。
- **结构变更必须写进 CHANGELOG 的「变更」节。** clone 型模板的用户靠 CHANGELOG 决定要不要合并更新（见 README「模板更新了怎么办」）；新增或删除目录、模板、命令、检查项，都属于结构变更。

## 提 PR 时注意行尾符

Windows 的 Git 默认会把 LF 转成 CRLF，提交后整个文件都会显示为"重写"，review 时没法看真实改动。本仓库已通过 `.gitattributes` 统一为 LF，你本地再配置一次即可：

```bash
git config --global core.autocrlf false
```

## 目录编号约定

`01-个人` 和 `03-复盘与规划` 用连字符（`00-行动与跟进`），`02-工作经历` 用下划线（`00_总览`）。

两套都是既有约定，**不要单独"修正"其一** —— 一侧改名会造成全库双链不一致，要改必须两侧同步改。

## 版本约定

版本号用 [semver](https://semver.org/lang/zh-CN/)，三处必须一致：

| 位置 | 字段 |
|---|---|
| GitHub Release | tag（如 `v1.2.0`） |
| `.claude-plugin/plugin.json` | `version` |
| `skills/personal-kb/SKILL.md` | `metadata.version` |

发版时三者必须一致，并在 `CHANGELOG.md` 新增对应版本小节（自 1.2.0 起每节对应一个 semver 版本；1.2.0 之前为日期制明细）。

## 改动演示页

`docs/index.html` 是**生成产物**，不要直接编辑。

源头在抖音视频项目：`抖音知识库视频/演示页-母版.html`（录屏母版，自带粒子背景、
封面粒子文字与录屏提词器），由 `抖音知识库视频/生成库版演示页.py` 生成库版——
去掉全部特效与提词、深色主题、系统字体栈、无外部依赖，只保留翻页阅读、
文字入场动画与「复制完整指令」按钮。改母版后重跑该脚本即可。

> `docs/index-cdn.html`、`docs/_shell.html`、`tools/build_demo.py` 是更早的
> 「幻灯片式产品演示」生产线产物，已被上面的视频叙事版取代，留档待删。

GIF 的第 5 屏（体检画面）里的数字是**真实跑一遍体检的结果**。新增或删除任何 `.md` 文件后，重跑 `python tools/vault_health_check.py --root .`，把新数字同步进 `docs/_gif-scenes.html` 第 5 屏，再用 `tools/gif_shots.js` + `tools/build_gif.py` 重建 GIF。**不要手改 GIF 里的数字**——手改的一定会腐化。
