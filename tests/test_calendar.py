from checkin_backend.app.extensions import db
from checkin_backend.app.models import Event

# ------- This file contains tests for the calendar functionality ------- #

# Tests successful event creation and storage
def test_calendar_01(client, auth_headers):
    response = client.post(
        "/calendar/create_events",
        json={
            "title": "Doctor Appointment",
            "description": "Annual checkup",
            "start_time": "2026-04-20T10:00:00",
            "end_time": "2026-04-20T11:00:00",
            "item_type": "event"
        },
        headers=auth_headers
    )

    data = response.get_json()

    assert response.status_code == 201
    assert data["message"] == "Event created successfully"
    assert len(data["events"]) == 1
    assert data["events"][0]["title"] == "Doctor Appointment"
    assert data["events"][0]["description"] == "Annual checkup"

# Tests event creation with missing title
def test_calendar_02(client, auth_headers):
    response = client.post(
        "/calendar/create_events",
        json={
            "description": "Annual checkup",
            "start_time": "2026-04-20T10:00:00",
            "end_time": "2026-04-20T11:00:00",
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Title is required"

# Tests event creation with missing start time
def test_calendar_03(client, auth_headers):
    response = client.post(
        "/calendar/create_events",
        json={
            "title": "Doctor Appointment",
            "end_time": "2026-04-20T11:00:00",
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Start time is required"

# Tests event creation with end time before start time
def test_calendar_04(client, auth_headers):
    response = client.post(
        "/calendar/create_events",
        json={
            "title": "Doctor Appointment",
            "start_time": "2026-04-20T11:00:00",
            "end_time": "2026-04-20T10:00:00",
        },
        headers=auth_headers
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "end_time must be after start_time"

# Tests getting calendar events when there are no events and ensure list is empty
def test_calendar_05(client, auth_headers):
    response = client.get(
        "/calendar/events", 
        headers=auth_headers
    )
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 0


# Tests getting calendar events when there are events and ensure data is correct
def test_calendar_06(client, auth_headers):
    client.post(
        "/calendar/create_events",
        json={
            "title": "Study Session",
            "description": "Review notes",
            "start_time": "2026-04-21T14:00:00",
            "end_time": "2026-04-21T15:00:00",
            "item_type": "event"
        },
        headers=auth_headers
    )

    response = client.get(
        "/calendar/events", 
        headers=auth_headers
    )
    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Study Session"
    assert data[0]["description"] == "Review notes"

# Tests updating event successfully and ensure changes are reflected in database
def test_calendar_07(client, auth_headers):
    create_response = client.post(
        "/calendar/create_events",
        json={
            "title": "Study Session",
            "description": "Review notes",
            "start_time": "2026-04-21T14:00:00",
            "end_time": "2026-04-21T15:00:00",
            "item_type": "event",
        },
        headers=auth_headers
    )

    event_id = create_response.get_json()["events"][0]["id"]

    response = client.put(
        f"/calendar/events/{event_id}",
        json={
            "title": "Updated Study Session",
            "description": "Review chapters 1 and 2",
        },
        headers=auth_headers
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["message"] == "Updated"
    assert data["events"][0]["title"] == "Updated Study Session"
    assert data["events"][0]["description"] == "Review chapters 1 and 2"


# Test deleting event successfully and ensure it is removed from database
def test_calendar_08(client, auth_headers):
    create_response = client.post(
        "/calendar/create_events",
        json={
            "title": "Delete Me",
            "description": "Temporary event",
            "start_time": "2026-04-22T09:00:00",
            "end_time": "2026-04-22T10:00:00",
            "item_type": "event"
        },
        headers=auth_headers
    )

    event_id = create_response.get_json()["events"][0]["id"]

    response = client.delete(
        f"/calendar/event/{event_id}", 
        headers=auth_headers
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "Event deleted"

    response_after = client.get(
        "/calendar/events", 
        headers=auth_headers
    )
    data_after = response_after.get_json()

    assert len(data_after) == 0

# Test deleting non-existent event and ensure proper error message is returned
def test_calendar_09(client, auth_headers):
    response = client.delete(
        "/calendar/event/9999", 
        headers=auth_headers
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Event not found"