from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date, timedelta
from sqlalchemy import func
from ..models import CheckIn
from ..extensions import db

trends_bp = Blueprint("trends", __name__)


# get weekly check-in average
@trends_bp.route("/weekly-average", methods=["GET"])
@jwt_required()
def get_weekly_avg():
    user_id = int(get_jwt_identity())
    today = date.today()
    start_date = today - timedelta(days=6)

    avg_data = db.session.query(func.avg(CheckIn.mood).label("avg_mood"),
                                func.avg(CheckIn.stress).label("avg_stress"),
                                func.avg(CheckIn.energy).label("avg_energy")).filter(CheckIn.user_id == user_id,
                                                                                     CheckIn.date >= start_date,
                                                                                     CheckIn.date <= today).first()
    if not avg_data or avg_data.avg_mood is None:
        return jsonify({"message": "No check-in found for the past 7 days"}), 404

    return jsonify({"avg_mood": float(avg_data.avg_mood),
                    "avg_stress": float(avg_data.avg_stress),
                    "avg_energy": float(avg_data.avg_energy)
                    })


# get 7 day history
@trends_bp.route("/weekly-history", methods=["GET"])
@jwt_required()
def get_weekly_trends():
    user_id = int(get_jwt_identity())
    today = date.today()
    start_date = today - timedelta(days=6)

    checkins = CheckIn.query.filter(CheckIn.user_id == user_id,
                                    CheckIn.date >= start_date,
                                    CheckIn.date <= today).order_by(CheckIn.date.asc()).all()
    if not checkins:
        return jsonify({"message": "No check-ins for the past 7 days"}), 404

    weekly_history = []
    for c in checkins:
        weekly_history.append({"date": str(c.date),
                               "mood": c.mood,
                               "stress": c.stress,
                               "energy": c.energy})

    return jsonify(weekly_history)
