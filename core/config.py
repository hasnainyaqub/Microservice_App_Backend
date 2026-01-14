import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # === PostgreSQL (Supabase / Railway) ===
    # DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    # # === MySQL (optional, keep only if really needed) ===
    MYSQL_HOST: str | None = os.getenv("MYSQL_HOST")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER: str | None = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str | None = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB: str | None = os.getenv("MYSQL_DB")

    # # === Redis ===
    REDIS_HOST: str | None = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", 300))

    # === FastAPI ===
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    # === Security ===
    API_BEARER_TOKEN: str | None = os.getenv("API_BEARER_TOKEN")

    # === Groq ===
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")


settings = Settings()

