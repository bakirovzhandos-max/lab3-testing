from pathlib import Path
import os
from contextlib import closing
import sqlite3
from flask import Flask, request, jsonify, render_template, redirect, url_for

app = Flask(__name__)
DB = os.environ.get("DB_PATH", str(Path(__file__).with_name("users.db")))

def init_db():
    with closing(sqlite3.connect(DB)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)
        conn.commit()

def get_users():
    with closing(sqlite3.connect(DB)) as conn:
        return conn.execute(
            "SELECT id, name, email FROM users ORDER BY id"
        ).fetchall()

def add_user(name, email):
    with closing(sqlite3.connect(DB)) as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email)
        )
        conn.commit()
        return cursor.lastrowid

@app.route("/")
def index():
    return render_template("index.html", users=get_users())

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        if not name or not email:
            return "Name and email are required", 400
        try:
            add_user(name, email)
        except sqlite3.IntegrityError:
            return "Email already exists", 400
        return redirect(url_for("index"))
    return render_template("register.html")

@app.get("/api/users")
def api_get_users():
    return jsonify([
        {"id": u[0], "name": u[1], "email": u[2]}
        for u in get_users()
    ])

@app.post("/api/users")
def api_create_user():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="JSON object required"), 400
    name = data.get("name")
    email = data.get("email")
    if not isinstance(name, str) or not isinstance(email, str):
        return jsonify(error="Name and email required"), 400
    name, email = name.strip(), email.strip()
    if not name or not email:
        return jsonify(error="Name and email required"), 400
    try:
        user_id = add_user(name, email)
    except sqlite3.IntegrityError:
        return jsonify(error="Email already exists"), 400
    return jsonify(id=user_id, name=name, email=email), 201

@app.delete("/api/users/<int:user_id>")
def api_delete_user(user_id):
    with closing(sqlite3.connect(DB)) as conn:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    return "", 204

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)

