from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt
from .routes.routes import main
from .routes.auth import auth_bp
from .routes.checkins import checkins_bp
from .routes.calendar import calendar_bp
from .routes.trends import trends_bp
from .routes.journal import journal_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    with app.app_context():
        from .models import User, CheckIn
        db.create_all()

    app.register_blueprint(main)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(checkins_bp, url_prefix="/checkins")
    app.register_blueprint(calendar_bp, url_prefix="/calendar")
    app.register_blueprint(trends_bp, url_prefix="/trends")
    app.register_blueprint(journal_bp, url_prefix="/journal")

    return app


