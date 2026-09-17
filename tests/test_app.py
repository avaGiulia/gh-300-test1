import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities_state():
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


def test_get_activities_returns_all_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_email_and_returns_success():
    response = client.post("/activities/Chess Club/signup", params={"email": "newstudent@mergington.edu"})

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert "newstudent@mergington.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_email():
    response = client.post("/activities/Chess Club/signup", params={"email": "daniel@mergington.edu"})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_participant_removes_email_from_activity():
    response = client.delete("/activities/Chess Club/participants", params={"email": "daniel@mergington.edu"})

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered daniel@mergington.edu from Chess Club"
    assert "daniel@mergington.edu" not in app_module.activities["Chess Club"]["participants"]


def test_unregister_participant_fails_for_missing_email():
    response = client.delete("/activities/Gym Class/participants", params={"email": "missing@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_unknown_activity_returns_404_for_signup_and_unregister():
    signup_response = client.post("/activities/Unknown Club/signup", params={"email": "student@mergington.edu"})
    unregister_response = client.delete("/activities/Unknown Club/participants", params={"email": "student@mergington.edu"})

    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"
    assert unregister_response.status_code == 404
    assert unregister_response.json()["detail"] == "Activity not found"
