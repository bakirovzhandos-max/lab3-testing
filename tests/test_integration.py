import sqlite3
from contextlib import closing
import requests
from selenium.webdriver.common.by import By

def test_integration_api_ui_db(driver, server_url, api_url, db_path, logger):
    logger.info("Integration: API -> DB -> UI")
    response = requests.post(api_url, json={
        "name": "Alex", "email": "alex@test.com"
    }, timeout=10)
    assert response.status_code == 201
    user_id = response.json()["id"]
    with closing(sqlite3.connect(db_path)) as conn:
        user = conn.execute(
            "SELECT name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    assert user == ("Alex", "alex@test.com")
    driver.get(server_url)
    assert "Alex (alex@test.com)" in driver.find_element(
        By.TAG_NAME, "body"
    ).text

def test_integration_delete_user(driver, server_url, api_url, db_path, logger):
    logger.info("Integration: delete API -> DB -> UI")
    response = requests.post(api_url, json={
        "name": "DeleteUser", "email": "del@test.com"
    }, timeout=10)
    assert response.status_code == 201
    user_id = response.json()["id"]
    driver.get(server_url)
    assert "DeleteUser (del@test.com)" in driver.find_element(
        By.TAG_NAME, "body"
    ).text
    deleted = requests.delete(f"{api_url}/{user_id}", timeout=10)
    assert deleted.status_code == 204
    with closing(sqlite3.connect(db_path)) as conn:
        assert conn.execute(
            "SELECT id FROM users WHERE id = ?", (user_id,)
        ).fetchone() is None
    driver.refresh()
    assert "DeleteUser (del@test.com)" not in driver.find_element(
        By.TAG_NAME, "body"
    ).text
