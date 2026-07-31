import re
import logging
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from backend.config import settings

logger = logging.getLogger(__name__)

class YouTubeService:
    """
    Service to fetch YouTube videos and comments via Google API Client,
    with text cleaning and robust fallback dataset generation.
    """

    def __init__(self):
        self.youtube_client = None
        if settings.has_youtube_key:
            try:
                from googleapiclient.discovery import build
                self.youtube_client = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
                logger.info("YouTube API client initialized successfully.")
            except Exception as e:
                logger.warning(f"Failed to initialize YouTube API client: {e}")

    def fetch_videos_and_comments(self, topic: str, max_videos: int = 10, max_comments_per_video: int = 100) -> Dict[str, Any]:
        """
        Fetches top videos and their comments for a topic.
        """
        if self.youtube_client:
            try:
                videos = self._search_videos(topic, max_results=max_videos)
                all_comments = []
                for vid in videos:
                    comments = self._fetch_video_comments(vid["youtube_video_id"], max_results=max_comments_per_video)
                    for c in comments:
                        c["video_id_ref"] = vid["youtube_video_id"]
                    all_comments.extend(comments)

                if videos and all_comments:
                    cleaned_comments = self._clean_comments(all_comments)
                    return {
                        "videos": videos,
                        "comments": cleaned_comments
                    }
            except Exception as e:
                logger.error(f"Error executing YouTube API calls: {e}. Falling back to mock generator.")

        # Fallback to realistic synthetic public discussion generator
        return self._generate_synthetic_youtube_data(topic, max_videos, max_comments_per_video)

    def _search_videos(self, topic: str, max_results: int = 10) -> List[Dict[str, Any]]:
        request = self.youtube_client.search().list(
            q=topic,
            part="snippet",
            type="video",
            order="relevance",
            maxResults=max_results
        )
        response = request.execute()
        videos = []
        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            vid_id = item.get("id", {}).get("videoId")
            if vid_id:
                videos.append({
                    "youtube_video_id": vid_id,
                    "title": snippet.get("title", ""),
                    "channel": snippet.get("channelTitle", ""),
                    "published_at": snippet.get("publishedAt")
                })
        return videos

    def _fetch_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        comments = []
        try:
            request = self.youtube_client.commentThreads().list(
                videoId=video_id,
                part="snippet",
                maxResults=min(max_results, 100),
                textFormat="plainText"
            )
            response = request.execute()
            for item in response.get("items", []):
                top_comment = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                comments.append({
                    "author": top_comment.get("authorDisplayName", "Anonymous"),
                    "text": top_comment.get("textDisplay", ""),
                    "published_at": top_comment.get("publishedAt")
                })
        except Exception as e:
            logger.warning(f"Could not fetch comments for video {video_id}: {e}")
        return comments

    def _clean_comments(self, comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cleans comments: removes URLs, emojis, spam, duplicates.
        """
        cleaned = []
        seen_texts = set()

        url_pattern = re.compile(r'https?://\S+|www\.\S+')
        emoji_pattern = re.compile(
            r'[\U00010000-\U0010ffff]'
            r'|[\u2600-\u27FF]'
            r'|[\u2300-\u23FF]'
            r'|[\u2B00-\u2BFF]'
            r'|[\u2000-\u206F]',
            flags=re.UNICODE
        )

        for c in comments:
            raw_text = c.get("text", "")
            # Remove URLs
            text = url_pattern.sub('', raw_text)
            # Remove Emojis
            text = emoji_pattern.sub('', text)
            # Normalize whitespace
            text = re.sub(r'\s+', ' ', text).strip()

            # Filter out spam or too short comments
            if len(text) < 5 or text.lower() in seen_texts or "check my channel" in text.lower() or "subscribe" in text.lower():
                continue

            seen_texts.add(text.lower())
            cleaned.append({
                "author": c.get("author", "Anonymous"),
                "text": text,
                "published_at": c.get("published_at"),
                "video_id_ref": c.get("video_id_ref")
            })

        return cleaned

    def _generate_synthetic_youtube_data(self, topic: str, video_count: int = 10, comments_per_video: int = 25) -> Dict[str, Any]:
        """
        Generates rich realistic YouTube videos and comments for fallback/testing mode.
        """
        channels = ["TechVision Daily", "Future Insights", "Global Economy Watch", "Veritas Forum", "Daily Debate Live", "Engineering Explained", "Policy & People"]
        
        safe_topic_prefix = re.sub(r'[^a-zA-Z0-9]', '_', topic.lower())[:6] or "sim"
        # Synthetic video generation
        videos = []
        for i in range(1, video_count + 1):
            videos.append({
                "youtube_video_id": f"yt_{safe_topic_prefix}_{i:03d}",
                "title": f"The Truth About {topic.title()}: Deep Analysis #{i}",
                "channel": random.choice(channels),
                "published_at": (datetime.utcnow() - timedelta(days=random.randint(1, 60))).isoformat()
            })

        # Synthetic comment templates for high variety public discourse
        support_templates = [
            f"I have been following {topic} for years, and the long-term benefits clearly outweigh the initial costs.",
            f"The engineering and technical foundation behind {topic} is solid. Data from recent studies proves it works.",
            f"This is a massive step forward for our community. We need to embrace {topic} faster.",
            f"Economically, {topic} makes total sense once scaling efficiencies kick in.",
            f"I was skeptical at first, but after looking at the performance numbers, I'm completely convinced."
        ]

        oppose_templates = [
            f"The hidden costs of {topic} are absurd. Nobody talks about maintenance and infrastructure failure rates.",
            f"This is driven by government mandates and corporate lobbying, not genuine consumer demand for {topic}.",
            f"From an ethical perspective, {topic} creates major inequality and ignores low-income communities.",
            f"The timeline for implementing {topic} is totally unrealistic. Grid and supply chains cannot handle it.",
            f"Safety concerns around {topic} are being swept under the rug. I won't support this."
        ]

        neutral_templates = [
            f"It's a nuanced topic. {topic} has potential, but regulatory frameworks need to be established first.",
            f"Can anyone share reliable research comparing the lifecycle costs of {topic}?",
            f"Interesting presentation. It really depends on how local municipalities handle the rollout.",
            f"I see valid arguments on both sides. We need 5 more years of data before declaring a winner."
        ]

        comments = []
        authors = ["Alex Rivera", "Devon Vance", "Sarah Chen", "Marcus Brody", "Elena Rostova", "Dr. James Vance", "TechEnthusiast99", "CryptoMinerX", "PolicyObserver", "Clara Oswald", "David K.", "Maya Lin"]

        for vid in videos:
            for _ in range(random.randint(15, comments_per_video)):
                roll = random.random()
                if roll < 0.45:
                    tmpl = random.choice(support_templates)
                elif roll < 0.80:
                    tmpl = random.choice(oppose_templates)
                else:
                    tmpl = random.choice(neutral_templates)

                comments.append({
                    "author": random.choice(authors),
                    "text": tmpl,
                    "published_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 500))).isoformat(),
                    "video_id_ref": vid["youtube_video_id"]
                })

        return {
            "videos": videos,
            "comments": comments
        }

youtube_service = YouTubeService()
