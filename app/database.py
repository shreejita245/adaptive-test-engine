from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres.gzalfhvizdcdrycdqgqx:ShreejitaSaha2026@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres?sslmode=require")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()