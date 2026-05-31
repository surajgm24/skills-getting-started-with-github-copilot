import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: Reset the in-memory DB before each test
    for activity in activities.values():
        # Remove all test emails
        activity["participants"] = [p for p in activity["participants"] if not p.endswith("@test.com")]


def test_get_activities():
    # Arrange
    # (No setup needed, DB is already initialized)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_success():
    # Arrange
    email = "alice@test.com"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]
    assert "Signed up" in response.json()["message"]


def test_signup_duplicate():
    # Arrange
    email = "bob@test.com"
    activity = "Chess Club"
    activities[activity]["participants"].append(email)

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_not_found():
    # Arrange
    email = "carol@test.com"
    activity = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_unregister_success():
    # Arrange
    email = "dave@test.com"
    activity = "Chess Club"
    activities[activity]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]
    assert "Unregistered" in response.json()["message"]


def test_unregister_not_registered():
    # Arrange
    email = "eve@test.com"
    activity = "Chess Club"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "Student not registered" in response.json()["detail"]


def test_unregister_activity_not_found():
    # Arrange
    email = "frank@test.com"
    activity = "Nonexistent Club"

    # Act
    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]
