from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import CheckIn
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date

checkins_bp = Blueprint("checkins", __name__)


# create check-in
@checkins_bp.route("/", methods=["POST"])
@jwt_required()
def create_checkin():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    mood = data.get("mood")
    stress = data.get("stress")
    energy = data.get("energy")

    # validation
    if mood is None or stress is None or energy is None:
        return jsonify({"error": "Missing fields"}), 400

    if not (1 <= mood <= 5) or not (1 <= stress <= 5) or not (1 <= energy <= 5):
        return jsonify({"error": "Values must be between 1 and 5"}), 400

    today = date.today()

    existing = CheckIn.query.filter_by(user_id=user_id, date=today).first()
    if existing:
        return jsonify({"error": "Check-in already exists for today"}), 400

    checkin = CheckIn(user_id=user_id,
                      date=today,
                      mood=mood,
                      stress=stress,
                      energy=energy
                      )

    db.session.add(checkin)
    db.session.commit()

    return jsonify({"message": "Check-in created"}), 201


# get today's check-in
@checkins_bp.route("/today", methods=["GET"])
@jwt_required()
def get_today_checkin():
    user_id = int(get_jwt_identity())
    today = date.today()

    checkin = CheckIn.query.filter_by(user_id=user_id,
                                      date=today).first()

    if not checkin:
        return jsonify({"message": "No check-in found"}), 404

    return jsonify({"date": str(checkin.date),
                    "mood": checkin.mood,
                    "stress": checkin.stress,
                    "energy": checkin.energy
                    })


# get history
@checkins_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())

    checkins = CheckIn.query.filter_by(user_id=user_id).all()

    result = []
    for c in checkins:
        result.append({"date": str(c.date),
                       "mood": c.mood,
                       "stress": c.stress,
                       'energy': c.energy
                       })

    return jsonify(result)
