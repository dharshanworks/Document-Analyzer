from flask import Flask, jsonify

from app.config import Config
from app.extensions import cors, db, jwt


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    cors.init_app(app, resources={r"/*": {"origins": config_class.CORS_ORIGINS}})
    db.init_app(app)
    jwt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.documents import documents_bp
    from app.routes.user import user_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(user_bp)

    # Create tables AFTER models are imported via blueprints
    with app.app_context():
        db.create_all()

    @app.route('/')
    def health_check():
        return jsonify({"status": "success", "message": "AI-Powered Document Analysis API is running", "version": "2.0.0"}), 200

    @app.route('/api/health')
    def api_health():
        return jsonify({"status": "success", "message": "API is operational"}), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"status": "error", "message": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    return app
