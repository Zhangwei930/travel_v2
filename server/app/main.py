"""周密出游 — FastAPI 后端入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import SessionLocal, init_db
from app.routers import admin, catalog, feedback, home, kb, trip
from app.seed import seed_if_empty

app = FastAPI(title="周密出游 API", version="1.0", description="智能本地出游规划系统后端")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(catalog.router)
app.include_router(home.router)
app.include_router(home.compat_router)
app.include_router(trip.router)
app.include_router(kb.router)
app.include_router(feedback.router)
app.include_router(admin.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()


@app.get("/")
def root():
    return {"name": "周密出游 API", "version": "1.0", "docs": "/docs"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
