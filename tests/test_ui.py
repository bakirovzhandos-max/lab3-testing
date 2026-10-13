import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_ui_register_user(driver, server_url, api_url, logger):
    logger.info("UI: register user")
    driver.get(server_url + "/register")
    driver.find_element(By.NAME, "name").send_keys("Ivan")
    driver.find_element(By.NAME, "email").send_keys("ivan@test.com")
    driver.find_element(By.TAG_NAME, "button").click()
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), "Users List")
    )
    assert "Ivan (ivan@test.com)" in driver.find_element(
        By.TAG_NAME, "body"
    ).text
    users = requests.get(api_url, timeout=10)
    assert users.status_code == 200
    assert users.json()[0]["email"] == "ivan@test.com"

def test_ui_register_without_email(driver, server_url, api_url, logger):
    logger.info("UI: missing email")
    driver.get(server_url + "/register")
    driver.find_element(By.NAME, "name").send_keys("NoEmail")
    driver.find_element(By.TAG_NAME, "button").click()
    assert driver.current_url.endswith("/register")
    assert driver.execute_script(
        "return document.querySelector('[name=email]').validity.valueMissing"
    )
    users = requests.get(api_url, timeout=10)
    assert users.status_code == 200
    assert users.json() == []

def test_ui_register_without_name(driver, server_url, api_url, logger):
    logger.info("UI: missing name")
    driver.get(server_url + "/register")
    driver.find_element(By.NAME, "email").send_keys("no_name@test.com")
    driver.find_element(By.TAG_NAME, "button").click()
    assert driver.current_url.endswith("/register")
    assert driver.execute_script(
        "return document.querySelector('[name=name]').validity.valueMissing"
    )
    users = requests.get(api_url, timeout=10)
    assert users.status_code == 200
    assert users.json() == []

