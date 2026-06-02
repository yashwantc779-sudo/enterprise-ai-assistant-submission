from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/enterprise.db"
    VECTOR_DB_PATH: str = "./data/chroma_db"
    LOG_LEVEL: str = "INFO"
    MOCK_LLM: bool = False
    MAX_SCHEMA_RESULTS: int = 5
    MAX_SQL_RETRIES: int = 3
    SEMANTIC_CACHE_ENABLED: bool = True
    GEMINI_MODEL: str = "gemini-2.0-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def use_mock_llm(self) -> bool:
        if self.MOCK_LLM:
            return True
        key = (self.GEMINI_API_KEY or "").strip()
        return not key or key.startswith("your_")

    @property
    def sql_dialect(self) -> str:
        if "postgresql" in self.DATABASE_URL:
            return "postgres"
        if "mysql" in self.DATABASE_URL:
            return "mysql"
        return "sqlite"


settings = Settings()
