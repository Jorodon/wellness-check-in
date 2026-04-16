from checkin_backend.app.models import User

# Password too short test case
def test_login_01(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "student@ufl.edu",
            "password1": "123",
            "password2": "123"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Password has to be at least 8 characters"

#Successful registration test case
def test_login_02(client, app):
    response = client.post("/auth/register", json={
        "email": "wellnessRules@ufl.edu",
        "password1": "GatorCheck1",
        "password2": "GatorCheck1"
    }) 

    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully"

    with app.app_context():
        user = User.query.filter_by(email="wellnessRules@ufl.edu").first()
        assert user is not None


# Invalid credentials test case
def test_login_03(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPass1!"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid credentials"

# Duplicate email registration test case
def test_login_04(client, test_user):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password1": "password123",
            "password2": "password123"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Email already registered"

# Successful login test case
def test_login_05(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "password123"
        }
    )

    data = response.get_json()
    assert response.status_code == 200
    assert "access-token" in data
    assert data["email"] == "test@example.com"

# Missing fields test case
def test_login_06(client):
    response = client.post(
        "/auth/register",
        json={
            "password1": "password123",
            "password2": "password123"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing fields"

# Password mismatch test case
def test_login_07(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "mismatch@ufl.edu",
            "password1": "password123",
            "password2": "different123"
        }
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Password does not match"