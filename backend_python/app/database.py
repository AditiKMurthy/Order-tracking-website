# The "Plumbing" (SQLAlchemy setup).

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

# Load .env from project root
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=env_path)

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./order_track.db"

try:
    if DATABASE_URL.startswith("sqlite"):
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(DATABASE_URL)
    # Test the database connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except Exception as e:
    sqlite_url = "sqlite:///./order_track.db"
    print(f"Warning: Failed to connect to database at {DATABASE_URL} ({e}). "
          f"Falling back to local SQLite at {sqlite_url}")
    DATABASE_URL = sqlite_url
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
