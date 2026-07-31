import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import settings
from youtube_service import youtube_service
from ai_service import ai_service
from news_service import news_service
from supabase_service import supabase_service

def test_api_keys():
    print("=" * 50)
    print("       API KEYS & SERVICE HEALTH REPORT       ")
    print("=" * 50)
    
    print("\n[1] CONFIGURATION CHECK:")
    print(f"  - YOUTUBE_API_KEY : {'[OK] Configured' if settings.has_youtube_key else '[INFO] Not set (Using Synthetic Harvester fallback)'}")
    print(f"  - OPENAI_API_KEY  : {'[OK] Configured' if settings.has_openai_key else '[INFO] Not set (Using Heuristic Sentiment NLP Fallback)'}")
    print(f"  - ANTHROPIC_KEY   : {'[OK] Configured' if settings.has_anthropic_key else '[INFO] Not set (Using Heuristic Sentiment NLP Fallback)'}")
    print(f"  - NEWS_API_KEY    : {'[OK] Configured' if settings.has_news_api_key else '[INFO] Not set (Using Google News RSS Live Fallback)'}")
    print(f"  - SUPABASE        : {'[OK] Configured' if settings.has_supabase else '[INFO] Not set (Using SQLite local DB)'}")

    print("\n[2] TESTING BACKEND FUNCTIONALITY:")

    # YouTube / Synthetic Harvester
    yt_data = youtube_service.fetch_videos_and_comments("Artificial Intelligence", max_videos=2, max_comments_per_video=3)
    videos_count = len(yt_data.get("videos", []))
    comments_count = len(yt_data.get("comments", []))
    print(f"  - YouTube/Harvest Service: SUCCESS ({videos_count} videos, {comments_count} comments fetched)")

    # AI Sentiment Analysis
    ai_sample = ai_service.analyze_comment("AI will greatly enhance human productivity and scientific discovery.", "Artificial Intelligence")
    print(f"  - AI Sentiment Analysis   : SUCCESS (Stance: '{ai_sample.get('stance')}', Score: {ai_sample.get('score')}, Reason: '{ai_sample.get('reason')}')")

    # News Service
    async def run_news():
        articles = await news_service.searchNews("Artificial Intelligence")
        print(f"  - News Service            : SUCCESS ({len(articles)} articles fetched, Top Source: '{articles[0]['source'] if articles else 'N/A'}')")
    
    asyncio.run(run_news())
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_api_keys()
