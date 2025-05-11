from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenaiSettings(BaseSettings):
    model_config = SettingsConfigDict(
    env_file=".env",
    case_sensitive=True,
    extra="ignore",
    )
        
    OPENAI_API_KEY: str = ""