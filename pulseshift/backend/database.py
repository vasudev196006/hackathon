import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from .config import settings
from .models import Base

logger = logging.getLogger(__name__)

DB_URL = settings.DATABASE_URL.strip() if settings.DATABASE_URL else ""

if settings.ENVIRONMENT == "production":
    if not DB_URL or "[YOUR-PASSWORD]" in DB_URL or "YOUR-PASSWORD" in DB_URL:
        raise ValueError(
            "Production Database Error: A valid DATABASE_URL must be specified in the environment variables "
            "when running in production. Fallback to SQLite is disabled."
        )
else:
    if not DB_URL or "[YOUR-PASSWORD]" in DB_URL or "YOUR-PASSWORD" in DB_URL:
        DB_URL = "sqlite:///./consensus_entropy.db"

import urllib.parse

if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

DB_URL = DB_URL.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")

# Auto-encode special characters (like @, #) in the password portion of the database URL
if "://" in DB_URL:
    protocol, rest = DB_URL.split("://", 1)
    if "@" in rest:
        at_idx = rest.rfind("@")
        creds = rest[:at_idx]
        host_port_db = rest[at_idx+1:]
        if ":" in creds:
            colon_idx = creds.find(":")
            username = creds[:colon_idx]
            password = creds[colon_idx+1:]
            # Unquote and quote to safely encode password special characters
            decoded_password = urllib.parse.unquote(password)
            encoded_password = urllib.parse.quote(decoded_password)
            DB_URL = f"{protocol}://{username}:{encoded_password}@{host_port_db}"

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(
    DB_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
        
        # Self-healing database migration for missing columns
        inspector = inspect(engine)
        if "topics" in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns("topics")]
            missing_cols = []
            
            # search_query
            if "search_query" not in columns:
                if engine.url.drivername.startswith("sqlite"):
                    missing_cols.append(("search_query", "TEXT"))
                else:
                    missing_cols.append(("search_query", "VARCHAR(255)"))
            
            # entropy_score
            if "entropy_score" not in columns:
                if engine.url.drivername.startswith("sqlite"):
                    missing_cols.append(("entropy_score", "FLOAT"))
                else:
                    missing_cols.append(("entropy_score", "DOUBLE PRECISION"))
            
            # volatility_score
            if "volatility_score" not in columns:
                if engine.url.drivername.startswith("sqlite"):
                    missing_cols.append(("volatility_score", "FLOAT"))
                else:
                    missing_cols.append(("volatility_score", "DOUBLE PRECISION"))
                    
            # consensus_status
            if "consensus_status" not in columns:
                if engine.url.drivername.startswith("sqlite"):
                    missing_cols.append(("consensus_status", "TEXT"))
                else:
                    missing_cols.append(("consensus_status", "VARCHAR(100)"))
            
            if missing_cols:
                logger.info(f"Adding missing columns to 'topics' table: {[c[0] for c in missing_cols]}...")
                with engine.begin() as conn:
                    for col_name, col_type in missing_cols:
                        conn.execute(text(f"ALTER TABLE topics ADD COLUMN {col_name} {col_type}"))
                logger.info("Successfully added missing columns to 'topics' table.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
