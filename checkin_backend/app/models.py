from .extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)


class CheckIn(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    mood = db.Column(db.Integer, nullable=False)
    stress = db.Column(db.Integer, nullable=False)
    energy = db.Column(db.Integer, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=True)
    journal = db.Column(db.String(length=2000), nullable=True)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)

    item_type = db.Column(db.String(20), nullable=False, default="event")
    class_names = db.Column(db.JSON, nullable=True)
    group_id = db.Column(db.String(64), nullable=True)

    is_recurring = db.Column(db.Boolean, default=False)
    recurrence = db.Column(db.String(20), nullable=True)
