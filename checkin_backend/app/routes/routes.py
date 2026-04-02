from flask import Flask, Blueprint, current_app, request, render_template
from app.extensions import db
from app.forms import RegisterForm
from app.models import User

main = Blueprint('main', __name__)


# Default start page, has buttons for login (login_page) and registering (register_page)
@main.route('/')
def start_page():
    return render_template("index.html")


# Home page, also referred to as the dashboard. Default view once a user has logged into app
@main.route('/home')
def home_page():
    return render_template("pages/home_page.html")


# Registration page, allows user to register with username, email, and password
@main.route('/register')
def register_page():
    return render_template("pages/register_page.html")


# Login page, allows user to login with email/username and password
@main.route('/login')
def login_page():
    return render_template("pages/login_page.html")


# Database reset page, for development use
@main.route('/dev/reset-db')
def reset_db():
    if not current_app.config.get("DEBUG", False):
        return "Not allowed outside development.", 403

    secret = current_app.config.get("DEV_RESET_KEY")

    if request.args.get("key") != secret:
        return "Unauthorized", 401

    db.drop_all()
    db.create_all()
    return "Development database reset complete."

