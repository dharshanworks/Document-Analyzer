"""Document Analyzer API v1."""

from app.api.v1.auth import auth_bp
from app.api.v1.documents import documents_bp
from app.api.v1.user import user_bp

__all__ = ["auth_bp", "documents_bp", "user_bp"]
