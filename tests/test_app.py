from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    response = client.delete("/activities/Chess Club/participants", params={"email": "daniel@mergington.edu"})

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered daniel@mergington.edu from Chess Club"

    activities = client.get("/activities").json()
    assert "daniel@mergington.edu" not in activities["Chess Club"]["participants"]

    # restore state for the next test run
    client.post("/activities/Chess Club/signup", params={"email": "daniel@mergington.edu"})


def test_unregister_participant_fails_for_missing_email():
    response = client.delete("/activities/Gym Class/participants", params={"email": "missing@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
