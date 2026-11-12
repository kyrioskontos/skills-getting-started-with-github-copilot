import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

TEST_ACTIVITY = "Test Activity"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_activity(monkeypatch):
    activity = {
        "description": "A test activity",
        "schedule": "Mondays",
        "max_participants": 5,
        "participants": ["existing@example.edu"],
    }
    monkeypatch.setitem(activities, TEST_ACTIVITY, activity)
    return activity


def test_get_activities_returns_available_activities(client, test_activity):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()[TEST_ACTIVITY] == test_activity


def test_signup_adds_participant(client, test_activity):
    email = "new@example.edu"

    response = client.post(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {TEST_ACTIVITY}"}
    assert email in test_activity["participants"]


def test_signup_rejects_duplicate_participant(client, test_activity):
    response = client.post(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": "existing@example.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "new@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client, test_activity):
    email = "existing@example.edu"
    test_activity["participants"].append(email)

    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {TEST_ACTIVITY}"}
    assert email not in test_activity["participants"]


def test_unregister_rejects_missing_participant(client, test_activity):
    response = client.delete(
        f"/activities/{TEST_ACTIVITY}/signup",
        params={"email": "missing@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown/signup",
        params={"email": "student@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
