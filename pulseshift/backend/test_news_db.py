import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
import uuid
from database import SessionLocal, init_db
from models import TopicModel, NewsArticleModel
from news_service import news_service

def test_db_persistence():
    print("=== Initializing Database ===")
    init_db()
    
    db = SessionLocal()
    try:
        # Create a test topic
        topic = TopicModel(title="Test Real-Time News Topic")
        db.add(topic)
        db.commit()
        db.refresh(topic)
        print(f"Created topic: '{topic.title}' with ID: {topic.id}")

        # Fetch articles
        articles = asyncio.run(news_service.searchNews(topic.title))
        print(f"Fetched {len(articles)} articles from NewsService.")

        # Persist articles in DB
        for art in articles:
            model = NewsArticleModel(
                topic_id=topic.id,
                title=art.get("title", "Untitled"),
                description=art.get("description", ""),
                source=art.get("source", "Unknown"),
                author=art.get("author", "Unknown"),
                published_at=art.get("publishedAt", ""),
                url=art.get("url", ""),
                url_to_image=art.get("urlToImage", ""),
                content=art.get("content", "")
            )
            db.add(model)
        db.commit()

        # Query database for news_articles for this topic
        saved_articles = db.query(NewsArticleModel).filter(NewsArticleModel.topic_id == topic.id).all()
        print(f"Successfully retrieved {len(saved_articles)} persisted news_articles from database:")
        for idx, item in enumerate(saved_articles[:3]):
            print(f"  [{idx+1}] Title: {item.title[:50]}...")
            print(f"       Source: {item.source} | Image: {item.url_to_image[:60]}...")

        # Clean up test topic
        db.delete(topic)
        db.commit()
        print("\nTest topic and cascading news_articles deleted cleanly.")

    finally:
        db.close()

if __name__ == "__main__":
    test_db_persistence()
