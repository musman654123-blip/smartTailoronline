from flask import Flask, request, redirect, session
import sqlite3, os, shutil
from datetime import datetime

ADMIN_PASSWORD = "admin123"
app = Flask(__name__)
app.secret_key = "smart-tailor-secret"
DB_FILE = "data.db"

# ---------------- DATABASE ----------------
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

# ---------------- BACKUP ----------------
def backup_db():
    if not os.path.exists("backup"):
        os.mkdir("backup")
    shutil.copy(DB_FILE, f"backup/data_{datetime.now().strftime('%Y%m%d_%H%M')}.db")

# ---------------- LICENSE ----------------
def check_license(code):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM licenses WHERE license=? AND status='active'", (code,))
    row = cur.fetchone()
    conn.close()
    return row

def update_last_login(code):
    conn = get_db()
    conn.execute("UPDATE licenses SET last_login=? WHERE license=?", (datetime.now().strftime("%Y-%m-%d %H:%M"), code))
    conn.commit()
    conn.close()

# ---------------- LOGIN (TAILOR) ----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        code = request.form.get("license")
        lic = check_license(code)
        if lic:
            session["license"] = code
            update_last_login(code)
            return redirect("/main")
        return "<h3>Invalid or Blocked License</h3>"
    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <h2>Smart Tailor Login</h2>
    <form method="post">
        <input name="license" placeholder="Enter License" required><br><br>
        <button>Login</button>
    </form>
    """

# ---------------- MAIN (TAILOR) ----------------
@app.route("/main")
def main():
    if "license" not in session:
        return redirect("/")
    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <h2>Add Customer</h2>
    <form method="post" action="/add">
      Name: <input name="name" required><br><br>
      Mobile: <input name="mobile" required><br><br>
      Length: <input name="length"><br><br>
      Chest: <input name="chest"><br><br>
      Waist: <input name="waist"><br><br>
      Shoulder: <input name="shoulder"><br><br>
      Poncha: <input name="poncha"><br><br>
      Batton: <input name="batton"><br><br>
      Packet: <input name="packet"><br><br>
      Zip: <input name="zip"><br><br>
      Shalwar: <input name="shalwar"><br><br>
      Collar: <input name="collar"><br><br>
      Ghara: <input name="ghara"><br><br>
      Amount: <input name="amount"><br><br>
      <button style="width:100%;padding:10px;">Save Customer</button>
    </form>
    <br><a href="/list">📋 View Customers</a><br>
    <a href="/logout">🚪 Logout</a>
    """

# ---------------- ADD CUSTOMER ----------------
@app.route("/add", methods=["POST"])
def add():
    if "license" not in session:
        return redirect("/")
    conn = get_db()
    conn.execute("""
    INSERT INTO customers
    (name,mobile,length,chest,waist,shoulder,poncha,batton,packet,zip,shalwar,collar,ghara,amount,created_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        request.form["name"],
        request.form["mobile"],
        request.form.get("length"),
        request.form.get("chest"),
        request.form.get("waist"),
        request.form.get("shoulder"),
        request.form.get("poncha"),
        request.form.get("batton"),
        request.form.get("packet"),
        request.form.get("zip"),
        request.form.get("shalwar"),
        request.form.get("collar"),
        request.form.get("ghara"),
        request.form.get("amount"),
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()
    backup_db()
    return redirect("/main")

# ---------------- VIEW CUSTOMERS ----------------
@app.route("/list")
def list_customers():
    if "license" not in session:
        return redirect("/")
    conn = get_db()
    rows = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    conn.close()
    html = "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    html += "<h2>Customers</h2>"
    for r in rows:
        html += f"""
        <p>
        <b>{r['name']}</b> |
        {r['mobile']} |
        L:{r['length']} C:{r['chest']} W:{r['waist']} |
        Shoulder:{r['shoulder']} Poncha:{r['poncha']} Batton:{r['batton']} Packet:{r['packet']} Zip:{r['zip']}<br>
        Shalwar:{r['shalwar']} Collar:{r['collar']} Ghara:{r['ghara']} Amount:{r['amount']}<br>
        Added:{r['created_at']}
        </p><hr>
        """
    html += '<br><a href="/main">🔙 Back</a>'
    return html

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- ADMIN LOGIN ----------------
@app.route("/admin-login", methods=["GET","POST"])
def admin_login():
    if request.method=="POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        return "<h3>Wrong Password</h3>"
    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <h2>Admin Login</h2>
    <form method="post">
      <input type="password" name="password" placeholder="Admin Password"><br><br>
      <button>Login</button>
    </form>
    """

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin-login")
    conn = get_db()
    licenses = conn.execute("SELECT * FROM licenses").fetchall()
    total_customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    active_licenses = conn.execute("SELECT COUNT(*) FROM licenses WHERE status='active'").fetchone()[0]
    blocked_licenses = conn.execute("SELECT COUNT(*) FROM licenses WHERE status='blocked'").fetchone()[0]
    conn.close()
    html = "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    html += f"<h2>Admin Dashboard</h2><p>Total Customers: {total_customers}<br>Active Licenses: {active_licenses}<br>Blocked Licenses: {blocked_licenses}</p>"
    html += "<table border=1 cellpadding=5><tr><th>License</th><th>Name</th><th>Status</th><th>Last Login</th><th>Action</th></tr>"
    for l in licenses:
        html += f"<tr><td>{l['license']}</td><td>{l['name']}</td><td>{l['status']}</td><td>{l['last_login'] or ''}</td>"
        html += f"<td><a href='/admin/activate/{l['license']}'>Activate</a> | <a href='/admin/block/{l['license']}'>Block</a></td></tr>"
    html += "</table><br>"
    html += """
    <h3>Add License</h3>
    <form method='post' action='/admin/add'>
      License: <input name='license' required><br>
      Name: <input name='name' required><br>
      <button>Add</button>
    </form>
    """
    return html

# ---------------- ADMIN ACTIONS ----------------
@app.route("/admin/add", methods=["POST"])
def admin_add():
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO licenses VALUES (?,?, 'active','')", (request.form["license"], request.form["name"]))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/admin/block/<code>")
def admin_block(code):
    conn = get_db()
    conn.execute("UPDATE licenses SET status='blocked', last_login='' WHERE license=?", (code,))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/admin/activate/<code>")
def admin_activate(code):
    conn = get_db()
    conn.execute("UPDATE licenses SET status='active' WHERE license=?", (code,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))