import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # === PostgreSQL (Supabase / Railway) ===
    # DATABASE_URL: str | None = os.getenv("DATABASE_URL")

    # # === MySQL (optional, keep only if really needed) ===
    # === PostgreSQL (Supabase / Railway) ===
    # DATABASE_URL: str | None = os.getenv("DATABASE_URL")


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

