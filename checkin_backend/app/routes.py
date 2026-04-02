from flask import Blueprint, current_app, request
from .extensions import db
from .forms import RegisterForm
from .models import User

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home_page():
    return "<h1>Coming Soon...Gator Check-In!</h1>"


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


@main.route('/signin', methods=['GET', 'POST'])
def signin_page():
    if request.method == "POST":
        data = request.get_json()

        user_to_create = User(username=data['username'],
                              email=data['email_address'],
                              password_hash=data['password']
        )

        db.session.add(user_to_create)
        db.session.commit()
        return {'message': "User created successfully"}

    # form = RegisterForm()
    # if form.validate_on_submit():
    #     user_to_create = User(username=form.username.data,
    #                           email_address=form.email_address.data,
    #                           password=form.password1.data)
    #     db.session.add(user_to_create)
    #     db.session.commit()
    #
    # if form.errors != {}:
    #     for err_msg in form.errors.values():
    #         print(f'There was an error with creating user: {err_msg}')
    #
    # if form.errors != {}:
    #     for err_msg in form.errors.values():
    #         print(f'There was an error with creating user: {err_msg}')

    return "<p1>Sign in</p>"
