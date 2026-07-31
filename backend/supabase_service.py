import logging
from typing import Optional, Dict, Any, List
from backend.config import settings

logger = logging.getLogger(__name__)

class SupabaseService:
    """
    Supabase Python Service for database operations & realtime events.
    Falls back gracefully if Supabase credentials are not provided.
    """

    def __init__(self):
        self.client = None
        if settings.has_supabase:
            try:
                from supabase import create_client, Client
                self.client: Optional[Client] = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                logger.info("Supabase client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Supabase client: {e}")

    @property
    def is_active(self) -> bool:
        return self.client is not None

    def insert_topic(self, title: str) -> Optional[Dict[str, Any]]:
        if not self.is_active:
            return None
        try:
            res = self.client.table("topics").insert({"title": title}).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Supabase insert_topic error: {e}")
            return None

    def insert_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.is_active or not videos:
            return []
        try:
            res = self.client.table("videos").insert(videos).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Supabase insert_videos error: {e}")
            return []

    def insert_comments(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.is_active or not comments:
            return []
        try:
            res = self.client.table("comments").insert(comments).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Supabase insert_comments error: {e}")
            return []

    def insert_entropy_snapshot(self, topic_id: str, entropy: float, volatility: float, classification: str) -> Optional[Dict[str, Any]]:
        if not self.is_active:
            return None
        try:
            data = {
                "topic_id": topic_id,
                "entropy": entropy,
                "volatility": volatility,
                "classification": classification
            }
            res = self.client.table("entropy_snapshots").insert(data).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Supabase insert_entropy_snapshot error: {e}")
            return None

supabase_service = SupabaseService()
