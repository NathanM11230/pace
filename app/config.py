from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    anthropic_api_key: str
    newsdata_api_key: str
    elevenlabs_api_key: str
    database_url: str = "sqlite:///./pace.db"
    audio_files_dir: str = "./audio_files"
    scheduler_hour: int = 6
    scheduler_minute: int = 0
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
