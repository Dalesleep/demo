from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SkillMetadata:
    id: str
    name: str
    description: str
    tags: list[str]
    path: str
    prompt: str


class SkillLoaderError(ValueError):
    pass


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        raise SkillLoaderError("Missing YAML frontmatter")

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SkillLoaderError("Missing YAML frontmatter delimiter")

    end_index = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break
    if end_index is None:
        raise SkillLoaderError("Unterminated YAML frontmatter")

    raw_yaml = "\n".join(lines[1:end_index]).strip()
    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")

    try:
        import yaml
    except ImportError as exc:
        raise SkillLoaderError("PyYAML is required to parse skill metadata") from exc

    data = yaml.safe_load(raw_yaml) or {}
    if not isinstance(data, dict):
        raise SkillLoaderError("Skill frontmatter must be a mapping")
    return data, body


def _normalize_tags(tags: Any) -> list[str]:
    if tags is None:
        return []
    if not isinstance(tags, list) or not all(isinstance(item, str) and item.strip() for item in tags):
        raise SkillLoaderError("Skill tags must be a list of non-empty strings")
    return [item.strip() for item in tags]


def _validate_skill_metadata(data: dict[str, Any], prompt: str, path: Path) -> SkillMetadata:
    name = data.get("name")
    description = data.get("description")
    tags = _normalize_tags(data.get("tags"))

    if not isinstance(name, str) or not name.strip():
        raise SkillLoaderError(f"Skill {path}: missing or invalid 'name'")
    if not isinstance(description, str) or not description.strip():
        raise SkillLoaderError(f"Skill {path}: missing or invalid 'description'")

    return SkillMetadata(
        id=path.parent.name,
        name=name.strip(),
        description=description.strip(),
        tags=tags,
        path=str(path),
        prompt=prompt.strip(),
    )


def load_skill(path: Path) -> SkillMetadata:
    raw = path.read_text(encoding="utf-8")
    data, body = _parse_frontmatter(raw)
    return _validate_skill_metadata(data, body, path)


def discover_skills(skills_dir: str | Path) -> list[SkillMetadata]:
    root = Path(skills_dir)
    if not root.exists():
        return []
    results: list[SkillMetadata] = []
    for skill_md in sorted(root.glob("*/SKILL.md")):
        results.append(load_skill(skill_md))
    return results


def find_skill_prompts(skills: list[SkillMetadata], active_skill_ids: list[str]) -> list[SkillMetadata]:
    if not active_skill_ids:
        return []
    by_id = {skill.id: skill for skill in skills}
    missing = [skill_id for skill_id in active_skill_ids if skill_id not in by_id]
    if missing:
        raise SkillLoaderError(f"Unknown skill id(s): {', '.join(missing)}")
    return [by_id[skill_id] for skill_id in active_skill_ids]

