-- Consensus Entropy Mapper Database Schema for Supabase / PostgreSQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 1. Topics Table
CREATE TABLE IF NOT EXISTS topics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    search_query VARCHAR(255),
    entropy_score DOUBLE PRECISION,
    volatility_score DOUBLE PRECISION,
    consensus_status VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
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
    author_name VARCHAR(255),
    comment_text TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    stance VARCHAR(20) CHECK (stance IN ('support', 'oppose', 'neutral')),
    score DOUBLE PRECISION DEFAULT 0.0,
    reason VARCHAR(50) CHECK (reason IN ('facts', 'values', 'process')),
    emotion VARCHAR(50),
    confidence DOUBLE PRECISION DEFAULT 0.0,
    entropy_weight DOUBLE PRECISION DEFAULT 1.0,
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

-- 5. News Articles Table
CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id UUID REFERENCES topics(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    snippet TEXT,
    source_name VARCHAR(255),
    author VARCHAR(255),
    published_at TIMESTAMPTZ,
    url TEXT,
    image_url TEXT,
    content TEXT,
    stance VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 6. Chatbot Logs Table
CREATE TABLE IF NOT EXISTS chatbot_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id VARCHAR(255),
    user_query TEXT,
    ai_response TEXT,
    model_used VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance & lookups
CREATE INDEX IF NOT EXISTS idx_topics_title ON topics(title);
CREATE INDEX IF NOT EXISTS idx_news_topic_id ON news_articles(topic_id);
CREATE INDEX IF NOT EXISTS idx_comments_topic_id ON comments(topic_id);
CREATE INDEX IF NOT EXISTS idx_news_title_trgm ON news_articles USING gin (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_topic ON videos(topic_id);
CREATE INDEX IF NOT EXISTS idx_comments_stance ON comments(stance);
CREATE INDEX IF NOT EXISTS idx_entropy_snapshots_topic ON entropy_snapshots(topic_id);
