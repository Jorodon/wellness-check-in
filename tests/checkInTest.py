from datetime import date, timedelta
from checkin_backend.app.extensions import db
from checkin_backend.app.models import CheckIn

# ------- This file contains tests for the check-in functionality of the wellness check-in application. ------- #


# Test for successful check-in
def test_checkin_01(client, auth_headers, app, test_user):
    response = client.post(
        "/checkins/check-in",
        json={
            "mood": 4,
            "energy": 3,
            "stress": 2,
            "sleep_hours": 7.5,
        },
        headers=auth_headers
    )

    # JSON response
    assert response.status_code == 201
    assert response.get_json()["message"] == "Check-in created"

    # DB check
    with app.app_context():
        checkin = CheckIn.query.filter_by(user_id=test_user["id"]).first()
        assert checkin is not None
        assert checkin.mood == 4
        assert checkin.energy == 3
        assert checkin.stress == 2
        assert checkin.sleep_hours == 7.5

# TEst for sleep hours below 0
def test_checkin_02(client, auth_headers):
    response = client.post(
        "/checkins/check-in",
        json={
            "mood": 4,
            "energy": 3,
            "stress": 2,
            "sleep_hours": -1
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Sleep hours must be between 0 and 24"

# Test for sleep hours above 24
def test_checkin_03(client, auth_headers):
    response = client.post(
        "/checkins/check-in",
        json={
            "mood": 4,
            "energy": 3,
            "stress": 2,
            "sleep_hours": 25
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Sleep hours must be between 0 and 24"

# Test for duplicate check-in on the same day
def test_checkin_04(client, auth_headers):
    # Check-in 1
    client.post(
        "/checkins/check-in",
        json={
            "mood": 4,
            "energy": 5,
            "stress": 2,
            "sleep_hours": 7.3
        },
        headers=auth_headers
    )

    # Check-in 2 (same day)
    response = client.post(
        "/checkins/check-in",
        json={
            "mood": 4,
            "energy": 5,
            "stress": 2,
            "sleep_hours": 7.3
        },
        headers=auth_headers
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "Check-in already exists for today"

# Empty sleep should nullify sleep_hours in DB
def test_checkin_05(client, auth_headers, app, test_user):
    response = client.post(
        "/checkins/check-in",
        json={
            "mood": 4,
            "stress": 2,
            "energy": 3
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.get_json()["message"] == "Check-in created"

    with app.app_context():
        checkin = CheckIn.query.filter_by(user_id=test_user["id"]).first()
        assert checkin is not None
        assert checkin.sleep_hours is None

# Test for non-numeric sleep hours (even though this should be prevented by frontend validation, we want to ensure backend handles properly)
def test_checkin_06(client, auth_headers):
    response = client.post(
        "/checkins/check-in",
        json={
            "mood": 4,
            "stress": 2,
            "energy": 5,
            "sleep_hours": "abc"
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Sleep hours must be a number"

# Test for getting today's check-in when none exists
def test_checkin_07(client, auth_headers):
    response = client.get(
        "/checkins/today",
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "No check-in found"

# Test for getting today's check-in when it exists
def test_checkin_08(client, auth_headers):
    # creates check-in for today
    client.post(
        "/checkins/check-in",
        json={
            "mood": 3,
            "stress": 4,
            "energy": 2,
            "sleep_hours": 6
        },
        headers=auth_headers
    )

    response = client.get(
        "/checkins/today",
        headers=auth_headers
    )

    data = response.get_json()
    assert response.status_code == 200
    assert data["mood"] == 3
    assert data["stress"] == 4
    assert data["energy"] == 2
    assert data["sleep_hours"] == 6.0

# Test for getting check-in history
def test_checkin_09(client, auth_headers, app, test_user):
    with app.app_context():
        # create 2 check-ins for history test
        checkin1 = CheckIn(
            user_id=test_user["id"],
            date=date.today(),
            mood=5,
            stress=1,
            energy=4,
            sleep_hours=8.0
        )

        checkin2 = CheckIn(
            user_id=test_user["id"],
            date=date.today() - timedelta(days=1),
            mood=3,
            stress=4,
            energy=2,
            sleep_hours=6.5
        )

        db.session.add(checkin1)
        db.session.add(checkin2)
        db.session.commit()

    response = client.get(
        "/checkins/history",
        headers=auth_headers
    )

    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 2

    dates = [entry["date"] for entry in data]
    assert str(date.today()) in dates
    assert str(date.today() - timedelta(days=1)) in dates