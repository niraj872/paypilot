from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db.session import Base, SessionLocal, engine
from app import db as dbpkg  # noqa: F401 - registers database models
from app.api.routes import router
from app.seed import seed


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database schema and seed demo data on startup."""
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        seed(session)
    finally:
        session.close()

    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix=settings.api_prefix)


@app.get("/")
def root():
    return {
        "name": "PayPilot",
        "tagline": "AI agents that negotiate, verify, and safely move money for you.",
        "mode": "demo" if settings.demo_mode else "sandbox",
    }