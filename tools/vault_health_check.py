#!/usr/bin/env python3
"""Check the personal knowledge base for the failures that are easy to miss.

    python tools/vault_health_check.py --root .

What it catches:
  * missing entry pages
  * broken links in either syntax — [[wikilinks]] or [text](relative.md) —
    which is the classic silent rot (GitHub renders the latter, Obsidian the
    former; both must point at a real file)
  * action rows with missing fields, illegal states, or closed without evidence
  * credentials and other sensitive values that should never have been written

It never modifies anything. Exit code 1 means at least one problem was found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 各机私有目录：本机状态、工具缓存、版本库内部，都不算知识库内容。
PRIVATE_DIRS = frozenset({".git", ".workbuddy", ".obsidian", "node_modules", "__pycache__", ".github"})

REQUIRED_FILES = (
    "README.md",
    "使用说明.md",
    "AGENTS.md",
    "01-个人/00-行动与跟进/行动总览.md",
    "01-个人/规划总览.md",
    "02-工作经历/00_总览/项目索引.md",
    "02-工作经历/01_决策日志/决策日志.md",
    "02-工作经历/02_主题手册/主题手册索引.md",
    "02-工作经历/03_经验卡片/经验卡片索引.md",
    "03-复盘与规划/复盘与规划.md",
    "03-复盘与规划/07-对话沉淀/对话沉淀说明.md",
)

RAW_LAYERS = (
    "02-工作经历/04_日报素材/",
    "02-工作经历/05_文档原文/",
    "02-工作经历/07_附件/",
)

ACTION_FIELDS = (
    "编号", "下一步动作", "状态", "状态原因", "来源",
    "归属", "硬截止", "建议复核", "完成定义", "完成证据",
)
ACTION_ID_RE = re.compile(r"^[AEWJH]-\d{3}$")
STATES = {"未开始", "进行中", "等待", "待判断", "暂缓", "状态不明", "已完成", "已取消"}
CLOSED = {"已完成", "已取消"}
# 同时支持两种链接写法：
#   [[路径]]              —— Obsidian 双链（库内使用）
#   [文字](路径.md)        —— 标准 Markdown 相对链接（GitHub 网页上可点击）
# 两种都必须是真实存在的文件，否则就是断链。
LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)\)")

# 命中即报警。宁可误报，也不要让令牌进版本库。
SENSITIVE_PATTERNS = (
    (r"gh[pousr]_[A-Za-z0-9]{16,}", "GitHub 令牌"),
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI 风格密钥"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "Slack 令牌"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----", "私钥"),
    (r"\b\d{17}[\dXx]\b", "疑似身份证号"),
    (r"\b\d{16,19}\b", "疑似银行卡号"),
    (r"Bearer\s+[A-Za-z0-9._-]{20,}", "Bearer 令牌"),
)
# 这些字段出现在说明文字里是正常的（比如本文件、AGENTS.md），要跳过。
SENSITIVE_SKIP = ("tools/", "AGENTS.md", "CONTRIBUTING.md", ".github/", "skill/")


def library_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in PRIVATE_DIRS for part in path.relative_to(root).parts):
            continue
        yield path


def strip_code(text: str) -> str:
    """Drop fenced blocks and inline code so examples don't count as content."""
    return re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", text, flags=re.S), flags=re.S)


def extract_links(text: str) -> list[tuple[str, str]]:
    """返回 (写法, 目标) 列表。写法仅用于报错时说明是哪种链接。"""
    found = []
    for match in LINK_RE.finditer(strip_code(text)):
        target = match.group(1).replace(r"\|", "|").split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            found.append(("[[...]]", target))
    for match in MD_LINK_RE.finditer(strip_code(text)):
        target = match.group(1)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue  # 外链与页内锚点不强制解析
        target = target.split("#", 1)[0].split("?", 1)[0]
        if target.endswith(".md") or "/" in target:
            found.append(("[...](...)", target))
    return found


def resolve(root: Path, target: str) -> list[Path]:
    if "/" in target:
        candidate = root / target
        for path in ([candidate] if target.endswith(".md") else [candidate, Path(str(candidate) + ".md")]):
            if path.is_file():
                return [path]
        return []
    return [p for p in library_files(root) if p.stem == target or p.name == target]


def check_required(root: Path) -> list[str]:
    return [f"缺少入口文件：{rel}" for rel in REQUIRED_FILES if not (root / rel).is_file()]


def check_links(root: Path) -> list[str]:
    errors = []
    for path in library_files(root):
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for style, target in extract_links(text):
            name = Path(target).name
            if "." in name and not name.endswith(".md"):
                continue  # 附件链接，不强制解析
            if style == "[...](...)":
                # 标准 Markdown 相对链接：相对当前文件所在目录解析
                candidate = (path.parent / target).resolve()
                if not candidate.is_file():
                    errors.append(
                        f"断链：{path.relative_to(root).as_posix()} -> ({target})"
                    )
                continue
            if not resolve(root, target):
                errors.append(
                    f"断链：{path.relative_to(root).as_posix()} -> [[{target}]]"
                )
    return errors


def parse_tables(text: str):
    """Very small Markdown table reader: enough for the action dashboard."""
    rows, header, has_sep = [], None, False
    for line in strip_code(text).splitlines():
        if not line.lstrip().startswith("|"):
            header, has_sep = None, False
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
            has_sep = bool(header)
            continue
        if header is None:
            header, has_sep = cells, False
            continue
        if has_sep and len(cells) == len(header):
            rows.append(dict(zip(header, cells)))
    return rows


def check_actions(root: Path) -> list[str]:
    path = root / "01-个人/00-行动与跟进/行动总览.md"
    if not path.is_file():
        return []
    rows = [r for r in parse_tables(path.read_text(encoding="utf-8", errors="replace"))
            if ACTION_ID_RE.fullmatch(r.get("编号", ""))]
    if not rows:
        return ["行动总览里找不到可解析的十字段行动表"]
    errors, seen = [], set()
    for row in rows:
        aid = row["编号"]
        if aid in seen:
            errors.append(f"行动编号重复：{aid}")
        seen.add(aid)
        for field in ACTION_FIELDS:
            if field not in row:
                errors.append(f"行动表缺少字段：{field}（{aid}）")
            elif not row[field].strip():
                errors.append(f"{aid} 未填写{field}")
        status = row.get("状态", "")
        if status not in STATES:
            errors.append(f"{aid} 状态非法：{status}")
        if status in {"进行中", "等待", "暂缓"} and row.get("状态原因", "") in {"", "无", "待补"}:
            errors.append(f"{aid} 是{status}状态，必须写清状态原因")
        if status in CLOSED:
            evidence = row.get("完成证据", "")
            if "待补" in evidence or "无记录" in evidence or not evidence.strip():
                errors.append(f"{aid} 已关闭但缺少完成证据")
            if not re.search(r"\d{4}-\d{2}-\d{2}", evidence):
                errors.append(f"{aid} 已关闭但完成证据里没有日期")
    return errors


def check_sensitive(root: Path) -> list[str]:
    errors = []
    for path in library_files(root):
        if path.suffix.lower() not in {".md", ".txt", ".yml", ".yaml", ".json"}:
            continue
        relative = path.relative_to(root).as_posix()
        if any(relative.startswith(s) for s in SENSITIVE_SKIP):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern, label in SENSITIVE_PATTERNS:
            for match in re.finditer(pattern, text):
                line = text[: match.start()].count("\n") + 1
                errors.append(f"疑似{label}：{relative}:{line} —— 请删除或移出库外")
                break
    return errors


def measure(root: Path) -> dict[str, int]:
    def count(rel: str, predicate) -> int:
        directory = root / rel
        if not directory.is_dir():
            return 0
        return sum(1 for p in directory.rglob("*.md") if predicate(p.name))

    return {
        "经验卡片": count("02-工作经历/03_经验卡片", lambda n: not n.endswith("索引.md")),
        "决策": count("02-工作经历/01_决策日志", lambda n: not n.endswith("日志.md")),
        "主题手册": count("02-工作经历/02_主题手册", lambda n: not n.endswith("索引.md")),
        "日报": count("03-复盘与规划/01-每日记录", lambda n: re.fullmatch(r"\d{4}-\d{2}-\d{2}\.md", n) is not None),
        "周复盘": count("03-复盘与规划/02-周复盘", lambda n: not n.endswith(("索引.md", "模板.md"))),
        "月复盘": count("03-复盘与规划/03-月复盘", lambda n: not n.endswith(("索引.md", "模板.md"))),
    }


def run(root: Path) -> list[str]:
    errors = check_required(root)
    errors += check_links(root)
    errors += check_actions(root)
    errors += check_sensitive(root)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="知识库根目录，默认当前目录")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"目录不存在：{root}")
        return 1

    stats = measure(root)
    print("STATS: " + "，".join(f"{k}={v}" for k, v in stats.items()))

    errors = run(root)
    if errors:
        for error in errors:
            print(error)
        print(f"\nFAIL: {len(errors)} 项问题")
        return 1
    print("PASS: 知识库体检通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
