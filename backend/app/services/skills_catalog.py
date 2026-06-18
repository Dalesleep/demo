from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
from app.services.skill_loader import discover_skills


@lru_cache(maxsize=1)
def get_all_skills():
    settings = get_settings()
    return discover_skills(Path(settings.skills_dir))

