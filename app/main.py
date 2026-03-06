from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.restaurants import router as restaurant_router
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Restaurant  # noqa: F401
from app.services.ingest_service import collect_and_upsert

app = FastAPI(title=settings.app_name)
app.include_router(restaurant_router)

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/")
def index():
    return FileResponse(str(WEB_DIR / "index.html"))


@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        has_data = db.query(Restaurant.id).first() is not None
        if not has_data:
            start, end = settings.fetch_range()
            await collect_and_upsert(
                db,
                city=settings.default_city,
                start_date=start,
                end_date=end,
                min_rating=settings.high_score_threshold,
            )
