from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import CheckIn
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import date

journal_bp = Blueprint("journal", __name__)


# add journal to today's checkin
@journal_bp.route("/journal", methods=["POST"])
@jwt_required()
def journal_entry():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    today = date.today()

    journal = data.get("journal")

    if journal is not None:
        journal = journal.strip()
        if journal == "":
            journal = None

    if journal and len(journal) > 2000:
        return jsonify({"error": "Journal entry must be under 2000 characters"}), 400

    checkin = CheckIn.query.filter_by(user_id=user_id, date=today).first()

    if not checkin:
        return jsonify({"error": "You must create today's checkin before adding a journal entry"}), 400

    if checkin.journal is not None and checkin.journal.strip() != "":
        return jsonify({"error": "A journal entry has already been added for today's checkin"}), 400

    checkin.journal = journal

    db.session.commit()

    return jsonify({"message": "Journal entry added"}), 201


# get today's journal entry
@journal_bp.route("/today", methods=["GET"])
@jwt_required()
def get_today_journal():
    user_id = int(get_jwt_identity())
    today = date.today()

    journal_today = CheckIn.query.filter(CheckIn.user_id == user_id,
                                         CheckIn.date == today,
                                         CheckIn.journal.isnot(None),
                                         CheckIn.journal != "").first()

    if not journal_today:
        return jsonify({"message": "No journal entry found for today"}), 404

    return jsonify({"journal": journal_today.journal})


# get journal history
@journal_bp.route("/journal-history", methods=["GET"])
@jwt_required()
def get_journal_history():
    user_id = int(get_jwt_identity())

    journal_history = CheckIn.query.filter(CheckIn.user_id == user_id,
                                           CheckIn.journal.isnot(None),
                                           CheckIn.journal != "").order_by(CheckIn.date.desc()).all()

    journal_result = []
    for j in journal_history:
        journal_result.append({"date": str(j.date),
                               "journal": j.journal})

    return jsonify(journal_result)
