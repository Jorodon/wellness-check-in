import pytest
from datetime import date, timedelta

from checkin_backend.app.extensions import db
from checkin_backend.app.models import CheckIn

# ------- This file contains tests for the statistics functionality ------- #


# Test average for when there is no data for past 7 days
def test_statistics_01(client, auth_headers):
    response = client.get(
        "/trends/weekly-average", 
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "No check-in found for the past 7 days"


# Tests average with only one check-in in the past 7 days
def test_statistics_02(client, auth_headers, app, test_user):
    with app.app_context():
        checkin = CheckIn(
            user_id=test_user["id"],
            date=date.today(),
            mood=4,
            stress=2,
            energy=5,
            sleep_hours=7.5
        )
        db.session.add(checkin)
        db.session.commit()

    response = client.get(
        "/trends/weekly-average", 
        headers=auth_headers
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["avg_mood"] == pytest.approx(4.0)
    assert data["avg_stress"] == pytest.approx(2.0)
    assert data["avg_energy"] == pytest.approx(5.0)
    assert data["avg_sleep_hours"] == pytest.approx(7.5)

# Tests average with multiple check-ins in the past 7 days, with old check-in being excluded
def test_statistics_03(client, auth_headers, app, test_user):
    with app.app_context():
        checkin1 = CheckIn(
            user_id=test_user["id"],
            date=date.today(),
            mood=4,
            stress=2,
            energy=5,
            sleep_hours=8.0
        )
        checkin2 = CheckIn(
            user_id=test_user["id"],
            date=date.today() - timedelta(days=2),
            mood=2,
            stress=4,
            energy=3,
            sleep_hours=6.0
        )
        old_checkin = CheckIn(
            user_id=test_user["id"],
            date=date.today() - timedelta(days=8),
            mood=1,
            stress=1,
            energy=1,
            sleep_hours=1.0
        )

        db.session.add(checkin1)
        db.session.add(checkin2)
        db.session.add(old_checkin)
        db.session.commit()

    response = client.get(
        "/trends/weekly-average", 
        headers=auth_headers
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["avg_mood"] == pytest.approx(3.0)
    assert data["avg_stress"] == pytest.approx(3.0)
    assert data["avg_energy"] == pytest.approx(4.0)
    assert data["avg_sleep_hours"] == pytest.approx(7.0)

# Tests get weekly history with no check-ins in the past 7 days
def test_statistics_04(client, auth_headers):
    response = client.get(
        "/trends/weekly-history", 
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "No check-ins for the past 7 days"

# Test that data returned from weekly history endpoint is sorted
def test_statistics_05(client, auth_headers, app, test_user):
    with app.app_context():
        checkin1 = CheckIn(
            user_id=test_user["id"],
            date=date.today() - timedelta(days=3),
            mood=2,
            stress=4,
            energy=3,
            sleep_hours=6.5
        )
        checkin2 = CheckIn(
            user_id=test_user["id"],
            date=date.today(),
            mood=5,
            stress=1,
            energy=4,
            sleep_hours=8.0
        )
        old_checkin = CheckIn(
            user_id=test_user["id"],
            date=date.today() - timedelta(days=10),
            mood=1,
            stress=1,
            energy=1,
            sleep_hours=5.0
        )

        db.session.add(checkin1)
        db.session.add(checkin2)
        db.session.add(old_checkin)
        db.session.commit()

    response = client.get(
        "/trends/weekly-history", 
        headers=auth_headers
    )
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 2

    assert data[0]["date"] == str(date.today() - timedelta(days=3))
    assert data[0]["mood"] == 2
    assert data[0]["stress"] == 4
    assert data[0]["energy"] == 3
    assert data[0]["sleep_hours"] == 6.5

    assert data[1]["date"] == str(date.today())
    assert data[1]["mood"] == 5
    assert data[1]["stress"] == 1
    assert data[1]["energy"] == 4
    assert data[1]["sleep_hours"] == 8.0