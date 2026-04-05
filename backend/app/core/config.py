import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    API_KEY = os.getenv('API_KEY', 'sk_track2_default_key_change_this')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE', 16 * 1024 * 1024))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

    # Use PostgreSQL on Render, SQLite locally
    _db_url = os.getenv('DATABASE_URL')
    if _db_url and _db_url.startswith(('postgresql://', 'postgres://')):
        # Use psycopg v3 dialect for Python 3.14 compatibility
        SQLALCHEMY_DATABASE_URI = _db_url.replace('postgres://', 'postgresql+psycopg://', 1).replace('postgresql://', 'postgresql+psycopg://', 1)
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///document_analysis.db'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
