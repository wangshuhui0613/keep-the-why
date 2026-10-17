# Windows 使用指南

> 这篇只讲 Windows 上和别的系统不一样的地方。通用用法先读 [使用说明](使用说明.md)。

## 一、下载

**方式 A：Download ZIP（推荐给不想装 Git 的人）**

GitHub 页面 → 绿色 `Code` 按钮 → `Download ZIP` → 解压到任意目录（比如 `D:\我的知识库`）。

**方式 B：git clone（想多设备同步的人）**

先装 [Git for Windows](https://git-scm.com/download/win)，然后：

```powershell
git clone https://github.com/wangshuhui0613/personal-kb-template.git 我的知识库
```

> 路径里有中文没问题，Obsidian 和 Git 都正常处理。

## 二、打开

Obsidian →「打开文件夹作为库」→ 选中解压出来的目录。模板、日记、附件路径**已经配好**，不用再设。

## 三、日常操作

| 你想做什么 | Windows 上怎么做 |
|---|---|
| 建今天的日记 | 点左侧日历图标（不用敲命令） |
| 插入模板 | `Ctrl + P` →「插入模板」→ 选日报 / 周复盘 / 月复盘 / 决策 / 经验卡片模板（共 5 个） |
| 跑体检 | **双击 `tools\health-check.cmd`**，或命令行里 `python tools\vault_health_check.py --root .` |
| 只要纯净笔记库 | PowerShell 里跑下面的删除命令（见第五节） |

## 四、体检和 Python（最常见的困惑）

体检是**可选步骤**——不装 Python，知识库照常使用、照常维护，只是不能跑体检。

`tools\health-check.cmd` 的行为：

| 情况 | 表现 | 含义 |
|---|---|---|
| 没装 Python | 提示 `[SKIP]`，退出码 2 | 体检跳过，**不影响使用** |
| 装了，体检通过 | `[PASS]`，退出码 0 | 结构完好 |
| 装了，发现问题 | `[FAIL]` + 问题列表，退出码 1 | 按列表逐条修 |

装 Python 时注意两个坑：

1. **安装界面第一屏勾选「Add python.exe to PATH」**，否则命令行里敲 `python` 会提示找不到命令。
2. **微软商店版 Python 是个“替身”**：如果你从 Microsoft Store 装过 Python，命令行里的 `python` 可能被它劫持，表现是能打开商店页面但跑不了脚本。卸载商店版，从 [python.org](https://www.python.org/downloads/) 装官方版最稳。

方式二（装 Agent Skill）需要 Node.js，同样去 [nodejs.org](https://nodejs.org) 下 LTS 版，安装选项保持默认即可。

## 五、只想要纯粹的 Obsidian 库

PowerShell（在库根目录执行）：

```powershell
Remove-Item -Recurse -Force prompts, skills, commands, tools, docs, .github, .claude-plugin, CONTRIBUTING.md, AGENTS.md
```

删掉之后 README、README.en、使用说明、EXAMPLES、CHANGELOG 里指向这些目录的链接会失效——**这是正常的**，不影响笔记库本身。想恢复就重新下载一份。

## 六、其他 Windows 特有提醒

- **行尾符**：Windows 的 Git 默认会把文件行尾转换成 CRLF。自己用完全无感；只有当你打算把修改推回 GitHub 时才需要在 Git 里设置 `core.autocrlf=false`（[原因说明](https://github.com/wangshuhui0613/personal-kb-template/blob/main/CONTRIBUTING.md)）。
- **别用记事本改 `.md` 文件**：记事本会加 BOM、可能改编码，Obsidian 会显示异常。用 Obsidian 本身、[VS Code](https://code.visualstudio.com) 或任何现代编辑器。
- **杀毒软件误报**：极少数情况下杀毒软件会拦 `health-check.cmd`（因为它调用了 Python）。这是误报，整个仓库只有这一个可执行入口，源码就在文件里，可以自己看。
