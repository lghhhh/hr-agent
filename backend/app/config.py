import os
from dotenv import load_dotenv

# Load .env from multiple locations (priority order):
# 1. backend/app/../.env  → backend/.env  (running from backend/)
# 2. backend/app/../../.env → project root  (Docker / docker-compose)
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _try_path in [
    os.path.join(_BACKEND_DIR, ".env"),
    os.path.join(_BACKEND_DIR, "..", ".env"),
]:
    _resolved = os.path.abspath(_try_path)
    if os.path.exists(_resolved):
        load_dotenv(_resolved)
        break

# Database — 基于项目根目录，不依赖 CWD
_PROJECT_ROOT = os.path.dirname(_BACKEND_DIR)
_DEFAULT_DB = f"sqlite:///{os.path.join(_PROJECT_ROOT, 'data', 'hr_system.db')}"
DATABASE_URL = os.getenv("DATABASE_URL") or _DEFAULT_DB

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# LLM API (OpenAI-compatible)
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Default admin
DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
DEFAULT_ADMIN_NAME = os.getenv("DEFAULT_ADMIN_NAME", "管理员")
