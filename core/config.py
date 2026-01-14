import os
from dotenv import load_dotenv

# === Load environment variables from .env file ===
load_dotenv()

# === Application Settings ===
class Settings:
    # MySQL
    MYSQL_HOST: str = os.getenv("MYSQL_HOST")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB: str = os.getenv("MYSQL_DB")

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_TTL: int = int(os.getenv("REDIS_TTL", 300))

    # FastAPI
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))

    # Security
    API_BEARER_TOKEN: str = os.getenv("API_BEARER_TOKEN")

    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")

# === Instantiate Settings Object ===
settings = Settings()
