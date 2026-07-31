import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_FILE)
load_dotenv()

class Settings(BaseSettings):
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Configurable Entropy & Volatility Thresholds
    GENUINE_CONSENSUS_ENTROPY_MAX: float = 0.85
    GENUINE_CONSENSUS_VOLATILITY_MAX: float = 0.15
    FRAGILE_CONSENSUS_ENTROPY_MAX: float = 1.15
    FRAGILE_CONSENSUS_VOLATILITY_MIN: float = 0.15
    FALSE_CONVERGENCE_REASON_DIVERGENCE_MIN: float = 0.60

    @property
    def has_youtube_key(self) -> bool:
        return bool(self.YOUTUBE_API_KEY.strip())

    @property
    def has_supabase(self) -> bool:
        return bool(self.SUPABASE_URL.strip() and self.SUPABASE_KEY.strip())

    @property
    def has_anthropic_key(self) -> bool:
        return bool(self.ANTHROPIC_API_KEY.strip())

    @property
    def has_openai_key(self) -> bool:
        return bool(self.OPENAI_API_KEY.strip())

    @property
    def has_news_api_key(self) -> bool:
        return bool(self.NEWS_API_KEY.strip())

settings = Settings()
