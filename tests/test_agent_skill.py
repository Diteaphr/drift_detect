"""The benchmark skill has one source and per-tool pointers that must stay in sync."""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / ".agents" / "skills" / "dataset0921-benchmark" / "SKILL.md"
CLAUDE_COPY = REPO / ".claude" / "skills" / "dataset0921-benchmark" / "SKILL.md"
POINTERS = [CLAUDE_COPY, REPO / "AGENTS.md", REPO / ".github" / "copilot-instructions.md"]


def frontmatter(path: Path) -> dict:
    match = re.match(r"---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    assert match, f"{path} has no frontmatter"
    return dict(line.split(": ", 1) for line in match.group(1).splitlines() if ": " in line)


class TestAgentSkill(unittest.TestCase):
    def test_source_files_exist(self):
        self.assertTrue(SKILL.exists())
        self.assertTrue((SKILL.parent / "protocols.md").exists())

    def test_frontmatter_matches_source(self):
        source = frontmatter(SKILL)
        self.assertEqual(source["name"], SKILL.parent.name)
        self.assertLessEqual(len(source["description"]), 1024)
        self.assertEqual(frontmatter(CLAUDE_COPY), source)

    def test_pointers_reference_source(self):
        for path in POINTERS:
            self.assertIn(".agents/skills/dataset0921-benchmark/SKILL.md", path.read_text(encoding="utf-8"), path)
        self.assertIn("AGENTS.md", (REPO / "GEMINI.md").read_text(encoding="utf-8"))

    def test_relative_links_resolve(self):
        for target in re.findall(r"\]\(([^)#:]+)\)", SKILL.read_text(encoding="utf-8")):
            self.assertTrue((SKILL.parent / target).exists(), target)


if __name__ == "__main__":
    unittest.main()
