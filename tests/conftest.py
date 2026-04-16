import pytest
from werkzeug.security import generate_password_hash

from checkin_backend.app import create_app
from checkin_backend.app.extensions import db
from checkin_backend.app.models import User

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,
    })

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User(
            email="test@example.com",
            password_hash=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200

    token = response.get_json()["access-token"]
    return {"Authorization": f"Bearer {token}"}