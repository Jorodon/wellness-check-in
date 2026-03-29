from flask import Flask, Blueprint, current_app, request, render_template
from .extensions import db
from .forms import RegisterForm
from .models import User

main = Blueprint('main', __name__)

# Default start page, has buttons for login (login_page) and registering (register_page)
@main.route('/')
def start_page():
    return render_template("index.html")

# Home page, also referred to as the dashboard. Default view once a user has logged into app
@main.route('/home')
def home_page():
    return render_template("pages/home_page.html")

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

# Registration page, allows user to register with username, email, and password
@main.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == "POST":
        data = request.get_json()

        user_to_create = User(username=data['username'],
                              email=data['email_address'],
                              password_hash=data['password']
        )

        db.session.add(user_to_create)
        db.session.commit()
        return "{{ url_for('main.login_page') }}"
        return {'message': "User created successfully"}

    # form = RegisterForm()
    # if form.validate_on_submit():
    #     user_to_create = User(username=form.username.data,
    #                           email_address=form.email_address.data,
    #                           password=form.password1.data)
    #     db.session.add(user_to_create)
    #     db.session.commit()
    
    # if form.errors != {}:
    #     for err_msg in form.errors.values():
    #         print(f'There was an error with creating user: {err_msg}')
    
    # if form.errors != {}:
    #     for err_msg in form.errors.values():
    #         print(f'There was an error with creating user: {err_msg}')

    #return "<p1>Login</p>"
    return render_template("pages/register_page.html")

# Login page, allows user to login with email/username and password
@main.route('/login')
def login_page():
    return render_template("pages/login_page.html")
    #return "<h1>Coming Soon...Gator Check-In!</h1>"