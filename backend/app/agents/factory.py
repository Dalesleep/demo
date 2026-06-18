from pathlib import Path

from pydantic_ai.models.test import TestModel
from pydantic_deep import StateBackend, create_deep_agent

from app.core.config import get_settings
from app.services.mcp_registry import get_mcp_registry
from app.services.skill_loader import SkillMetadata, find_skill_prompts
from app.services.skills_catalog import get_all_skills


def compose_skill_prompt(skills: list[SkillMetadata]) -> str:
    if not skills:
        return ""
    chunks: list[str] = ["The following skills are enabled for this session:"]
    for skill in skills:
        chunks.append(f"\n## Skill: {skill.name} ({skill.id})")
        if skill.tags:
            chunks.append(f"Tags: {', '.join(skill.tags)}")
        chunks.append(skill.prompt)
    return "\n".join(chunks).strip()


def build_agent(active_skill_ids: list[str] | None = None):
    settings = get_settings()
    if settings.agent_model == "test":
        model = TestModel(custom_output_text=settings.test_model_reply)
    else:
        model = settings.agent_model

    skills = get_all_skills()
    active_skill_ids = active_skill_ids or []
    active_skills = find_skill_prompts(skills, active_skill_ids)
    skill_prompt = compose_skill_prompt(active_skills)
    mcp_registry = get_mcp_registry()
    mcp_context = mcp_registry.available_context()
    instructions = settings.agent_instructions
    instructions = f"{instructions}\n\nMCP context:\n{mcp_context}"
    if skill_prompt:
        instructions = f"{instructions}\n\n{skill_prompt}"

    return create_deep_agent(
        model=model,
        instructions=instructions,
        skill_directories=[str(Path(settings.skills_dir))],
        include_memory=False,
        include_filesystem=False,
        include_subagents=False,
        include_skills=True,
        include_todo=False,
        include_plan=False,
        web_search=False,
        web_fetch=False,
        thinking=False,
        context_manager=False,
        include_history_archive=False,
        cost_tracking=False,
    )


def get_agent_for_session(session):
    return build_agent(active_skill_ids=session.active_skills)
