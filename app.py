from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import date, timedelta
from pathlib import Path

app = Flask(__name__)
DB = Path(__file__).with_name("habits.db")

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT DEFAULT 'Personal',
            created_at TEXT NOT NULL
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            check_date TEXT NOT NULL,
            UNIQUE(habit_id, check_date),
            FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )""")
        count = con.execute("SELECT COUNT(*) FROM habits").fetchone()[0]
        if count == 0:
            today = date.today().isoformat()
            con.executemany("INSERT INTO habits(name,category,created_at) VALUES(?,?,?)", [
                ("Read for 20 minutes", "Learning", today),
                ("Drink 8 glasses of water", "Health", today),
                ("Practice coding", "Career", today)
            ])

def habit_payload(row):
    return {"id": row["id"], "name": row["name"], "category": row["category"]}

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/habits")
def get_habits():
    today = date.today().isoformat()
    with db() as con:
        rows = con.execute("SELECT * FROM habits ORDER BY id DESC").fetchall()
        items = []
        for row in rows:
            item = habit_payload(row)
            item["done_today"] = con.execute(
                "SELECT 1 FROM checkins WHERE habit_id=? AND check_date=?", (row["id"], today)
            ).fetchone() is not None
            item["streak"] = streak_for(con, row["id"])
            items.append(item)
    return jsonify(items)

def streak_for(con, habit_id):
    days = {r[0] for r in con.execute(
        "SELECT check_date FROM checkins WHERE habit_id=?", (habit_id,)
    ).fetchall()}
    cursor = date.today()
    if cursor.isoformat() not in days:
        cursor -= timedelta(days=1)
    streak = 0
    while cursor.isoformat() in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak

@app.post("/api/habits")
def add_habit():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    category = (data.get("category") or "Personal").strip()[:40]
    if not name:
        return jsonify({"error": "Habit name is required."}), 400
    with db() as con:
        cur = con.execute("INSERT INTO habits(name,category,created_at) VALUES(?,?,?)",
                          (name[:100], category, date.today().isoformat()))
        habit_id = cur.lastrowid
    return jsonify({"id": habit_id, "name": name[:100], "category": category}), 201

@app.put("/api/habits/<int:habit_id>")
def edit_habit(habit_id):
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    category = (data.get("category") or "Personal").strip()[:40]
    if not name:
        return jsonify({"error": "Habit name is required."}), 400
    with db() as con:
        cur = con.execute("UPDATE habits SET name=?, category=? WHERE id=?",
                          (name[:100], category, habit_id))
        if cur.rowcount == 0:
            return jsonify({"error": "Habit not found."}), 404
    return jsonify({"message": "Habit updated."})

@app.delete("/api/habits/<int:habit_id>")
def delete_habit(habit_id):
    with db() as con:
        con.execute("DELETE FROM checkins WHERE habit_id=?", (habit_id,))
        cur = con.execute("DELETE FROM habits WHERE id=?", (habit_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "Habit not found."}), 404
    return jsonify({"message": "Habit deleted."})

@app.post("/api/habits/<int:habit_id>/checkin")
def checkin(habit_id):
    data = request.get_json(silent=True) or {}
    check_date = data.get("date") or date.today().isoformat()
    with db() as con:
        exists = con.execute("SELECT id FROM habits WHERE id=?", (habit_id,)).fetchone()
        if not exists:
            return jsonify({"error": "Habit not found."}), 404
        already = con.execute("SELECT id FROM checkins WHERE habit_id=? AND check_date=?",
                              (habit_id, check_date)).fetchone()
        if already:
            con.execute("DELETE FROM checkins WHERE id=?", (already["id"],))
            done = False
        else:
            con.execute("INSERT INTO checkins(habit_id,check_date) VALUES(?,?)",
                        (habit_id, check_date))
            done = True
    return jsonify({"done": done, "date": check_date})

@app.get("/api/stats")
def stats():
    today = date.today().isoformat()
    week_start = date.today() - timedelta(days=6)
    with db() as con:
        total = con.execute("SELECT COUNT(*) FROM habits").fetchone()[0]
        done = con.execute("SELECT COUNT(*) FROM checkins WHERE check_date=?", (today,)).fetchone()[0]
        week = con.execute("""SELECT check_date, COUNT(*) AS total FROM checkins
                              WHERE check_date>=? GROUP BY check_date ORDER BY check_date""",
                           (week_start.isoformat(),)).fetchall()
    counts = {r["check_date"]: r["total"] for r in week}
    weekly = [{"day": (week_start + timedelta(days=i)).strftime("%a"),
               "count": counts.get((week_start + timedelta(days=i)).isoformat(), 0)}
              for i in range(7)]
    return jsonify({"total_habits": total, "completed_today": done,
                    "completion_percent": round(done / total * 100) if total else 0,
                    "weekly": weekly})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
