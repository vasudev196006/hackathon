import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship, validates

Base = declarative_base()

def parse_date(date_str) -> Optional[datetime]:
    if not date_str:
        return None
    if isinstance(date_str, datetime):
        return date_str
    date_str = str(date_str).strip()
    try:
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        return datetime.fromisoformat(date_str)
    except Exception:
        try:
            from dateutil.parser import parse as date_parse
            return date_parse(date_str)
        except Exception:
            return datetime.utcnow()

class TopicModel(Base):
    __tablename__ = "topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    search_query = Column(String(255), nullable=True)
    entropy_score = Column(Float, nullable=True)
    volatility_score = Column(Float, nullable=True)
    consensus_status = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    videos = relationship("VideoModel", back_populates="topic", cascade="all, delete-orphan")
    comments = relationship("CommentModel", back_populates="topic", cascade="all, delete-orphan")
    entropy_snapshots = relationship("EntropySnapshotModel", back_populates="topic", cascade="all, delete-orphan")
    news_articles = relationship("NewsArticleModel", back_populates="topic", cascade="all, delete-orphan")


class NewsArticleModel(Base):
    __tablename__ = "news_articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column("snippet", Text, nullable=True)
    source = Column("source_name", String(255), nullable=True)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True)
    url = Column(Text, nullable=True)
    url_to_image = Column("image_url", Text, nullable=True)
    content = Column(Text, nullable=True)
    stance = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    topic = relationship("TopicModel", back_populates="news_articles")

    @validates('published_at')
    def validate_published_at(self, key, value):
        return parse_date(value)


class VideoModel(Base):
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    youtube_video_id = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    channel = Column(String(255), nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    topic = relationship("TopicModel", back_populates="videos")
    comments = relationship("CommentModel", back_populates="video")

    @validates('published_at')
    def validate_published_at(self, key, value):
        return parse_date(value)


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="SET NULL"), nullable=True)
    author = Column("author_name", String(255), nullable=True)
    text = Column("comment_text", Text, nullable=False)
    published_at = Column(DateTime, nullable=True)
    stance = Column(String(20), nullable=True) # support, oppose, neutral
    score = Column(Float, default=0.0)
    reason = Column(String(50), nullable=True) # facts, values, process
    emotion = Column(String(50), nullable=True)
    confidence = Column(Float, default=0.0)
    entropy_weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    topic = relationship("TopicModel", back_populates="comments")
    video = relationship("VideoModel", back_populates="comments")

    @validates('published_at')
    def validate_published_at(self, key, value):
        return parse_date(value)


class EntropySnapshotModel(Base):
    __tablename__ = "entropy_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    entropy = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    classification = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    topic = relationship("TopicModel", back_populates="entropy_snapshots")


class ChatbotLogModel(Base):
    __tablename__ = "chatbot_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(String(255), nullable=True)
    user_query = Column(Text, nullable=True)
    ai_response = Column(Text, nullable=True)
    model_used = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
