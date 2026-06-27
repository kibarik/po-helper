import pathlib
import re
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKILLS = [
    "blueprint-context", "blueprint-extract", "blueprint-discover",
    "blueprint-model", "blueprint-render",
]


def _frontmatter(p):
    text = p.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, f"no frontmatter in {p}"
    return yaml.safe_load(m.group(1))


def test_all_skills_exist_with_valid_frontmatter():
    for slug in SKILLS:
        p = ROOT / ".claude/skills" / slug / "SKILL.md"
        assert p.exists(), f"missing {p}"
        fm = _frontmatter(p)
        assert fm.get("name") == slug, f"{slug}: name mismatch: {fm.get('name')!r}"
        assert fm.get("description"), f"{slug}: empty description"


def test_render_skill_has_template():
    assert (ROOT / ".claude/skills/blueprint-render/references/mermaid-template.md").exists()
