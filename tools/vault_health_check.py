#!/usr/bin/env python3
"""Check the personal knowledge base for the failures that are easy to miss.

    python tools/vault_health_check.py --root .

What it catches:
  * missing entry pages
  * broken links in either syntax — [[wikilinks]] or [text](relative.md) —
    which is the classic silent rot (GitHub renders the latter, Obsidian the
    former; both must point at a real file)
  * action rows with missing fields, illegal states, or closed without evidence
    (light-tier rows — all seven non-core fields empty — are only checked for
    ID / next action / status; see the two registration tiers in 行动总览)
  * credentials and other sensitive values that should never have been written
  * template copies that drifted apart between 03-复盘与规划/99-模板/ (the
    Obsidian insertion source) and skills/personal-kb/assets/templates/ (the
    Skill distribution asset)
  * entry pages and actions nobody references (warning only — structure that
    exists but is never used is the earliest sign of ledger rot)

It never modifies anything. Exit code 1 means at least one problem was found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 各机私有目录：本机状态、工具缓存、版本库内部，都不算知识库内容。
PRIVATE_DIRS = frozenset({".git", ".workbuddy", ".obsidian", "node_modules", "__pycache__", ".github"})

# 模板源资件目录与目标目录：skills/ 里的模板按 build-brief 最终进入用户库的
# 03-复盘与规划/99-模板/（周复盘模板在 02-周复盘/、月复盘模板在 03-月复盘/，
# 与 99-模板/ 同深），相对链接按目标位置书写。这类文件不能按本仓库内的位置
# 解析（必然误报断链），check_links 对它们改按目标目录校验。
TEMPLATE_ASSET_PREFIX = "skills/personal-kb/assets/templates/"
TEMPLATE_DEST_DIR = "03-复盘与规划/99-模板"

# 模板双副本：99-模板/ 是 Obsidian 插入源，skills/assets/templates/ 是 Skill
# 分发资产（agent 装 Skill 只带 skills/ 目录），两边内容必须一致。改一边忘
# 另一边 = 两套用法静默分叉，故纳入体检（行尾归一化后比较，.gitattributes
# 已统一 LF，但 Windows 工作区可能显示 CRLF）。
TEMPLATE_PAIRS = tuple(
    (f"{TEMPLATE_DEST_DIR}/{name}", f"{TEMPLATE_ASSET_PREFIX}{name}")
    for name in ("日报模板.md", "周复盘模板.md", "月复盘模板.md", "决策模板.md", "经验卡片模板.md")
)

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

# 轻档必填三列（行动总览「两种登记档」）：其余七列留空即视为轻档
LIGHT_FIELDS = ("编号", "下一步动作", "状态")
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
SENSITIVE_SKIP = ("tools/", "AGENTS.md", "CONTRIBUTING.md", ".github/", "skills/")


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


def check_links(root: Path) -> tuple[list[str], int]:
    """返回 (问题列表, 实际校验的链接总数)。"""
    errors, total = [], 0
    for path in library_files(root):
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        relative = path.relative_to(root).as_posix()
        base = root / TEMPLATE_DEST_DIR if relative.startswith(TEMPLATE_ASSET_PREFIX) else path.parent
        for style, target in extract_links(text):
            name = Path(target).name
            if "." in name and not name.endswith(".md"):
                continue  # 附件链接，不强制解析
            total += 1
            if style == "[...](...)":
                # 标准 Markdown 相对链接：相对当前文件所在目录解析
                candidate = (base / target).resolve()
                if not candidate.is_file():
                    errors.append(
                        f"断链：{relative} -> ({target})"
                    )
                continue
            if not resolve(root, target):
                errors.append(
                    f"断链：{relative} -> [[{target}]]"
                )
    return errors, total


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


def action_rows(root: Path) -> list[dict]:
    """解析行动总览里的十字段行（不含表头与代码围栏里的示例）。"""
    path = root / "01-个人/00-行动与跟进/行动总览.md"
    if not path.is_file():
        return []
    return [r for r in parse_tables(path.read_text(encoding="utf-8", errors="replace"))
            if ACTION_ID_RE.fullmatch(r.get("编号", ""))]


def check_actions(root: Path) -> tuple[list[str], int]:
    """返回 (问题列表, 行动表行数)。"""
    rows = action_rows(root)
    if not rows:
        return ["行动总览里找不到可解析的十字段行动表"], 0
    errors, seen = [], set()
    for row in rows:
        aid = row["编号"]
        if aid in seen:
            errors.append(f"行动编号重复：{aid}")
        seen.add(aid)
        # 轻档/全档分级：七个非核心字段全空 = 轻档，只校验编号/动作/状态；
        # 任一非空 = 全档，十字段全校验（见行动总览「两种登记档」）。
        rest = {f: row.get(f, "").strip() for f in ACTION_FIELDS if f not in LIGHT_FIELDS}
        is_light = all(v == "" for v in rest.values())
        required = LIGHT_FIELDS if is_light else ACTION_FIELDS
        for field in required:
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
    return errors, len(rows)


def check_sensitive(root: Path) -> tuple[list[str], int, int]:
    """返回 (问题列表, 扫描文件数, 命中文件数)。"""
    errors, scanned, dirty = [], 0, 0
    for path in library_files(root):
        if path.suffix.lower() not in {".md", ".txt", ".yml", ".yaml", ".json"}:
            continue
        relative = path.relative_to(root).as_posix()
        if any(relative.startswith(s) for s in SENSITIVE_SKIP):
            continue
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        file_dirty = False
        for pattern, label in SENSITIVE_PATTERNS:
            for match in re.finditer(pattern, text):
                line = text[: match.start()].count("\n") + 1
                errors.append(f"疑似{label}：{relative}:{line} —— 请删除或移出库外")
                file_dirty = True
                break
        if file_dirty:
            dirty += 1
    return errors, scanned, dirty


def check_usage(root: Path) -> tuple[int, int, int, int]:
    """返回 (被引用的入口数, 入口总数, 被提及的行动数, 行动总数)。

    结构正确不代表结构在被用：没人引用的入口、没人提的行动，
    是账本腐化的最早信号（思路对标 second-brain-os 的 orphan rate）。
    本检查只警告，不计入 FAIL。
    """
    texts: dict[str, str] = {}
    for path in library_files(root):
        if path.suffix.lower() == ".md":
            texts[path.relative_to(root).as_posix()] = path.read_text(
                encoding="utf-8", errors="replace"
            )
    dashboard = "01-个人/00-行动与跟进/行动总览.md"
    mentions = "\n".join(text for rel, text in texts.items() if rel != dashboard)
    entries = [rel for rel in REQUIRED_FILES if (root / rel).is_file()]
    entries_hit = sum(
        1
        for rel in entries
        if any(rel in text or f"({rel})" in text or f"[[{Path(rel).stem}]]" in text
               for other, text in texts.items() if other != rel)
    )
    rows = action_rows(root)
    actions_hit = sum(1 for row in rows if row["编号"] in mentions)
    return entries_hit, len(entries), actions_hit, len(rows)


def check_template_sync(root: Path) -> tuple[list[str], int]:
    """模板双副本一致性。返回 (问题列表, 检查的模板数)。

    仅在库同时具备两侧目录时校验（本库以 Skill 分发时才存在双副本）；
    任一侧目录缺失 = 该库不使用双副本机制，整体跳过——本检查的目的是防
    「改一边忘另一边」，不是强制每个库都必须带模板。两侧目录都在而单个
    文件缺失或不一致，仍然算问题。
    """
    if not (root / TEMPLATE_DEST_DIR).is_dir() or not (root / TEMPLATE_ASSET_PREFIX).is_dir():
        return [], 0
    errors: list[str] = []
    for lib_rel, skill_rel in TEMPLATE_PAIRS:
        lib_p, skill_p = root / lib_rel, root / skill_rel
        if not lib_p.is_file() or not skill_p.is_file():
            errors.append(f"副本缺失: {lib_rel} / {skill_rel}")
            continue
        a = lib_p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        b = skill_p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        if a != b:
            errors.append(f"副本不一致: {lib_rel} ↔ {skill_rel}")
    return errors, len(TEMPLATE_PAIRS)


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


def run(root: Path) -> list[tuple[str, str, list[str]]]:
    """返回 [(检查项, 汇总, 问题列表)]，汇总由各项实际检查结果生成。"""
    required_errors = check_required(root)
    link_errors, link_total = check_links(root)
    action_errors, action_total = check_actions(root)
    sensitive_errors, sensitive_total, sensitive_dirty = check_sensitive(root)
    sync_errors, sync_total = check_template_sync(root)
    return [
        ("入口文件齐全", f"{len(REQUIRED_FILES) - len(required_errors)}/{len(REQUIRED_FILES)}", required_errors),
        ("链接完整", f"{link_total - len(link_errors)}/{link_total}", link_errors),
        ("行动字段与状态合法", f"{len(action_errors)} 错误 / {action_total} 条行动", action_errors),
        ("无敏感信息", f"{sensitive_total - sensitive_dirty}/{sensitive_total} 个文件", sensitive_errors),
        ("模板双副本一致", f"{sync_total - len(sync_errors)}/{sync_total}", sync_errors),
    ]


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

    checks = run(root)
    for name, summary, _errors in checks:
        print(f"CHECK: {name} ({summary})")

    entries_hit, entries_total, actions_hit, actions_total = check_usage(root)
    print(
        f"INFO: 入口被引用 ({entries_hit}/{entries_total})，"
        f"行动被提及 ({actions_hit}/{actions_total}) —— 仅警告，不计入结果"
    )

    all_errors = [e for _name, _summary, errs in checks for e in errs]
    if all_errors:
        for error in all_errors:
            print(error)
        print(f"\nFAIL: {len(all_errors)} 项问题")
        return 1
    print("PASS: 知识库体检通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
