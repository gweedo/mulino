from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """What migrations, seeds and the session factory need — no auth config."""

    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Settings(DatabaseSettings):
    # Supabase project URL, e.g. https://<ref>.supabase.co — issuer and JWKS derive from it.
    SUPABASE_URL: str

    @property
    def supabase_auth_issuer(self) -> str:
        return f"{self.SUPABASE_URL.rstrip('/')}/auth/v1"

    @property
    def supabase_jwks_url(self) -> str:
        return f"{self.supabase_auth_issuer}/.well-known/jwks.json"


def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()  # type: ignore[call-arg]


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
