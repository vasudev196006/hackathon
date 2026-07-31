import uuid
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from .database import get_db
from .models import TopicModel, VideoModel, CommentModel, EntropySnapshotModel, NewsArticleModel

from .schemas import TopicResponse, CommentResponse, EntropySnapshotResponse, DashboardMetrics, AnalyzeRequest, ChatRequest, ChatResponse
from .youtube_service import youtube_service
from .ai_service import ai_service
from .entropy_engine import EntropyEngine
from .classification import ConsensusClassifier
from .supabase_service import supabase_service
from .news_service import news_service, NewsServiceError
from .gemini_service import gemini_service
from .openrouter_service import openrouter_service

logger = logging.getLogger(__name__)

router = APIRouter()

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

@router.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse(content="<h1>PulseShift API is running</h1>")

@router.get("/dashboard", response_class=HTMLResponse)
def serve_dashboard():
    dashboard_file = FRONTEND_DIR / "dashboard.html"
    if dashboard_file.exists():
        return FileResponse(dashboard_file)
    return HTMLResponse(content="<h1>Dashboard file not found</h1>")

@router.post("/analyze", response_model=DashboardMetrics)
async def analyze_topic(req: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    Main pipeline:
    1. Search YouTube for topic -> Top 10 videos
    2. Download comments per video -> Clean comments
    3. Call AI Service to get stance, score, reason, emotion, confidence
    4. Store in database (and Supabase)
    5. Calculate Shannon Entropy & Volatility
    6. Classify Consensus state
    7. Return full metrics summary payload
    """
    topic_title = req.topic.strip()
    if not topic_title:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")

    logger.info(f"Starting analysis for topic: '{topic_title}'")

    # Step 1: Create or fetch topic record in DB
    existing_topic = db.query(TopicModel).filter(TopicModel.title.ilike(topic_title)).first()
    if existing_topic:
        topic_record = existing_topic
    else:
        topic_record = TopicModel(title=topic_title)
        db.add(topic_record)
        db.commit()
        db.refresh(topic_record)

    topic_id_str = str(topic_record.id)

    if not existing_topic:
        # Mirror to Supabase if active
        supabase_service.insert_topic(topic_title, topic_id=topic_id_str)

    # Step 2: Fetch YouTube videos & comments
    yt_data = youtube_service.fetch_videos_and_comments(topic_title, max_videos=10, max_comments_per_video=25)
    videos_raw = yt_data.get("videos", [])
    comments_raw = yt_data.get("comments", [])

    # Map video_id_ref to database video objects
    yt_id_to_db_id = {}
    db_videos = []
    for v in videos_raw:
        v_model = VideoModel(
            topic_id=topic_record.id,
            youtube_video_id=v["youtube_video_id"],
            title=v["title"],
            channel=v.get("channel", ""),
            published_at=None
        )
        db.add(v_model)
        db.commit()
        db.refresh(v_model)
        yt_id_to_db_id[v["youtube_video_id"]] = v_model.id
        db_videos.append(v_model)

    # Step 3: Run AI analysis on cleaned comments
    analyzed_comments = ai_service.analyze_batch(comments_raw, topic_title)

    # Step 4: Persist comments in database
    db_comments = []
    for c in analyzed_comments:
        vid_ref = c.get("video_id_ref")
        v_uuid = yt_id_to_db_id.get(vid_ref) if vid_ref else None

        c_model = CommentModel(
            topic_id=topic_record.id,
            video_id=v_uuid,
            author=c.get("author", "Anonymous"),
            text=c.get("text", ""),
            published_at=None,
            stance=c.get("stance", "neutral"),
            score=c.get("score", 0.0),
            reason=c.get("reason", "facts"),
            emotion=c.get("emotion", "Neutral"),
            confidence=c.get("confidence", 0.8)
        )
        db.add(c_model)
        db_comments.append(c_model)

    db.commit()

    # Step 5: Calculate Shannon Entropy & Volatility
    metrics = EntropyEngine.compute_full_metrics(analyzed_comments)

    # Step 6: Classify Consensus state
    classification_state = ConsensusClassifier.classify(
        entropy=metrics["entropy"],
        volatility=metrics["volatility"],
        support_pct=metrics["support_pct"],
        oppose_pct=metrics["oppose_pct"],
        neutral_pct=metrics["neutral_pct"],
        reason_divergence=metrics["reason_divergence"]
    )

    # Step 7: Store Entropy Snapshot
    snapshot = EntropySnapshotModel(
        topic_id=topic_record.id,
        entropy=metrics["entropy"],
        volatility=metrics["volatility"],
        classification=classification_state,
        created_at=datetime.utcnow()
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    # Mirror snapshot to Supabase Realtime table if active
    supabase_service.insert_entropy_snapshot(
        topic_id=topic_id_str,
        entropy=metrics["entropy"],
        volatility=metrics["volatility"],
        classification=classification_state,
        snapshot_id=str(snapshot.id)
    )

    # Step 8: Generate AI Executive Summary text
    ai_summary_text = ConsensusClassifier.generate_ai_insight_summary(
        topic_title=topic_title,
        total_comments=metrics["total_comments"],
        support_pct=metrics["support_pct"],
        oppose_pct=metrics["oppose_pct"],
        neutral_pct=metrics["neutral_pct"],
        entropy=metrics["entropy"],
        volatility=metrics["volatility"],
        classification=classification_state,
        reasons_breakdown=metrics["reasons_breakdown"]
    )

    # Fetch all historical snapshots for time series chart
    snapshots = db.query(EntropySnapshotModel).filter(EntropySnapshotModel.topic_id == topic_record.id).order_by(EntropySnapshotModel.created_at.asc()).all()

    # Step 9: Fetch and persist related news articles in Database
    try:
        raw_news = await news_service.searchNews(topic_title)
    except Exception as exc:
        logger.warning(f"Could not fetch news articles for '{topic_title}': {exc}")
        raw_news = []

    # Clear previous news records for this topic
    db.query(NewsArticleModel).filter(NewsArticleModel.topic_id == topic_record.id).delete()
    
    db_news_records = []
    supabase_news_payload = []
    for art in raw_news:
        n_model = NewsArticleModel(
            topic_id=topic_record.id,
            title=art.get("title", "Untitled"),
            description=art.get("description", ""),
            source=art.get("source", "Unknown"),
            author=art.get("author", "Unknown"),
            published_at=art.get("publishedAt", ""),
            url=art.get("url", ""),
            url_to_image=art.get("urlToImage", ""),
            content=art.get("content", "")
        )
        db.add(n_model)
        db_news_records.append(n_model)
        supabase_news_payload.append({
            "topic_id": str(topic_record.id),
            "title": art.get("title", "Untitled"),
            "description": art.get("description", ""),
            "source": art.get("source", "Unknown"),
            "author": art.get("author", "Unknown"),
            "published_at": art.get("publishedAt", ""),
            "url": art.get("url", ""),
            "url_to_image": art.get("urlToImage", "")
        })

    db.commit()

    # Mirror to Supabase if active
    supabase_service.insert_news_articles(supabase_news_payload)

    news_payload = [
        {
            "title": n.title,
            "description": n.description or "",
            "source": n.source or "Unknown",
            "author": n.author or "Unknown",
            "publishedAt": n.published_at or "",
            "url": n.url or "",
            "urlToImage": n.url_to_image or "",
            "content": n.content or ""
        } for n in db_news_records
    ]

    return DashboardMetrics(
        topic=TopicResponse.model_validate(topic_record),
        total_videos=len(db_videos),
        total_comments=metrics["total_comments"],
        support_pct=metrics["support_pct"],
        oppose_pct=metrics["oppose_pct"],
        neutral_pct=metrics["neutral_pct"],
        avg_confidence=metrics["avg_confidence"],
        entropy=metrics["entropy"],
        volatility=metrics["volatility"],
        classification=classification_state,
        reasons_breakdown=metrics["reasons_breakdown"],
        ai_summary=ai_summary_text,
        latest_snapshots=[EntropySnapshotResponse.model_validate(s) for s in snapshots],
        top_comments=[CommentResponse.model_validate(c) for c in db_comments[:50]],
        news_articles=news_payload
    )

@router.get("/topics", response_model=List[TopicResponse])
def get_topics(db: Session = Depends(get_db)):
    topics = db.query(TopicModel).order_by(TopicModel.created_at.desc()).all()
    return topics

@router.get("/topic/{topic_id}", response_model=DashboardMetrics)
async def get_topic_details(topic_id: uuid.UUID, db: Session = Depends(get_db)):
    topic_record = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
    if not topic_record:
        raise HTTPException(status_code=404, detail="Topic not found")

    comments = db.query(CommentModel).filter(CommentModel.topic_id == topic_id).all()
    videos_count = db.query(VideoModel).filter(VideoModel.topic_id == topic_id).count()
    snapshots = db.query(EntropySnapshotModel).filter(EntropySnapshotModel.topic_id == topic_id).order_by(EntropySnapshotModel.created_at.asc()).all()
    stored_news = db.query(NewsArticleModel).filter(NewsArticleModel.topic_id == topic_id).all()

    c_dicts = [{
        "stance": c.stance,
        "score": c.score,
        "reason": c.reason,
        "emotion": c.emotion,
        "confidence": c.confidence
    } for c in comments]

    metrics = EntropyEngine.compute_full_metrics(c_dicts)

    latest_class = snapshots[-1].classification if snapshots else ConsensusClassifier.classify(
        metrics["entropy"], metrics["volatility"], metrics["support_pct"], metrics["oppose_pct"], metrics["neutral_pct"], metrics["reason_divergence"]
    )

    ai_summary_text = ConsensusClassifier.generate_ai_insight_summary(
        topic_title=topic_record.title,
        total_comments=metrics["total_comments"],
        support_pct=metrics["support_pct"],
        oppose_pct=metrics["oppose_pct"],
        neutral_pct=metrics["neutral_pct"],
        entropy=metrics["entropy"],
        volatility=metrics["volatility"],
        classification=latest_class,
        reasons_breakdown=metrics["reasons_breakdown"]
    )

    if stored_news:
        news_payload = [
            {
                "title": n.title,
                "description": n.description or "",
                "source": n.source or "Unknown",
                "author": n.author or "Unknown",
                "publishedAt": n.published_at or "",
                "url": n.url or "",
                "urlToImage": n.url_to_image or "",
                "content": n.content or ""
            } for n in stored_news
        ]
    else:
        try:
            raw_news = await news_service.searchNews(topic_record.title)
            db_news_records = []
            for art in raw_news:
                n_model = NewsArticleModel(
                    topic_id=topic_record.id,
                    title=art.get("title", "Untitled"),
                    description=art.get("description", ""),
                    source=art.get("source", "Unknown"),
                    author=art.get("author", "Unknown"),
                    published_at=art.get("publishedAt", ""),
                    url=art.get("url", ""),
                    url_to_image=art.get("urlToImage", ""),
                    content=art.get("content", "")
                )
                db.add(n_model)
                db_news_records.append(n_model)
            db.commit()
            news_payload = [
                {
                    "title": n.title,
                    "description": n.description or "",
                    "source": n.source or "Unknown",
                    "author": n.author or "Unknown",
                    "publishedAt": n.published_at or "",
                    "url": n.url or "",
                    "urlToImage": n.url_to_image or "",
                    "content": n.content or ""
                } for n in db_news_records
            ]
        except Exception as exc:
            logger.warning(f"Could not fetch news articles for '{topic_record.title}': {exc}")
            news_payload = []

    return DashboardMetrics(
        topic=TopicResponse.model_validate(topic_record),
        total_videos=videos_count,
        total_comments=metrics["total_comments"],
        support_pct=metrics["support_pct"],
        oppose_pct=metrics["oppose_pct"],
        neutral_pct=metrics["neutral_pct"],
        avg_confidence=metrics["avg_confidence"],
        entropy=metrics["entropy"],
        volatility=metrics["volatility"],
        classification=latest_class,
        reasons_breakdown=metrics["reasons_breakdown"],
        ai_summary=ai_summary_text,
        latest_snapshots=[EntropySnapshotResponse.model_validate(s) for s in snapshots],
        top_comments=[CommentResponse.model_validate(c) for c in comments[:50]],
        news_articles=news_payload
    )

@router.get("/comments/{topic_id}", response_model=List[CommentResponse])
def get_topic_comments(topic_id: uuid.UUID, db: Session = Depends(get_db)):
    comments = db.query(CommentModel).filter(CommentModel.topic_id == topic_id).order_by(CommentModel.created_at.desc()).all()
    return comments

@router.get("/entropy/{topic_id}", response_model=List[EntropySnapshotResponse])
def get_topic_entropy_snapshots(topic_id: uuid.UUID, db: Session = Depends(get_db)):
    snapshots = db.query(EntropySnapshotModel).filter(EntropySnapshotModel.topic_id == topic_id).order_by(EntropySnapshotModel.created_at.asc()).all()
    return snapshots

@router.get("/news")
async def search_news(q: Optional[str] = None, category: Optional[str] = None, country: Optional[str] = None, event: Optional[str] = None):
    """
    GET /news?q=<keyword>&category=<cat>&country=<cc>&event=<evt>
    Flexible news endpoint supporting searchNews, getTopHeadlines, searchByCategory, and searchEvent.
    Returns clean JSON array of normalized articles.
    """
    try:
        if event and event.strip():
            return await news_service.searchEvent(event.strip())
        elif category and category.strip():
            return await news_service.searchByCategory(category.strip())
        elif country and country.strip():
            return await news_service.getTopHeadlines(country.strip())
        elif q and q.strip():
            return await news_service.searchNews(q.strip())
    except NewsServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in /news endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
