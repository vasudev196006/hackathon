from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

# Topic Schemas
class TopicCreate(BaseModel):
    title: str = Field(..., description="Topic query to search on YouTube")

class TopicResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

# Video Schemas
class VideoResponse(BaseModel):
    id: UUID
    topic_id: UUID
    youtube_video_id: str
    title: str
    channel: Optional[str] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# AI Analysis Result Schema
class CommentAIAnalysis(BaseModel):
    stance: str  # support, oppose, neutral
    score: float  # -1.0 to 1.0 or 0.0 to 1.0
    reason: str  # facts, values, process
    emotion: str
    confidence: float

# Comment Schemas
class CommentResponse(BaseModel):
    id: UUID
    topic_id: UUID
    video_id: Optional[UUID] = None
    author: Optional[str] = None
    text: str
    published_at: Optional[datetime] = None
    stance: Optional[str] = None
    score: Optional[float] = 0.0
    reason: Optional[str] = None
    emotion: Optional[str] = None
    confidence: Optional[float] = 0.0
    created_at: datetime

    class Config:
        from_attributes = True

# Entropy Snapshot Schemas
class EntropySnapshotResponse(BaseModel):
    id: UUID
    topic_id: UUID
    entropy: float
    volatility: float
    classification: str
    created_at: datetime

    class Config:
        from_attributes = True

class NewsArticleResponse(BaseModel):
    title: str
    description: Optional[str] = ""
    source: Optional[str] = "Unknown"
    author: Optional[str] = "Unknown"
    publishedAt: Optional[str] = ""
    url: Optional[str] = ""
    urlToImage: Optional[str] = ""
    content: Optional[str] = ""

# Dashboard Summary Schema
class DashboardMetrics(BaseModel):
    topic: TopicResponse
    total_videos: int
    total_comments: int
    support_pct: float
    oppose_pct: float
    neutral_pct: float
    avg_confidence: float
    entropy: float
    volatility: float
    classification: str
    reasons_breakdown: dict  # {"facts": int, "values": int, "process": int}
    ai_summary: str
    latest_snapshots: List[EntropySnapshotResponse]
    top_comments: List[CommentResponse]
    news_articles: List[NewsArticleResponse] = []

class AnalyzeRequest(BaseModel):
    topic: str

class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or prompt string")
    topic_id: Optional[str] = Field(None, description="Optional topic UUID string")
    topic_title: Optional[str] = Field(None, description="Optional topic title string")
    history: Optional[List[dict]] = Field(default_factory=list, description="Optional list of past chat messages")
    context: Optional[dict] = Field(default_factory=dict, description="Optional context dictionary")
    conversation_id: Optional[str] = Field(None, description="Unique session conversation identifier")

class ChatResponse(BaseModel):
    reply: str = Field(..., description="Gemini AI generated reply text (supports markdown)")
    topic: Optional[str] = Field(None, description="Associated topic title")
