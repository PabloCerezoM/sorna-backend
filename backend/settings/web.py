from hashlib import blake2b
from platform import uname
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET = blake2b(
    str(uname()._asdict()).encode("utf-8"),
    digest_size=32,
).hexdigest()

class WebSettings(BaseSettings):
    model_config = SettingsConfigDict(
        # secrets_dir="/vault/secrets/rule_shooter",
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    WEB_SESSION_SECRET: str = DEFAULT_SECRET
