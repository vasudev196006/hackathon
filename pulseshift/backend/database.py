import logging
from sqlalchemy import create_engine
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
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
