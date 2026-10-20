"""tools/vault_health_check.py 的单元测试（stdlib unittest，无需第三方依赖）。

覆盖：
  * 两种链接语法（[[双链]] 与 [文字](相对路径.md)）的提取与断链检测
  * 模板源资件按目标目录（03-复盘与规划/99-模板/）解析——修复 Skill 路径
    建库模板断链后的回归保护
  * 行动十字段的字段、状态、关闭证据与编号唯一性校验
  * 敏感信息模式命中与跳过目录
  * CLI 退出码语义：0 通过 / 1 有问题（含目录不存在）
"""

import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.vault_health_check import (  # noqa: E402
    ACTION_FIELDS,
    REQUIRED_FILES,
    TEMPLATE_PAIRS,
    check_actions,
    check_links,
    check_sensitive,
    extract_links,
    resolve,
)

SCRIPT = REPO_ROOT / "tools" / "vault_health_check.py"
ACTION_HEADER = "| " + " | ".join(ACTION_FIELDS) + " |"
ACTION_SEP = "|" + "|".join("---" for _ in ACTION_FIELDS) + "|"


def write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def action_row(aid: str, **overrides: str) -> str:
    cells = {
        "编号": aid,
        "下一步动作": "推进这件事",
        "状态": "未开始",
        "状态原因": "无",
        "来源": "EXAMPLES.md",
        "归属": "个人",
        "硬截止": "无",
        "建议复核": "2026-11-01",
        "完成定义": "有可验证的产出",
        "完成证据": "待补",
    }
    cells.update(overrides)
    return "| " + " | ".join(cells[field] for field in ACTION_FIELDS) + " |"


def build_dashboard(root: Path, *rows: str) -> None:
    write(
        root,
        "01-个人/00-行动与跟进/行动总览.md",
        "\n".join(["# 行动总览", "", ACTION_HEADER, ACTION_SEP, *rows]) + "\n",
    )


def build_mini_vault(root: Path) -> None:
    """一套能通过全部检查的最小库：11 个入口文件 + 一条合法行动 + 5 套模板双副本。"""
    for relative in REQUIRED_FILES:
        write(root, relative, f"# {Path(relative).stem}\n")
    build_dashboard(root, action_row("A-001"))
    # 模板双副本：99-模板/ 是 Obsidian 插入源，skills/assets/templates/ 是 Skill
    # 建库源，两边必须同时存在且内容一致（check_template_sync 检查项）。
    for lib_rel, skill_rel in TEMPLATE_PAIRS:
        text = f"# {Path(lib_rel).stem}\n"
        write(root, lib_rel, text)
        write(root, skill_rel, text)


class ExtractLinksTests(unittest.TestCase):
    def test_both_syntaxes_skips_code_and_external(self):
        text = (
            "见 [[路径/笔记|显示名]] 与 [文字](子目录/笔记.md)。\n"
            "行内代码 `[[不是链接]]` 和围栏里的都不算：\n"
            "```markdown\n[[围栏里的也不是]](围栏.md)\n```\n"
            "外链 [官网](https://example.com) 与锚点 [跳转](#标题) 不解析；\n"
            "缺后缀又缺斜杠的 [纯名字](笔记) 也不算标准 Markdown 链接。"
        )
        self.assertEqual(
            extract_links(text),
            [("[[...]]", "路径/笔记"), ("[...](...)", "子目录/笔记.md")],
        )


class CheckLinksTests(unittest.TestCase):
    def test_detects_broken_and_accepts_valid(self):
        with TemporaryDirectory() as tmp, self.subTest("两种语法的断链都报警"):
            root = Path(tmp)
            write(root, "a/甲.md", "双链 [[不存在]] 加 [x](缺失.md)。")
            errors, total = check_links(root)
            self.assertEqual(total, 2)
            self.assertEqual(len(errors), 2)
            self.assertIn("[[不存在]]", errors[0])
            self.assertIn("(缺失.md)", errors[1])
        with TemporaryDirectory() as tmp, self.subTest("两种语法的有效链接都通过"):
            root = Path(tmp)
            write(root, "a/甲.md", "见 [[乙]] 与 [乙](../b/乙.md)。")
            write(root, "b/乙.md", "# 乙")
            errors, total = check_links(root)
            self.assertEqual((errors, total), ([], 2))

    def test_template_assets_resolve_against_destination_dir(self):
        # 回归：Skill 模板的相对链接按目标位置（99-模板/，与 02-周复盘/、
        # 03-月复盘/ 同深）书写，此前按源仓库位置解析会误报断链。
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "skills/personal-kb/assets/templates/日报模板.md",
                  "去 [行动总览](../../01-个人/00-行动与跟进/行动总览.md) 开编号。")
            write(root, "01-个人/00-行动与跟进/行动总览.md", "# 行动总览")
            errors, total = check_links(root)
            self.assertEqual((errors, total), ([], 1))
            write(root, "skills/personal-kb/assets/templates/日报模板.md",
                  "去 [行动总览](../../../../01-个人/00-行动与跟进/行动总览.md) 开编号。")
            errors, total = check_links(root)
            self.assertEqual(total, 1)
            self.assertTrue(any("日报模板.md" in error for error in errors))


class ResolveTests(unittest.TestCase):
    def test_matches_stem_anywhere_and_exact_path(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "one/笔记.md", "# one")
            write(root, "two/笔记.md", "# two")
            self.assertEqual(len(resolve(root, "笔记")), 2)
            self.assertEqual(resolve(root, "one/笔记"), [root / "one/笔记.md"])
            self.assertEqual(resolve(root, "one/笔记.md"), [root / "one/笔记.md"])
            self.assertEqual(resolve(root, "不存在/笔记"), [])


class CheckActionsTests(unittest.TestCase):
    def test_accepts_valid_dashboard(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_dashboard(root, action_row("A-001"))
            self.assertEqual(check_actions(root), ([], 1))

    def test_reports_field_and_state_problems(self):
        with TemporaryDirectory() as tmp, self.subTest("缺字段值与非法状态"):
            root = Path(tmp)
            build_dashboard(
                root,
                action_row("A-001", 来源="  "),
                action_row("A-002", 状态="搞定啦"),
            )
            errors, count = check_actions(root)
            self.assertEqual(count, 2)
            self.assertTrue(any("A-001 未填写来源" in e for e in errors))
            self.assertTrue(any("A-002 状态非法" in e for e in errors))
        with TemporaryDirectory() as tmp, self.subTest("进行中必须写状态原因"):
            root = Path(tmp)
            build_dashboard(root, action_row("A-001", 状态="进行中", 状态原因="待补"))
            errors, _count = check_actions(root)
            self.assertTrue(any("A-001 是进行中状态，必须写清状态原因" in e for e in errors))

    def test_closed_requires_evidence_with_date(self):
        cases = {
            "证据待补": ({"完成证据": "待补"}, "已关闭但缺少完成证据"),
            "证据无日期": ({"完成证据": "已交付"}, "已关闭但完成证据里没有日期"),
        }
        for name, (overrides, expected) in cases.items():
            with TemporaryDirectory() as tmp, self.subTest(name):
                root = Path(tmp)
                build_dashboard(root, action_row("A-001", 状态="已完成", **overrides))
                errors, _count = check_actions(root)
                self.assertTrue(any(expected in e for e in errors))
        with TemporaryDirectory() as tmp, self.subTest("证据带日期即合法"):
            root = Path(tmp)
            build_dashboard(
                root, action_row("A-001", 状态="已完成", 完成证据="2026-10-17 已交付")
            )
            self.assertEqual(check_actions(root)[0], [])

    def test_rejects_duplicate_ids_and_empty_table(self):
        with TemporaryDirectory() as tmp, self.subTest("编号重复"):
            root = Path(tmp)
            build_dashboard(root, action_row("A-001"), action_row("A-001"))
            errors, _count = check_actions(root)
            self.assertTrue(any("行动编号重复：A-001" in e for e in errors))
        with TemporaryDirectory() as tmp, self.subTest("空表无法解析"):
            root = Path(tmp)
            write(root, "01-个人/00-行动与跟进/行动总览.md", "# 行动总览\n\n还没有行动。\n")
            self.assertEqual(
                check_actions(root),
                (["行动总览里找不到可解析的十字段行动表"], 0),
            )


class CheckSensitiveTests(unittest.TestCase):
    def test_flags_patterns_and_skips_listed_paths(self):
        token = "ghp_" + "a1b2c3d4e5f6g7h8i9j0"
        with TemporaryDirectory() as tmp, self.subTest("命中即报警"):
            root = Path(tmp)
            write(root, "笔记.md", f"令牌 {token} 不要提交")
            errors, scanned, dirty = check_sensitive(root)
            self.assertEqual((scanned, dirty), (1, 1))
            self.assertTrue(any("GitHub 令牌" in e and "笔记.md:1" in e for e in errors))
        with TemporaryDirectory() as tmp, self.subTest("跳过目录不计入"):
            root = Path(tmp)
            write(root, "tools/说明.md", f"示例令牌 {token}")
            errors, scanned, dirty = check_sensitive(root)
            self.assertEqual((errors, scanned, dirty), ([], 0, 0))
        with TemporaryDirectory() as tmp, self.subTest("干净文件零命中"):
            root = Path(tmp)
            write(root, "笔记.md", "普通内容，2026-10-17 的记录。")
            self.assertEqual(check_sensitive(root)[2], 0)


class CliExitCodeTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_exit_codes(self):
        with TemporaryDirectory() as tmp, self.subTest("目录不存在返回 1"):
            result = self.run_cli("--root", str(Path(tmp) / "no-such-vault"))
            self.assertEqual(result.returncode, 1)
            self.assertIn("目录不存在", result.stdout)
            self.assertNotIn("Traceback", result.stderr)
        with TemporaryDirectory() as tmp, self.subTest("完整小库返回 0"):
            root = Path(tmp)
            build_mini_vault(root)
            result = self.run_cli("--root", str(root))
            self.assertEqual(result.returncode, 0)
            self.assertIn("PASS", result.stdout)
        with TemporaryDirectory() as tmp, self.subTest("断链返回 1"):
            root = Path(tmp)
            build_mini_vault(root)
            write(root, "01-个人/规划总览.md", "见 [决策日志](02-工作经历/01_决策日志/不存在的日志.md)。")
            result = self.run_cli("--root", str(root))
            self.assertEqual(result.returncode, 1)
            self.assertIn("断链", result.stdout)
            self.assertIn("FAIL", result.stdout)


if __name__ == "__main__":
    unittest.main()
