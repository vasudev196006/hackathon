-- Consensus Entropy Mapper Database Schema for Supabase / PostgreSQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Topics Table
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 2. Videos Table
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    youtube_video_id VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    channel VARCHAR(255),
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Comments Table
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    video_id UUID REFERENCES videos(id) ON DELETE SET NULL,
    author VARCHAR(255),
    text TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    stance VARCHAR(20) CHECK (stance IN ('support', 'oppose', 'neutral')),
    score DOUBLE PRECISION DEFAULT 0.0,
    reason VARCHAR(50) CHECK (reason IN ('facts', 'values', 'process')),
    emotion VARCHAR(50),
    confidence DOUBLE PRECISION DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Entropy Snapshots Table
CREATE TABLE IF NOT EXISTS entropy_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    entropy DOUBLE PRECISION NOT NULL,
    volatility DOUBLE PRECISION NOT NULL,
    classification VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_videos_topic ON videos(topic_id);
CREATE INDEX IF NOT EXISTS idx_comments_topic ON comments(topic_id);
CREATE INDEX IF NOT EXISTS idx_comments_stance ON comments(stance);
CREATE INDEX IF NOT EXISTS idx_entropy_snapshots_topic ON entropy_snapshots(topic_id);
