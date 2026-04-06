from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token


auth_bp = Blueprint("auth", __name__)


# register
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # validation
    if not username or not email or not password:
        return jsonify({"error": "Missing fields"}), 400

    # hash password
    hashed_password = generate_password_hash(password)

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
