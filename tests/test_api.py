import requests

def test_api_create_user(api_url, logger):
    logger.info("API: create user")
    payload = {"name": "Ivan", "email": "ivan@test.com"}
    response = requests.post(api_url, json=payload, timeout=10)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert isinstance(data["id"], int)

def test_api_get_users(api_url, logger):
    logger.info("API: get users")
    payload = {"name": "Ivan", "email": "ivan@test.com"}
    created = requests.post(api_url, json=payload, timeout=10)
    assert created.status_code == 201
    response = requests.get(api_url, timeout=10)
    assert response.status_code == 200
    assert response.json() == [created.json()]

def test_api_create_duplicate_user(api_url, logger):
    logger.info("API: duplicate email")
    payload = {"name": "Ivan", "email": "ivan@test.com"}
    first = requests.post(api_url, json=payload, timeout=10)
    assert first.status_code == 201
    second = requests.post(api_url, json=payload, timeout=10)
    assert second.status_code == 400
    assert second.json()["error"] == "Email already exists"
    users = requests.get(api_url, timeout=10)
    assert users.status_code == 200
    assert users.json() == [first.json()]

def test_api_delete_user(api_url, logger):
    logger.info("API: delete user")
    created = requests.post(api_url, json={
        "name": "Alex", "email": "alex@test.com"
    }, timeout=10)
    assert created.status_code == 201
    response = requests.delete(
        f"{api_url}/{created.json()['id']}", timeout=10
    )
    assert response.status_code == 204
    users = requests.get(api_url, timeout=10)
    assert users.status_code == 200
    assert users.json() == []
