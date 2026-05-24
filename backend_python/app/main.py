# The "Entry Point" where you start the server.
from fastapi import FastAPI, Depends  # type: ignore[import]
from sqlalchemy import text
from .database import engine, Base, get_db
from .routers import auth, orders
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# Load environment variables at application startup
load_dotenv()

# Create the FastAPI app instance before including routers
app = FastAPI(title="High-Scale Logistics Platform")

from ai_bot import bot
app.include_router(bot.router)

from fastapi.middleware.cors import CORSMiddleware

# CORS configuration - allow frontend URLs
allowed_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Generate all DB tables on startup
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(orders.router, prefix="/orders", tags=["Orders"])

@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "postgres": "Connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}