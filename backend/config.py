import os
import sys
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Base backend directory and project root
BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

# Ensure project root is in sys.path so 'import database' works seamlessly
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Load .env file from backend or root directory if present
env_path = BASE_DIR / '.env'
if not env_path.exists():
    env_path = ROOT_DIR / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chroma-blend-dev-secret-key-3e31337c')
    
    # SQLite Database Configuration (default in dedicated database/ folder)
    default_db_path = str(ROOT_DIR / 'database' / 'chroma_blend.db')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', default_db_path)
    if not os.path.isabs(DATABASE_PATH):
        DATABASE_PATH = str((BASE_DIR / DATABASE_PATH).resolve())
        
    # File Uploads
    default_upload_dir = str(ROOT_DIR / 'data' / 'uploads')
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', default_upload_dir)
    if not os.path.isabs(UPLOAD_FOLDER):
        UPLOAD_FOLDER = str((BASE_DIR / UPLOAD_FOLDER).resolve())
        
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload size
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'webp', 'txt', 'docx', 'doc', 'csv'}
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 't')
    
    # Server settings
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't')
