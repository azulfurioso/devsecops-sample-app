from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route("/user")
def get_user():
    name = request.args.get("name")
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")  # 🚩
    # cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    return str(cursor.fetchall())
