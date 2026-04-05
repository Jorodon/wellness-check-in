from flask import Flask, Blueprint, current_app, request, render_template
from ..extensions import db
from ..extensions import db


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


# Daily Check-In page, allows user to record several metrics once per day
@main.route('/checkin')
def checkin_page():
    return render_template("pages/checkin_page.html")


# Weekly task page, allows users to record events and reminders for upcoming tasks
@main.route('/weekly_tasks')
def weekly_tasks():
    return render_template("pages/weekly_tasks.html")


# Journal page, allows user to write a journal entry and tie it to a specific day
@main.route('/journal')
def journal_page():
    return render_template("pages/journal_page.html")


# Statistics page, allows user to view aggregates of their daily check-ins over a selected period of time
@main.route('/statistics')
def statistics_page():
    return render_template("pages/statistics_page.html")


# Resources page, contains references to various mental health resources for the user to get more information or help
@main.route('/resources')
def resources_page():
    return render_template("pages/resources_page.html")


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



