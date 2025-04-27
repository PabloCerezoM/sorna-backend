from hashlib import blake2b
from platform import uname
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_SECRET = blake2b(
    str(uname()._asdict()).encode("utf-8"),
    digest_size=32,
).hexdigest()

class WebSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    WEB_TITLE: str = "Sorna API"
    WEB_COOKIE_SECRET: str = DEFAULT_SECRET
    WEB_FQDN: str = "localhost"
    WEB_COOKIE_EXPIRATION_SECONDS: int = 14400 # 4 hours
    WEB_COOKIE_EXTEND_TRIGGER_SECONDS: int = 600 # 10 minutes
