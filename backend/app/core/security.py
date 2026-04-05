"""Authentication middleware."""

from functools import wraps

from flask import request, jsonify

from app.core.config import Config


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if not api_key:
            return jsonify({"status": "error", "message": "Missing API key. Please provide x-api-key header."}), 401
        if api_key != Config.API_KEY:
            return jsonify({"status": "error", "message": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated
