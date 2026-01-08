from flask import Flask, request, redirect, session
import sqlite3, os, shutil
from datetime import datetime
import uuid

ADMIN_PASSWORD = "admin123"
app = Flask(__name__)
app.secret_key = "smart-tailor-secret"
DB_FILE = "data.db"

def get_machine_id():
    return str(uuid.getnode())

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_columns(table, required_cols):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    existing = [c[1] for c in cur.fetchall()]
    for col, col_type in required_cols.items():
        if col not in existing:
            cur.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
    conn.commit()
    conn.close()

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
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

    ensure_columns("licenses", {
        "machine_id": "TEXT",
        "last_login": "TEXT",
        "last_ip": "TEXT"
    })

init_db()

# ---------------- BACKUP ----------------
def backup_db():
    if not os.path.exists("backup"):
        os.mkdir("backup")
    shutil.copy(DB_FILE, f"backup/data_{datetime.now().strftime('%Y%m%d_%H%M')}.db")

# ---------------- LICENSE ----------------
def check_license(code, current_ip=None):
    machine_id = get_machine_id()
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM licenses WHERE license=?", (code,))
    lic = cur.fetchone()

    if not lic or lic["status"] != "active":
        conn.close()
        return "invalid"

    if not lic["machine_id"]:
        cur.execute("""
            UPDATE licenses 
            SET machine_id=?, last_login=?, last_ip=? 
            WHERE license=?
        """, (machine_id, datetime.now().strftime("%Y-%m-%d %H:%M"), current_ip or "", code))
        conn.commit()
        conn.close()
        return "ok"

    if lic["machine_id"] != machine_id:
        conn.close()
        return "used_on_other_system"

    cur.execute("""
        UPDATE licenses 
        SET last_login=?, last_ip=? 
        WHERE license=?
    """, (datetime.now().strftime("%Y-%m-%d %H:%M"), current_ip or "", code))
    conn.commit()
    conn.close()
    return "ok"

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        code = request.form.get("license")
        status = check_license(code, request.remote_addr)
        if status == "ok":
            session["license"] = code
            return redirect("/main")
        return "<h3 style='color:red'>❌ Invalid / Used License</h3>"

    return """
    <h2>Smart Tailor Login</h2>
    <form method="post">
      <input name="license" placeholder="Enter License" required>
      <button>Login</button>
    </form>
    """

# ---------------- MAIN ----------------
@app.route("/main")
def main():
    if "license" not in session:
        return redirect("/")
    return "<h2>Smart Tailor System Running ✅</h2><a href='/logout'>Logout</a>"

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- ADMIN ----------------
@app.route("/admin-login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        return "Wrong Password"
    return "<form method='post'><input name='password'><button>Login</button></form>"

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin-login")
    conn = get_db()
    rows = conn.execute("SELECT * FROM licenses").fetchall()
    conn.close()
    html = "<h2>Licenses</h2>"
    for r in rows:
        html += f"<p>{r['license']} | {r['status']} | {r['machine_id']}</p>"
    html += """
    <form method='post' action='/admin/add'>
      <input name='license' placeholder='License'>
      <input name='name' placeholder='Name'>
      <button>Add</button>
    </form>
    """
    return html

@app.route("/admin/add", methods=["POST"])
def admin_add():
    conn = get_db()
    conn.execute("""
        INSERT OR REPLACE INTO licenses
        (license,name,status,machine_id,last_login,last_ip)
        VALUES (?,?,?,?,?,?)
    """, (request.form["license"], request.form["name"], "active", "", "", ""))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))