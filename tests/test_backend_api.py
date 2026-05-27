from urllib.parse import quote


def test_root_redirects_to_static_index(client):
    # Arrange
    endpoint = "/"

    # Act
    response = client.get(endpoint, follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_payload_shape(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert {"description", "schedule", "max_participants", "participants"}.issubset(
        payload["Chess Club"].keys()
    )


def test_signup_for_activity_adds_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    activity_path = quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{activity_path}/signup", params={"email": email})
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in participants


def test_signup_duplicate_participant_returns_400_without_state_change(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    activity_path = quote(activity_name, safe="")
    before_count = len(client.get("/activities").json()[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_path}/signup", params={"email": email})
    after_count = len(client.get("/activities").json()[activity_name]["participants"])

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert after_count == before_count


def test_signup_nonexistent_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "new.student@mergington.edu"
    activity_path = quote(activity_name, safe="")

    # Act
    response = client.post(f"/activities/{activity_path}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_existing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    activity_path = quote(activity_name, safe="")

    # Act
    response = client.delete(f"/activities/{activity_path}/signup", params={"email": email})
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in participants


def test_unregister_nonexistent_activity_returns_404(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"
    activity_path = quote(activity_name, safe="")

    # Act
    response = client.delete(f"/activities/{activity_path}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_non_participant_returns_404_without_state_change(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not.signed.up@mergington.edu"
    activity_path = quote(activity_name, safe="")
    before_count = len(client.get("/activities").json()[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_path}/signup", params={"email": email})
    after_count = len(client.get("/activities").json()[activity_name]["participants"])

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"
    assert after_count == before_count