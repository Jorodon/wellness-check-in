from datetime import date, timedelta
from checkin_backend.app.extensions import db
from checkin_backend.app.models import CheckIn

# ------- This file contains tests for the journal functionality. ------- #

# Test requires check-in to be created first
def test_journal_01(client, auth_headers, app, test_user):
    response = client.post(
        "/journal/journal",
        json={
            "journal": "Today was a good day!"
        },
        headers=auth_headers
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "You must create today's checkin before adding a journal entry"


# Test for successful journal entry and storage in the database
def test_journal_02(client, auth_headers):
    client.post(
        "/checkins/check-in",
        json={
            "mood": 4,
            "energy": 3,
            "stress": 2,
            "sleep_hours": 7.5,
        },
        headers=auth_headers
    )

    response = client.post(
        "/journal/journal",
        json={
            "journal": "Today was a good day!"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.get_json()["message"] == "Journal entry added"

    response2 = client.get(
        "/journal/today",
        headers=auth_headers
    )
    data = response2.get_json()

    assert response2.status_code == 200
    assert data["journal"] == "Today was a good day!"


# Test for duplicate journal entry for the same day
def test_journal_03(client, auth_headers):
    client.post(
        "/checkins/check-in",
        json={
            "mood": 4,
            "energy": 3,
            "stress": 2,
            "sleep_hours": 7.5,
        },
        headers=auth_headers
    )

    client.post(
        "/journal/journal",
        json={
            "journal": "First entry of the day"
        },
        headers=auth_headers
    )

    response = client.post(
        "/journal/journal",
        json={
            "journal": "Second entry of the day"
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "A journal entry has already been added for today's checkin"

# Test for retrieving journal entry when it does not exist
def test_journal_04(client, auth_headers):
    response = client.get(
        "/journal/today", 
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "No journal entry found for today"


# Test for journal being too long
def test_journal_05(client, auth_headers):
    client.post(
        "/checkins/check-in",
        json={
            "mood": 4,
            "stress": 2,
            "energy": 3,
            "sleep_hours": 7
        },
        headers=auth_headers
    )

    #creates a string of 2001 characters
    long_journal = "a" * 2001

    response = client.post(
        "/journal/journal",
        json={
            "journal": long_journal
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Journal entry must be under 2000 characters"


# Test that blank journal gets stored as none
def test_journal_06(client, auth_headers):
    client.post(
        "/checkins/check-in",
        json={
            "mood": 4,
            "stress": 2,
            "energy": 3,
            "sleep_hours": 7
        },
        headers=auth_headers
    )

    response = client.post(
        "/journal/journal",
        json={
            "journal": "    "
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.get_json()["message"] == "Journal entry added"

    response2 = client.get(
        "/journal/today",
        headers=auth_headers
    )
    assert response2.status_code == 404


# Test for journal history retrieval
def test_journal_07(client, auth_headers, app, test_user):
    with app.app_context():
        checkin1 = CheckIn(
            user_id=test_user["id"],
            date=date.today(),
            mood=5,
            stress=1,
            energy=4,
            sleep_hours=8.0,
            journal="First check in journal"
        )

        checkin2 = CheckIn(
            user_id=test_user["id"],
            date=date.today() - timedelta(days=1),
            mood=3,
            stress=4,
            energy=2,
            sleep_hours=6.5,
            journal="Second check in journal"
        )

        db.session.add(checkin1)
        db.session.add(checkin2)
        db.session.commit()

    response = client.get(
        "/journal/journal-history", 
        headers=auth_headers
    )
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 2

    dates = [entry["date"] for entry in data]
    journals = [entry["journal"] for entry in data]

    assert str(date.today()) in dates
    assert str(date.today() - timedelta(days=1)) in dates
    assert "First check in journal" in journals
    assert "Second check in journal" in journals