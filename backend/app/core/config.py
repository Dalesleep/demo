from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "DeepAgents Web Console MVP"
    agent_model: str = Field(default="test")
    agent_instructions: str = Field(default="你是一名简洁、可靠的中文助手。")
    test_model_reply: str = Field(default="你好，我正在通过 pydantic-deep 运行。")
    skills_dir: str = Field(default="app/skills")
    mcp_config_path: str = Field(default="config/mcp.json")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
