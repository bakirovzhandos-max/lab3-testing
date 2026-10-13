from uuid import uuid4
from locust import HttpUser, task, between


class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_users(self):
        with self.client.get(
            "/api/users", catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")

    @task(1)
    def create_user(self):
        payload = {
            "name": "user_" + uuid4().hex[:8],
            "email": uuid4().hex + "@test.com",
        }
        with self.client.post(
            "/api/users", json=payload, catch_response=True
        ) as response:
            if response.status_code != 201:
                response.failure(f"Expected 201, got {response.status_code}")
