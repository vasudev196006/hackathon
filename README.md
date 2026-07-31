# Consensus Entropy Mapper

A production-ready web application designed to collect public comments from YouTube, analyze them using an AI model (Anthropic Claude / OpenAI / NLP fallback), calculate **Shannon Entropy** and **Sentiment Volatility**, classify the state of consensus (Genuine Consensus, Fragile Consensus, False Convergence, Polarized Disagreement), and visualize everything through a modern Apple + Linear + Vercel inspired glassmorphism dashboard.

---

## Features

- **YouTube Public Discussion Harvester**: Searches YouTube Data API v3 for top videos and extracts public comment threads.
- **NLP & AI Sentiment Analysis**: Evaluates stance (`support`, `oppose`, `neutral`), sentiment score, reasoning dimension (`facts`, `values`, `process`), emotion, and confidence score.
- **Shannon Entropy Engine**: Computes exact Information Entropy $H(P) = -\sum p_i \log_2(p_i)$ to measure public opinion dispersion.
- **Volatility Dynamics**: Calculates score variance and standard deviation across public commentary.
- **Consensus State Classification**:
  - **Genuine Consensus**: Low entropy, low volatility, strong agreement.
  - **Fragile Consensus**: Superficial majority, high sentiment volatility.
  - **False Convergence**: Low stance entropy, high underlying reason divergence.
  - **Polarized Disagreement**: High entropy, high volatility, split sentiment.
- **Interactive Glassmorphic Dashboard**: Real-time KPI summary cards, interactive Chart.js visualizations (Donut, Line, Bar), AI Executive Insights, and filterable comment stream.
- **Supabase Integration**: Stores topics, videos, comments, and entropy snapshots in PostgreSQL with Supabase Realtime synchronization support.

---

## Folder Structure

```
PulseShift/
├── backend/
│   ├── .env                    # API keys and environment variables
│   ├── requirements.txt        # Python dependencies
│   ├── main.py                 # FastAPI application entrypoint
│   ├── config.py               # Settings and configuration management
│   ├── database.py             # SQLAlchemy session and engine initialization
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── youtube_service.py      # YouTube Data API harvester & text cleaner
│   ├── ai_service.py           # Anthropic Claude / OpenAI / Heuristic NLP analyzer
│   ├── entropy_engine.py       # Shannon Entropy & Volatility math engine
│   ├── classification.py       # Consensus state classification engine
│   ├── news_service.py         # NewsAPI integration with 5-min caching
│   ├── supabase_service.py     # Supabase Python client integration
│   └── routes.py               # REST API endpoints & HTML page servers
├── frontend/
│   ├── index.html              # Home page with search form and hero section
│   ├── dashboard.html          # Analytics workstation dashboard
│   ├── css/
│   │   ├── style.css           # Global design system & dark glassmorphism
│   │   └── dashboard.css       # Dashboard KPI cards, chart grids, tables
│   ├── js/
│   │   ├── main.js             # Home page search logic
│   │   ├── dashboard.js        # Dashboard state & API communication
│   │   └── charts.js           # Chart.js initialization & dynamic updates
│   └── assets/
├── schema.sql                  # PostgreSQL / Supabase table setup script
└── README.md                   # System documentation
```

---

## Installation & Setup

### 1. Requirements
- Python 3.12+
- `pip` or virtual environment manager
- (Optional) Supabase Account & PostgreSQL Database
- (Optional) YouTube Data API v3 Key
- (Optional) Anthropic API Key or OpenAI API Key

> **Note**: The application is built with automatic fallback modes. If API keys or Supabase credentials are not supplied in `.env`, it automatically uses heuristic NLP classification and realistic synthetic YouTube data generation so you can immediately test and run out-of-the-box!

---

### 2. Install Python Dependencies

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

---

### 3. Database Setup (Supabase / PostgreSQL)

Run the SQL script provided in `schema.sql` inside your Supabase SQL Editor or PostgreSQL instance:

```sql
-- Creates topics, videos, comments, and entropy_snapshots tables
\i schema.sql
```

---

### 4. Configure Environment Variables (`backend/.env`)

Edit `backend/.env` with your API keys:

```env
YOUTUBE_API_KEY=your_youtube_api_key_here
SUPABASE_URL=https://your-supabase-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
NEWS_API_KEY=your_news_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/consensus_db
```

---

### 5. Running the Backend Server

Start the Uvicorn ASGI server from the project root:

```bash
# From workspace root directory:
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### 6. Accessing the Frontend

Open your web browser and navigate to:
- **Home Page**: [http://localhost:8000/](http://localhost:8000/)
- **Live Workstation Dashboard**: [http://localhost:8000/dashboard](http://localhost:8000/dashboard)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves home page (`index.html`) |
| `GET` | `/dashboard` | Serves workstation dashboard (`dashboard.html`) |
| `POST` | `/analyze` | Triggers YouTube search, AI analysis, entropy math, and DB storage |
| `GET` | `/topics` | Returns list of all analyzed topics |
| `GET` | `/topic/{id}` | Returns metrics, snapshots, and comments for single topic |
| `GET` | `/comments/{topic_id}` | Returns detailed analyzed comments for topic |
| `GET` | `/entropy/{topic_id}` | Returns historical entropy & volatility snapshots |
| `GET` | `/news?q=<keyword>` | Returns clean JSON news articles using NewsAPI |

---

## License & Author

Developed with Python FastAPI, Supabase, Chart.js, and Anthropic Claude.
