import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings
from models import Base

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

if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

DB_URL = DB_URL.replace("?pgbouncer=true", "").replace("&pgbouncer=true", "")

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
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
