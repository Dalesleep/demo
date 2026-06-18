from pathlib import Path

import pytest

from app.services.skill_loader import SkillLoaderError, discover_skills, load_skill


def test_discover_skills_loads_all_three():
    skills = discover_skills(Path("app/skills"))
    skill_ids = {skill.id for skill in skills}

    assert skill_ids == {"code-review", "test-generator", "data-analysis"}


def test_load_skill_parses_metadata(tmp_path: Path):
    skill_dir = tmp_path / "custom-skill"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(
        """---
name: custom-skill
description: Custom skill description
tags:
  - alpha
  - beta
---

# Body
""",
        encoding="utf-8",
    )

    skill = load_skill(skill_file)

    assert skill.id == "custom-skill"
    assert skill.name == "custom-skill"
    assert skill.description == "Custom skill description"
    assert skill.tags == ["alpha", "beta"]


@pytest.mark.parametrize(
    "content",
    [
        "# no frontmatter",
        """---
name: missing-description
tags: [a]
---
""",
        """---
description: missing-name
tags: [a]
---
""",
        """---
name: bad-tags
description: nope
tags: bad
---
""",
    ],
)
def test_load_skill_rejects_invalid_metadata(tmp_path: Path, content: str):
    skill_dir = tmp_path / "broken-skill"
    skill_dir.mkdir()
    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(content, encoding="utf-8")

    with pytest.raises(SkillLoaderError):
        load_skill(skill_file)

