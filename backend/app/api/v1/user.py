"""User routes: history, stats."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from app.core.extensions import db
from app.models import Analysis

user_bp = Blueprint('user', __name__)


@user_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = Analysis.query.filter_by(user_id=user_id)\
        .order_by(Analysis.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "success": True,
        "analyses": [a.to_summary() for a in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    }), 200


@user_bp.route('/history/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis(analysis_id):
    user_id = int(get_jwt_identity())
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    return jsonify({
        "success": True,
        "analysis": analysis.to_dict(),
    }), 200


@user_bp.route('/history/<int:analysis_id>', methods=['DELETE'])
@jwt_required()
def delete_analysis(analysis_id):
    user_id = int(get_jwt_identity())
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    db.session.delete(analysis)
    db.session.commit()

    return jsonify({"success": True, "message": "Analysis deleted"}), 200


@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = int(get_jwt_identity())

    total_analyses = Analysis.query.filter_by(user_id=user_id).count()
    if total_analyses == 0:
        return jsonify({
            "success": True,
            "total_analyses": 0,
            "total_words": 0,
            "average_quality_score": 0,
            "sentiment_distribution": {},
            "document_types": {},
            "file_types": {},
        }), 200

    total_words = db.session.query(func.sum(Analysis.word_count))\
        .filter_by(user_id=user_id).scalar() or 0

    avg_quality = db.session.query(func.avg(Analysis.quality_score))\
        .filter_by(user_id=user_id).scalar() or 0

    sentiment_dist = {}
    for row in db.session.query(Analysis.sentiment, func.count(Analysis.id))\
            .filter_by(user_id=user_id).group_by(Analysis.sentiment).all():
        sentiment_dist[row[0]] = row[1]

    doc_types = {}
    for row in db.session.query(Analysis.document_type, func.count(Analysis.id))\
            .filter_by(user_id=user_id).group_by(Analysis.document_type).all():
        doc_types[row[0]] = row[1]

    file_types = {}
    for row in db.session.query(Analysis.file_type, func.count(Analysis.id))\
            .filter_by(user_id=user_id).group_by(Analysis.file_type).all():
        file_types[row[0]] = row[1]

    return jsonify({
        "success": True,
        "total_analyses": total_analyses,
        "total_words": total_words,
        "average_quality_score": round(avg_quality, 1),
        "sentiment_distribution": sentiment_dist,
        "document_types": doc_types,
        "file_types": file_types,
    }), 200
