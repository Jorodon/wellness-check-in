from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token


auth_bp = Blueprint("auth", __name__)


# register
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password1 = data.get("password1")
    password2 = data.get("password2")

    # validation
    if not username or not email or not password1:
        return jsonify({"error": "Missing fields"}), 400

    email = email.lower()

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

    if len(password1) < 8:
        return jsonify({"error": "Password has to be at least 8 characters"}), 400

    if password1 != password2:
        return jsonify({"error": "Password does not match"}), 400

    # hash password
    hashed_password = generate_password_hash(password1)

    # create user
    new_user = User(username=username,
                    email=email,
                    password_hash=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# login
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    # create JWT token
    access_token = create_access_token(identity=str(user.id))


    return jsonify({"access-token": access_token}), 200
