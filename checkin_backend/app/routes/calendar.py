from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import uuid
from ..extensions import db
from ..models import Event

calendar_bp = Blueprint("calendar", __name__)


# Helper functions
def event_to_dict(event):
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "start": event.start_time.isoformat() if event.start_time else None,
        "end": event.end_time.isoformat() if event.end_time else None,
        "classNames": event.class_names,
        "groupId": event.group_id,
        "extendedProps": {
            "item_type": event.item_type,
            "user_id": event.user_id,
            #"is_recurring": event.is_recurring,
            #"recurrence": event.recurrence
        }
    }


def parse_datetime(datetime_str, field_name):
    if datetime_str is None:
        return None
    try:
        return datetime.fromisoformat(datetime_str)
    except ValueError:
        raise ValueError(f"Invalid {field_name}. Use YYYY-MM-DD format")


def validate_class_names(class_names):
    if class_names is None:
        return None

    if not isinstance(class_names, list):
        raise ValueError("class_names must be a list")

    for c in class_names:
        if not isinstance(c, str):
            raise ValueError("class_names must contain only strings")

    return class_names


def get_next_datetime(dt, recurrence):
    if recurrence == "daily":
        return dt + timedelta(days=1)
    elif recurrence == "weekly":
        return dt + timedelta(weeks=1)
    elif recurrence == "monthly":
        return dt + timedelta(days=30)
    else:
        return dt


# POST - Create event(s)
@calendar_bp.route("/create_events", methods=["POST"])
@jwt_required()
def create_event():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    start_time_str = data.get("start_time")
    end_time_str = data.get("end_time")
    item_type = data.get("item_type")
    class_names = data.get("class_names")
    is_recurring = data.get("is_recurring")
    recurrence = data.get("recurrence")
    repeat_count = data.get("repeat_count", 1)

    if not title:
        return jsonify({"error": "Title is required"}), 400

    if not start_time_str:
        return jsonify({"error": "Start time is required"}), 400

    if not end_time_str:
        return jsonify({"error": "End time is required"}), 400

    try:
        start_time = parse_datetime(start_time_str, "start_time")
        end_time = parse_datetime(end_time_str, "end_time")
        class_names = validate_class_names(class_names)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if end_time <= start_time:
        return jsonify({"error": "End date must be same day, or later date than start date"}), 400

    if item_type not in ["event", "task"]:
        return jsonify({"error": "item type must be 'event' or 'task'"}), 400

    if is_recurring:
        if recurrence not in ["daily", "weekly", "monthly"]:
            return jsonify({"error": "recurrence must be 'daily', 'weekly', 'monthly'"}), 400
    if not isinstance(repeat_count, int) or repeat_count < 1:
        return jsonify({"error": "repeat count must be positive"}), 400

    else:
        recurrence = None

    created_events = []

    if is_recurring:
        group_id = str(uuid.uuid4())

        current_start = start_time
        current_end = end_time

        for _ in range(repeat_count):
            event = Event(user_id=user_id,
                          title=title,
                          description=description,
                          start_time=current_start,
                          end_time=current_end,
                          item_type=item_type,
                          class_names=class_names,
                          group_id=group_id,
                          is_recurring=True,
                          recurrence=recurrence
                          )

            db.session.add(event)
            created_events.append(event)

            current_start = get_next_datetime(current_start, recurrence)
            if current_end:
                current_end = get_next_datetime(current_end, recurrence)

    else:
        event = Event(user_id=user_id,
                      title=title,
                      description=description,
                      start_time=start_time,
                      end_time=end_time,
                      item_type=item_type,
                      class_names=class_names,
                      group_id=None,
                      is_recurring=False,
                      recurrence=None
                      )

        db.session.add(event)
        created_events.append(event)

    db.session.commit()

    return jsonify({"message": "Event created successfully",
                    "events": [event_to_dict(event) for event in created_events]
                    }), 201


# GET - All events
@calendar_bp.route("/events", methods=["GET"])
@jwt_required()
def get_events():
    user_id = int(get_jwt_identity())

    events = Event.query.filter_by(user_id=user_id).order_by(Event.start_time).all()

    return jsonify([event_to_dict(event) for event in events]), 200


# PUT - Update event(s)
@calendar_bp.route("/events/<int:event_id>", methods=["PUT"])
@jwt_required()
def update_event(event_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    event = Event.query.filter_by(id=event_id, user_id=user_id).first()

    if not event:
        return jsonify({"error": "Event not found"}), 404

    update_scope = data.get("update_scope", "one")

    if update_scope == "group" and not event.group_id:
        return jsonify({"error": "Not a recurring event"}), 400

    if update_scope == "group":
        events = Event.query.filter_by(user_id=user_id, group_id=event.group_id).all()
    else:
        events = [event]

    try:
        class_names = validate_class_names(data.get("class_names"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    for event in events:
        if "title" in data:
            event.title = data["title"]
        if "description" in data:
            event.description = data["description"]
        if "location" in data:
            event.location = data["location"]
        if "item_type" in data:
            event.item_type = data["item_type"]
        if class_names is not None:
            event.class_names = class_names

        if update_scope == "one":
            if "start_time" in data:
                event.start_time = parse_datetime(data["start_time"], "start_time")
            if "end_time" in data:
                event.end_time = parse_datetime(data["end_time"], "end_time")
                if event.end_time <= event.start_time:
                    return jsonify({"error": "End date must be same day, or later date than start date"}), 400

        db.session.commit()

        return jsonify({
            "message": "Updated",
            "events": [event_to_dict(event) for event in events]
        }), 200


# DELETE - event(s)
@calendar_bp.route("/event/<int:event_id>", methods=["DELETE"])
@jwt_required()
def delete_event(event_id):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    delete_scope = data.get("delete_scope", "one")

    event = Event.query.filter_by(id=event_id, user_id=user_id).first()

    if not event:
        return jsonify({"error": "Event not found"}), 404

    if delete_scope == "group" and event.group_id:
        events = Event.query.filter_by(user_id=user_id, group_id=event.group_id).all()
        for event in events:
            db.session.delete(event)
    else:
        db.session.delete(event)

    db.session.commit()

    return jsonify({"message": "Event deleted"}), 200
