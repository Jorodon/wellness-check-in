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
    journal = db.Column(db.Text, nullable=True)
