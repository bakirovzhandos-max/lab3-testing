import html
import json
from pathlib import Path
from uuid import uuid4

import requests

BASE = "http://127.0.0.1:5000"
API = BASE + "/api/users"
checks = []
findings = []


def record(name, passed, detail):
    checks.append({
        "check": name,
        "passed": passed,
        "detail": detail,
    })
    print(f"{'PASS' if passed else 'FAIL'}: {name} — {detail}")


def create(name):
    return requests.post(
        API,
        json={"name": name, "email": uuid4().hex + "@test.com"},
        timeout=10,
    )


# SQL payload must be handled as data, not executed.
payload = "Robert'); DROP TABLE users;--"
response = create(payload)
sql_ok = response.status_code == 201

if sql_ok:
    user_id = response.json()["id"]
    users = requests.get(API, timeout=10)
    sql_ok = (
        users.status_code == 200
        and any(
            u["id"] == user_id and u["name"] == payload
            for u in users.json()
        )
    )
    # Confirm the table still supports new inserts.
    probe = create("AfterSQL")
    sql_ok = sql_ok and probe.status_code == 201

record(
    "SQL injection",
    sql_ok,
    "Payload stored as text; users table remains operational",
)

# Check output escaping in the HTML page.
xss = "<script>alert('XSS')</script>"
response = create(xss)
page = requests.get(BASE + "/", timeout=10)

record(
    "XSS output escaping",
    response.status_code == 201
    and page.status_code == 200
    and xss not in page.text
    and html.escape(xss) in page.text,
    "Script markup must be HTML-escaped in the users list",
)

response = requests.post(
    API, json={"name": "MissingEmail"}, timeout=10
)
record(
    "Missing required field",
    response.status_code == 400,
    f"HTTP {response.status_code}; expected 400",
)

response = requests.post(
    API,
    data="{broken",
    headers={"Content-Type": "application/json"},
    timeout=10,
)
record(
    "Malformed JSON",
    response.status_code == 400,
    f"HTTP {response.status_code}; expected 400",
)

# Audit unauthenticated access to the application's own test data.
response = requests.get(API, timeout=10)
if response.status_code == 200:
    findings.append({
        "issue": "Users API accessible without authentication",
        "evidence": "Unauthenticated GET /api/users returned 200",
        "recommendation": "Require authentication and restrict data access",
    })

created = create("AuthorizationProbe")
if created.status_code == 201:
    user_id = created.json()["id"]
    deleted = requests.delete(f"{API}/{user_id}", timeout=10)
    after = requests.get(API, timeout=10)
    if (
        deleted.status_code == 204
        and after.status_code == 200
        and not any(u["id"] == user_id for u in after.json())
    ):
        findings.append({
            "issue": "User deletion lacks authorization checks",
            "evidence": "Unauthenticated DELETE returned 204 and removed the user",
            "recommendation": "Check identity, role and permission before deletion",
        })

for header, recommendation in [
    (
        "Content-Security-Policy",
        "Define a Content Security Policy appropriate for the application",
    ),
    (
        "X-Content-Type-Options",
        "Set X-Content-Type-Options: nosniff",
    ),
]:
    if header not in page.headers:
        findings.append({
            "issue": f"Missing {header}",
            "evidence": f"GET / response does not contain {header}",
            "recommendation": recommendation,
        })

for finding in findings:
    print("FINDING:", finding["issue"])
    print("EVIDENCE:", finding["evidence"])

Path("security_reports").mkdir(exist_ok=True)
Path("security_reports/api_security.json").write_text(
    json.dumps(
        {"checks": checks, "findings": findings},
        indent=2,
        ensure_ascii=False,
    ),
    encoding="utf-8",
)

if not all(check["passed"] for check in checks):
    raise SystemExit("One or more security regression checks failed")
