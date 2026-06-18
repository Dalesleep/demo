from app.agents.factory import build_agent, compose_skill_prompt
from app.services.skill_loader import SkillMetadata


def test_build_agent_returns_agent():
    agent = build_agent(active_skill_ids=[])
    assert agent is not None


def test_compose_skill_prompt_includes_skill_body():
    prompt = compose_skill_prompt(
        [
            SkillMetadata(
                id="code-review",
                name="code-review",
                description="Review source code and find correctness, maintainability, and testing issues.",
                tags=["code", "review"],
                path="app/skills/code-review/SKILL.md",
                prompt="Use this when reviewing code.",
            )
        ]
    )

    assert "code-review" in prompt
    assert "Use this when reviewing code." in prompt

