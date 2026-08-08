import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# .env file se variables load karein
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Check karein ki URL environment me set hai ya nahi
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL missing hai! Please check your .env file.")

# Supabase URL fix (SQLAlchemy requires 'postgresql://' instead of 'postgres://')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# PostgreSQL Engine - Optimized for Supabase Pooler & SSL Stability
engine = create_engine(
    DATABASE_URL,
    pool_size=15,          # Supabase Free Tier PgBouncer ke liye safe limit (per worker)
    max_overflow=10,       # Max temporary burst connections (Total 25 connections max)
    pool_timeout=30,       # Connection request queue timeout
    pool_pre_ping=True,    # Dropped / stale connections ka auto-detection & reconnect
    pool_recycle=300,      # 5 minute me connection refresh (PgBouncer idle timeout bypass)
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }                      # SSL connection Drop aur Socket Timeout rokne ke liye
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Server start hote hi Supabase par missing tables create kar dega
Base.metadata.create_all(bind=engine)