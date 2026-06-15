from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .database import init_db
from .api import auth, candidate, interview, ai, stats, export, position, config_api

app = FastAPI(title="AI智能招聘面试管理系统", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(candidate.router)
app.include_router(interview.router)
app.include_router(ai.router)
app.include_router(stats.router)
app.include_router(export.router)
app.include_router(position.router)
app.include_router(config_api.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Mount frontend static files (production)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_dir = os.path.join(BASE_DIR, "frontend", "dist")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.on_event("startup")
def on_startup():
    """Initialize database tables and default data."""
    init_db()
    from .database import SessionLocal
    from .models.user import User
    from .services.auth_service import hash_password
    from .config import DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_NAME

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == DEFAULT_ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=DEFAULT_ADMIN_USERNAME,
                password_hash=hash_password(DEFAULT_ADMIN_PASSWORD),
                real_name=DEFAULT_ADMIN_NAME,
                role="admin",
            )
            db.add(admin)
            db.commit()
            print(f"✅ 默认管理员已创建: {DEFAULT_ADMIN_USERNAME}")
    finally:
        db.close()
