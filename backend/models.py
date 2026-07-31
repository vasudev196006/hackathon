import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class TopicModel(Base):
    __tablename__ = "topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    videos = relationship("VideoModel", back_populates="topic", cascade="all, delete-orphan")
    comments = relationship("CommentModel", back_populates="topic", cascade="all, delete-orphan")
    entropy_snapshots = relationship("EntropySnapshotModel", back_populates="topic", cascade="all, delete-orphan")


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


class CommentModel(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="SET NULL"), nullable=True)
    author = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    published_at = Column(DateTime, nullable=True)
    stance = Column(String(20), nullable=True) # support, oppose, neutral
    score = Column(Float, default=0.0)
    reason = Column(String(50), nullable=True) # facts, values, process
    emotion = Column(String(50), nullable=True)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    topic = relationship("TopicModel", back_populates="comments")
    video = relationship("VideoModel", back_populates="comments")


class EntropySnapshotModel(Base):
    __tablename__ = "entropy_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    entropy = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    classification = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    topic = relationship("TopicModel", back_populates="entropy_snapshots")
