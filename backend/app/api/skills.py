from fastapi import APIRouter

from app.services.skills_catalog import get_all_skills


router = APIRouter()


@router.get("/skills")
def list_skills() -> list[dict]:
    return [
        {
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "tags": skill.tags,
        }
        for skill in get_all_skills()
    ]

