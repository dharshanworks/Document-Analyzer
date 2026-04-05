"""Authentication routes: register, login, profile, password, account."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

from app.core.extensions import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Missing required fields: username, email, password"}), 400

        username = data.get('username').strip()
        email = data.get('email').strip()
        password = data.get('password')

        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already exists"}), 409

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 409

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=data.get('full_name', ''),
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Account created successfully",
            "user": user.to_dict(),
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({"error": "Missing username or password"}), 400

        username = data.get('username').strip()
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid username or password"}), 401

        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            "status": "success",
            "access_token": access_token,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
        }), 200
    except Exception as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "status": "success",
        "user": user.to_dict(),
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if 'full_name' in data:
        user.full_name = data['full_name'].strip()
    if 'email' in data:
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user.id:
            return jsonify({"error": "Email already in use"}), 409
        user.email = data['email'].strip()

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Profile updated successfully",
        "user": user.to_dict(),
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({"error": "Missing old_password or new_password"}), 400

    if not check_password_hash(user.password_hash, data['old_password']):
        return jsonify({"error": "Current password is incorrect"}), 401

    if len(data['new_password']) < 6:
        return jsonify({"error": "New password must be at least 6 characters"}), 400

    user.password_hash = generate_password_hash(data['new_password'])
    db.session.commit()

    return jsonify({"status": "success", "message": "Password changed successfully"}), 200


@auth_bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"status": "success", "message": "Account deleted successfully"}), 200
