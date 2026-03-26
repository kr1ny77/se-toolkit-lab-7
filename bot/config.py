from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env.bot.secret"


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    bot_token: str = Field(default="", validation_alias="BOT_TOKEN")
    lms_api_base_url: str = Field(default="http://localhost:42002", validation_alias="LMS_API_BASE_URL")
    lms_api_key: str = Field(default="", validation_alias="LMS_API_KEY")
    llm_api_key: str = Field(default="", validation_alias="LLM_API_KEY")
    llm_api_base_url: str = Field(default="", validation_alias="LLM_API_BASE_URL")
    llm_api_model: str = Field(default="", validation_alias="LLM_API_MODEL")

    @property
    def is_test_mode(self) -> bool:
        return not self.bot_token


config = BotConfig()
