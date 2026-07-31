import logging
import uuid
from typing import Optional, Dict, Any, List
from .config import settings

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
                url = settings.SUPABASE_URL.strip().rstrip('/')
                if url.endswith('/rest/v1'):
                    url = url[:-len('/rest/v1')].rstrip('/')
                key = (settings.SUPABASE_KEY.strip() or 
                       settings.SUPABASE_SECRET_KEY.strip() or 
                       settings.SUPABASE_PUBLISHABLE_KEY.strip())
                self.client: Optional[Client] = create_client(url, key)
                logger.info("Supabase client initialized successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Supabase client: {e}")

    @property
    def is_active(self) -> bool:
        return self.client is not None

    def insert_topic(self, title: str, topic_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.is_active:
            return None
        try:
            row_id = topic_id or str(uuid.uuid4())
            res = self.client.table("topics").insert({"id": row_id, "title": title}).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Supabase insert_topic error: {e}")
            return None

    def insert_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.is_active or not videos:
            return []
        try:
            payload = []
            for v in videos:
                item = dict(v)
                if not item.get("id"):
                    item["id"] = str(uuid.uuid4())
                payload.append(item)
            res = self.client.table("videos").insert(payload).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Supabase insert_videos error: {e}")
            return []

    def insert_comments(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.is_active or not comments:
            return []
        try:
            payload = []
            for c in comments:
                item = dict(c)
                if not item.get("id"):
                    item["id"] = str(uuid.uuid4())
                payload.append(item)
            res = self.client.table("comments").insert(payload).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Supabase insert_comments error: {e}")
            return []

    def insert_entropy_snapshot(self, topic_id: str, entropy: float, volatility: float, classification: str, snapshot_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.is_active:
            return None
        try:
            data = {
                "id": snapshot_id or str(uuid.uuid4()),
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

    def insert_news_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.is_active or not articles:
            return []
        try:
            payload = []
            for art in articles:
                item = dict(art)
                if not item.get("id"):
                    item["id"] = str(uuid.uuid4())
                payload.append(item)
            res = self.client.table("news_articles").insert(payload).execute()
            return res.data or []
        except Exception as e:
            logger.error(f"Supabase insert_news_articles error: {e}")
            return []

supabase_service = SupabaseService()
