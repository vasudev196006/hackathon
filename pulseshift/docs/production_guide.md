# 🚀 PulseShift — Production-Ready Database & Deployment Guide

This guide provides an end-to-end blueprint for deploying **PulseShift** and its **Supabase PostgreSQL database** to production with high availability, security, scalability, and zero downtime.

---

## 🗄️ 1. Database Architecture & Schema Specification

PulseShift uses **PostgreSQL on Supabase** with fallback to local SQLite for development.

### Core Relational Schema Diagram

```mermaid
erDiagram
    TOPICS ||--o{ NEWS_ARTICLES : contains
    TOPICS ||--o{ COMMENTS : contains
    TOPICS ||--o{ CHATBOT_LOGS : references

    TOPICS {
        uuid id PK
        string title
        string search_query
        float entropy_score
        float volatility_score
        string consensus_status
        timestamp created_at
        timestamp updated_at
    }

    NEWS_ARTICLES {
        uuid id PK
        uuid topic_id FK
        string title
        string source_name
        string url
        string image_url
        text snippet
        string stance
        timestamp published_at
    }

    COMMENTS {
        uuid id PK
        uuid topic_id FK
        string video_id
        string author_name
        text comment_text
        string stance
        float entropy_weight
        timestamp created_at
    }

    CHATBOT_LOGS {
        uuid id PK
        string conversation_id
        text user_query
        text ai_response
        string model_used
        timestamp created_at
    }
```

---

## 🛠️ 2. PostgreSQL Connection Modes & Poolers

Supabase provides two distinct PostgreSQL endpoints:

### A. Transaction-Mode Pooler (Port 6543) — *For High-Concurrency Production App Services*
- **URL**: `postgresql://postgres.vdbafdrxznkiwcxbubsv:[YOUR-PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:6543/postgres`
- **Use Case**: Serverless functions, FastAPI worker processes, web APIs.
- **Benefits**: Handles thousands of concurrent incoming connections with minimal memory overhead via PgBouncer.

### B. Direct / Session-Mode Pooler (Port 5432) — *For Migrations & Schema Changes*
- **URL**: `postgresql://postgres.vdbafdrxznkiwcxbubsv:[YOUR-PASSWORD]@aws-1-ap-south-1.pooler.supabase.com:5432/postgres`
- **Use Case**: Alembic migrations, DDL statements (`CREATE TABLE`, `ALTER TABLE`), database seeding.
- **Benefits**: Supports prepared statements and full session state.

---

## 🔒 3. Production Environment Configuration (`.env`)

In production environments (Render, AWS ECS, GCP Cloud Run, Heroku), inject these environment variables into your secrets manager:

```env
# Server Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
SECRET_KEY=your_production_jwt_secret_key_here

# Supabase Production Database
SUPABASE_URL=https://vdbafdrxznkiwcxbubsv.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_6Hjf9x5FufrtDsoU3P0QYw_U8UxqqfK
SUPABASE_SECRET_KEY=sb_secret_zYbSrcvbH3tv2BOm0Hnj7A_mhVR8ZdO
DATABASE_URL=postgresql://postgres.vdbafdrxznkiwcxbubsv:YOUR_REAL_PASSWORD@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
DIRECT_URL=postgresql://postgres.vdbafdrxznkiwcxbubsv:YOUR_REAL_PASSWORD@aws-1-ap-south-1.pooler.supabase.com:5432/postgres

# AI Services & External APIs
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=poolside/laguna-s-2.1:free
NEWS_API_KEY=your_news_api_key
YOUTUBE_API_KEY=your_youtube_api_key
GEMINI_API_KEY=your_gemini_api_key
```

---

## ⚡ 4. Database Indexing & Performance Optimization

To ensure sub-50ms query response times under high load, execute these PostgreSQL SQL indexes in Supabase SQL Editor:

```sql
-- Index for fast topic lookups by title
CREATE INDEX IF NOT EXISTS idx_topics_title ON topics(title);

-- Foreign key indexes for news articles & comments
CREATE INDEX IF NOT EXISTS idx_news_topic_id ON news_articles(topic_id);
CREATE INDEX IF NOT EXISTS idx_comments_topic_id ON comments(topic_id);

-- Full-text title index for News search
CREATE INDEX IF NOT EXISTS idx_news_title_trgm ON news_articles USING gin (title gin_trgm_ops);

-- Index for ordering news by published date
CREATE INDEX IF NOT EXISTS idx_news_published ON news_articles(published_at DESC);
```

---

## 🐳 5. Production Containerization (`Dockerfile`)

Create a lightweight, multi-stage `Dockerfile` for backend deployment:

```dockerfile
# Stage 1: Build & Dependencies
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production Runtime
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . /app

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "backend.main:app", "--bind", "0.0.0.0:8000"]
```

---

## 🛡️ 6. Production Security & Health Check

### A. CORS Configuration (`backend/main.py`)
Ensure CORS origins are restricted to your verified production domains:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pulseshiftmap.netlify.app",
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

### B. Health Check Endpoint (`/health`)
Monitors DB connection health for cloud load balancers:

```python
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "unhealthy", "error": str(e)})
```

---

## 📋 7. Pre-Flight Launch Checklist

- [x] **Supabase Project Active**: `vdbafdrxznkiwcxbubsv.supabase.co`
- [x] **API Credentials Configured**: Publishable key & Secret key injected into `.env`.
- [x] **Database Fallback Verified**: Automatic graceful fallback to SQLite if DB password is omitted.
- [x] **Rate Limiting Shield**: Fast-break logic on HTTP 429 quota exhaustion in OpenRouter and Gemini services.
- [x] **Liquid Glass UI System**: Pure neutral glassmorphism UI synced across landing page, workstation, and chatbot widget.
- [ ] **DB Password Injected**: Replace `[YOUR-PASSWORD]` in `DATABASE_URL` with your actual Supabase DB password when deploying to live cloud servers.
