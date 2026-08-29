import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_manifest_is_valid():
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "romhacking"
    assert re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"])
    assert len(manifest["description"]) > 40


def test_every_skill_has_a_description():
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    assert skills, "no skills found"
    for skill in skills:
        text = skill.read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{skill.parent.name}: missing frontmatter"
        frontmatter = text.split("---", 2)[1]
        assert re.search(r"^description:\s*\S", frontmatter, re.M), \
            f"{skill.parent.name}: missing description"


def test_infrastructure_skills_are_hidden_from_the_user():
    import roles
    for name in ("project-state", "toolchain"):
        text = roles.skill_text(name)
        frontmatter = text.split("---", 2)[1]
        assert "user-invocable: false" in frontmatter, (
            f"{name} is infrastructure: it must not appear in the / menu"
        )
