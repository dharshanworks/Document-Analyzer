"""Document analysis routes."""

import base64
import os

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.middleware.auth import require_api_key
from app.services.document_service import analyze_document, analyze_and_format
from app.extensions import db
from app.models import Analysis, User

documents_bp = Blueprint('documents', __name__)

ALLOWED_TYPES = ['pdf', 'docx', 'txt', 'text', 'jpg', 'jpeg', 'png', 'gif', 'bmp']


@documents_bp.route('/api/document-analyze', methods=['GET', 'POST', 'OPTIONS'])
def analyze_document_endpoint():
    if request.method == 'OPTIONS':
        return '', 204

    if request.method == 'GET':
        return jsonify({
            "status": "success",
            "message": "Document Analysis API is running",
            "method": "POST",
            "auth": "x-api-key header",
        }), 200

    try:
        api_key = request.headers.get('x-api-key')
        expected_key = os.getenv('API_KEY', '7339386072_default')
        if not api_key or api_key != expected_key:
            return jsonify({"status": "error", "message": "Invalid API key"}), 401

        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Missing JSON body with fileName, fileType, fileBase64"}), 400

        file_name = data.get('fileName')
        file_type = data.get('fileType', '').lower().strip()
        file_base64 = data.get('fileBase64')

        if not file_name or not file_type or not file_base64:
            return jsonify({"error": "Missing required fields: fileName, fileType, fileBase64"}), 400

        if file_type not in ALLOWED_TYPES:
            return jsonify({"error": f"Unsupported file type: {file_type}"}), 400

        result = analyze_document(file_base64, file_type, file_name)
        if result.get("status") == "error":
            return jsonify({"error": result.get("message")}), 400

        sentiment_data = result.get("sentiment", {})
        if isinstance(sentiment_data, dict):
            sentiment_label = sentiment_data.get("classification", "Neutral")
            sentiment_polarity = sentiment_data.get("polarity", 0.0)
            sentiment_subjectivity = sentiment_data.get("subjectivity", 0.0)
        else:
            sentiment_label = str(sentiment_data)
            sentiment_polarity = 0.0
            sentiment_subjectivity = 0.0

        entities = result.get("entities", {})

        return jsonify({
            "status": "success",
            "fileName": result.get("fileName", file_name),
            "summary": result.get("summary", ""),
            "entities": {
                "names": entities.get("names", []),
                "dates": entities.get("dates", []),
                "organizations": entities.get("organizations", []),
                "amounts": entities.get("amounts", []),
                "locations": entities.get("locations", []),
            },
            "sentiment": sentiment_label,
            "sentiment_polarity": sentiment_polarity,
            "sentiment_subjectivity": sentiment_subjectivity,
            "statistics": result.get("statistics", {}),
            "readability": result.get("readability", {}),
            "keywords": result.get("keywords", []),
            "key_phrases": result.get("key_phrases", []),
            "deep_analysis": result.get("deep_analysis", {}),
            "timestamp": result.get("timestamp", ""),
        }), 200

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@documents_bp.route('/upload', methods=['POST'])
@jwt_required(optional=True)
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if file_ext not in ['pdf', 'docx', 'txt', 'jpg', 'jpeg', 'png']:
            return jsonify({"error": f"Unsupported file type: {file_ext}"}), 400

        file_content = file.read()
        file_base64 = base64.b64encode(file_content).decode('utf-8')

        result = analyze_and_format(file_base64, file_ext, file.filename)
        if not result.get("success"):
            return jsonify({"error": result.get("message", "Analysis failed")}), 400

        user_id = get_jwt_identity()
        if user_id:
            _save_analysis_to_db(int(user_id), result)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Unable to analyze file: {str(e)}"}), 500


def _save_analysis_to_db(user_id, result):
    try:
        analysis_data = result.get('analysis', {})
        deep = analysis_data.get('deep_analysis', {})
        doc_type = deep.get('document_type', {})
        quality = analysis_data.get('content_quality', {})
        entities = analysis_data.get('entities', {})

        analysis = Analysis(
            user_id=user_id,
            filename=result.get('filename', 'unknown'),
            file_type=result.get('filename', '').split('.')[-1].lower() if '.' in result.get('filename', '') else 'txt',
            word_count=analysis_data.get('statistics', {}).get('word_count', 0),
            sentiment=analysis_data.get('sentiment', 'Neutral'),
            document_type=doc_type.get('primary', 'general') if isinstance(doc_type, dict) else 'general',
            quality_grade=quality.get('grade', 'N/A'),
            quality_score=quality.get('overall_score', 0),
            entity_count=sum(len(v) for v in entities.values() if isinstance(v, list)),
            topic_count=len(analysis_data.get('topics', [])),
            result_data=analysis_data,
        )
        db.session.add(analysis)
        db.session.commit()
        return analysis.id
    except Exception as e:
        db.session.rollback()
        return None
