from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import CheckIn
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date

checkins_bp = Blueprint("checkins", __name__)


# create check-in
@checkins_bp.route("/check-in", methods=["POST"])
@jwt_required()
def create_checkin():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    mood = data.get("mood")
    stress = data.get("stress")
    energy = data.get("energy")
    sleep_hours = data.get("sleep_hours")

    # validation
    if mood is None or stress is None or energy is None:
        return jsonify({"error": "Missing fields"}), 400

    if not (1 <= mood <= 5) or not (1 <= stress <= 5) or not (1 <= energy <= 5):
        return jsonify({"error": "Values must be between 1 and 5"}), 400

    if sleep_hours is not None:
        try:
            sleep_hours = float(sleep_hours)
        except (TypeError, ValueError):
            return jsonify({"error": "sleep_hours must be a number"}), 400

        if sleep_hours < 0 or sleep_hours > 24:
            return jsonify({"error": "sleep_hours must be between 0 and 24"}), 400

    today = date.today()

    existing = CheckIn.query.filter_by(user_id=user_id, date=today).first()
    if existing:
        return jsonify({"error": "Check-in already exists for today"}), 400

    checkin = CheckIn(user_id=user_id,
                      date=today,
                      mood=mood,
                      stress=stress,
                      energy=energy,
                      sleep_hours=sleep_hours
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
                    "energy": checkin.energy,
                    "sleep_hours": checkin.sleep_hours,
                    "journal": checkin.journal,
                    "sleep_hours": checkin.sleep_hours
                    })


# get history
@checkins_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    user_id = int(get_jwt_identity())

    checkins = CheckIn.query.filter_by(user_id=user_id).order_by(CheckIn.date.desc()).all()

    result = []
    for c in checkins:
        result.append({"date": str(c.date),
                       "mood": c.mood,
                       "stress": c.stress,
                       "energy": c.energy,
                       "sleep_hours": c.sleep_hours
                       })

    return jsonify(result)
