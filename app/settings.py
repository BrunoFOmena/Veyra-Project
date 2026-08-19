from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "veyra"
    postgres_user: str = "veyra"
    postgres_password: str = "veyra"

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "veyra"
    minio_secret_key: str = "veyrasecret"
    minio_bucket: str = "veyra-bronze"
    minio_secure: bool = False

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def minio_url(self) -> str:
        scheme = "https" if self.minio_secure else "http"
        return f"{scheme}://{self.minio_endpoint}"


settings = Settings()
