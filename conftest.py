import os
import sqlite3
from contextlib import closing
import pytest
from selenium import webdriver
from logger import get_logger

@pytest.fixture(scope="session")
def server_url(worker_id):
    assert worker_id in ("gw0", "gw1")
    return f"http://web-{worker_id}:5000"

@pytest.fixture(scope="session")
def db_path(worker_id):
    return f"/data/users-{worker_id}.db"

@pytest.fixture(autouse=True)
def clear_db(db_path, server_url):
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute("DELETE FROM users")
        conn.commit()
    yield
    with closing(sqlite3.connect(db_path)) as conn:
        conn.execute("DELETE FROM users")
        conn.commit()

@pytest.fixture(scope="session")
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    browser = webdriver.Remote(
        command_executor="http://selenium-hub:4444",
        options=options
    )
    try:
        yield browser
    finally:
        browser.quit()

@pytest.fixture
def api_url(server_url):
    return server_url + "/api/users"

@pytest.fixture
def logger(worker_id):
    return get_logger(f"lab3.{worker_id}")

def pytest_configure(config):
    worker = os.environ.get("PYTEST_XDIST_WORKER", "controller")
    config.option.log_file = f"/reports/tests-{worker}.log"
