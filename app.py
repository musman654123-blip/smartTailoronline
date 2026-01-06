from flask import Flask, request, redirect
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_FILE = "data.db"

# ---------------- DATABASE SETUP ----------------
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mobile TEXT,
        length TEXT,
        chest TEXT,
        waist TEXT,
        shoulder TEXT,
        poncha TEXT,
        batton TEXT,
        packet TEXT,
        zip TEXT,
        shalwar TEXT,
        collar TEXT,
        ghara TEXT,
        amount TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS licenses (
        license TEXT PRIMARY KEY,
        name TEXT,
        status TEXT,
        last_login TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- LICENSE CHECK ----------------
def check_license(code):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM licenses WHERE license=? AND status='active'", (code,))
    row = cur.fetchone()
    conn.close()
    return row is not None

def update_last_login(code):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE licenses SET last_login=? WHERE license=?",
        (datetime.now().strftime("%Y-%m-%d %H:%M"), code)
    )
    conn.commit()
    conn.close()

# ---------------- LICENSE PAGE ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        code = request.form.get("license").strip()
        if check_license(code):
            update_last_login(code)
            return redirect("/main")
        return "<h3>Invalid / Blocked License</h3>"
    return """
    <h2>Enter License</h2>
    <form method="post">
      <input name="license" required>
      <button>Enter</button>
    </form>
    """

# ---------------- MAIN APP ----------------
@app.route("/main")
def main_page():
    return """
    <h2>Add Customer</h2>
    <form method="post" action="/add">
      Name:<input name="name"><br>
      Mobile:<input name="mobile"><br>
      Length:<input name="length"><br>
      Chest:<input name="chest"><br>
      Waist:<input name="waist"><br>
      <button>Save</button>
    </form>
    <a href="/list">View Customers</a>
    """

# ---------------- ADD CUSTOMER ----------------
@app.route("/add", methods=["POST"])
def add():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO customers
    (name, mobile, length, chest, waist, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        request.form.get("name"),
        request.form.get("mobile"),
        request.form.get("length"),
        request.form.get("chest"),
        request.form.get("waist"),
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()
    return redirect("/main")

# ---------------- VIEW CUSTOMERS ----------------
@app.route("/list")
def list_customers():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    html = "<h2>All Customers</h2>"
    for r in rows:
        html += f"<p>{r['name']} - {r['mobile']} - {r['created_at']}</p>"
    return html
# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin_dashboard():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM licenses")
    licenses = cur.fetchall()
    conn.close()

    html = "<h2>Admin Dashboard</h2>"
    html += "<table border='1' cellpadding='5'>"
    html += "<tr><th>License</th><th>Name</th><th>Status</th><th>Last Login</th><th>Action</th></tr>"

    for l in licenses:
        html += f"""
        <tr>
          <td>{l['license']}</td>
          <td>{l['name']}</td>
          <td>{l['status']}</td>
          <td>{l['last_login'] or ''}</td>
          <td>
            <a href="/admin/activate/{l['license']}">Activate</a> |
            <a href="/admin/block/{l['license']}">Block</a>
          </td>
        </tr>
        """

    html += "</table><br>"

    html += """
    <h3>Add New License</h3>
    <form method="post" action="/admin/add">
      License: <input name="license"><br>
      Name: <input name="name"><br>
      <button>Add</button>
    </form>
    """
    return html


@app.route("/admin/add", methods=["POST"])
def admin_add():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO licenses (license, name, status, last_login) VALUES (?, ?, ?, ?)",
        (request.form["license"], request.form["name"], "active", "")
    )
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/admin/block/<code>")
def admin_block(code):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE licenses SET status='blocked', last_login='' WHERE license=?", (code,))
    conn.commit()
    conn.close()
    return redirect("/admin")


@app.route("/admin/activate/<code>")
def admin_activate(code):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE licenses SET status='active' WHERE license=?", (code,))
    conn.commit()
    conn.close()
    return redirect("/admin")
# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)