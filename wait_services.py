import time
import requests

deadline = time.monotonic() + 180
while time.monotonic() < deadline:
    try:
        for host in ("web-gw0", "web-gw1"):
            response = requests.get(f"http://{host}:5000/api/users", timeout=3)
            response.raise_for_status()
        grid = requests.get(
            "http://selenium-hub:4444/status", timeout=3
        ).json()["value"]
        slots = sum(len(node.get("slots", [])) for node in grid.get("nodes", []))
        if grid["ready"] and slots >= 2:
            print("Web services and Selenium Grid are ready", flush=True)
            break
    except (requests.RequestException, KeyError, ValueError):
        pass
    time.sleep(2)
else:
    raise SystemExit("Services did not become ready within 180 seconds")
