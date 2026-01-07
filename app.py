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
    machine_id TEXT,
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
    machine_id = get_machine_id()
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM licenses WHERE license=?", (code,))
    lic = cur.fetchone()

    if not lic or lic["status"] != "active":
        conn.close()
        return "invalid"

    # first time login → bind machine
    if lic["machine_id"] is None or lic["machine_id"] == "":
        cur.execute(
            "UPDATE licenses SET machine_id=?, last_login=? WHERE license=?",
            (machine_id, datetime.now().strftime("%Y-%m-%d %H:%M"), code)
        )
        conn.commit()
        conn.close()
        return "ok"

    # already used on another system
    if lic["machine_id"] != machine_id:
        conn.close()
        return "used_on_other_system"

    # same system login
    cur.execute(
        "UPDATE licenses SET last_login=? WHERE license=?",
        (datetime.now().strftime("%Y-%m-%d %H:%M"), code)
    )
    conn.commit()
    conn.close()
    return "ok"

def update_last_login(code):
    conn = get_db()
    conn.execute("UPDATE licenses SET last_login=? WHERE license=?", (datetime.now().strftime("%Y-%m-%d %H:%M"), code))
    conn.commit()
    conn.close()

# ---------------- LOGIN (TAILOR) ----------------
# ---------------- LOGIN (TAILOR) ----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        code = request.form.get("license")
        lic = check_license(code)
        if lic:
            session["license"] = code
            update_last_login(code)
            return redirect("/main")
        # ❌ Corrected line
        return "<h3 style='color:red'>❌ Invalid or Blocked License</h3>"

    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <h2 style='text-align:center;color:green;'>Smart Tailor Login</h2>
    <div style='max-width:400px;margin:auto;padding:20px;border:2px solid #4CAF50;border-radius:10px;background:#f2f2f2'>
        <form method="post">
            <input name="license" placeholder="Enter License" required style='width:100%;padding:10px;margin:10px 0;border-radius:5px;border:1px solid #ccc;'><br>
            <button style='width:100%;padding:10px;background:#4CAF50;color:white;border:none;border-radius:5px;font-size:16px;'>Login</button>
        </form>
    </div>
    """

# ---------------- MAIN (TAILOR) ----------------
@app.route("/main")
def main():
    if "license" not in session:
        return redirect("/")
    return """
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <div style='max-width:600px;margin:auto;padding:20px;background:#f9f9f9;border-radius:10px;border:2px solid #4CAF50'>
    <h2 style='color:#4CAF50;'>Add Customer</h2>

    <h3>Search Customer</h3>
    <form method="get" action="/search" style='margin-bottom:20px;'>
        <input type="text" name="query" placeholder="Enter Name or Mobile" required style='width:70%;padding:10px;border-radius:5px;border:1px solid #ccc;'>
        <button type="submit" style='padding:10px;background:#2196F3;color:white;border:none;border-radius:5px;'>Search</button>
    </form>

    <form method="post" action="/add">
      Name: <input name="name" required style='width:100%;padding:10px;margin:5px 0;'><br>
      Mobile: <input name="mobile" required style='width:100%;padding:10px;margin:5px 0;'><br>
      Length: <input name="length" style='width:100%;padding:10px;margin:5px 0;'><br>
      Chest: <input name="chest" style='width:100%;padding:10px;margin:5px 0;'><br>
      Waist: <input name="waist" style='width:100%;padding:10px;margin:5px 0;'><br>
      Shoulder: <input name="shoulder" style='width:100%;padding:10px;margin:5px 0;'><br>
      Poncha: <input name="poncha" style='width:100%;padding:10px;margin:5px 0;'><br>
      Batton: <input name="batton" style='width:100%;padding:10px;margin:5px 0;'><br>
      Packet: <input name="packet" style='width:100%;padding:10px;margin:5px 0;'><br>
      Zip: <input name="zip" style='width:100%;padding:10px;margin:5px 0;'><br>
      Shalwar: <input name="shalwar" style='width:100%;padding:10px;margin:5px 0;'><br>
      Collar: <input name="collar" style='width:100%;padding:10px;margin:5px 0;'><br>
      Ghara: <input name="ghara" style='width:100%;padding:10px;margin:5px 0;'><br>
      Amount: <input name="amount" style='width:100%;padding:10px;margin:5px 0;'><br><br>
      <button style='width:100%;padding:10px;background:#4CAF50;color:white;border:none;border-radius:5px;'>Save Customer</button>
    </form>
    <br>
    <a href="/list" style='display:inline-block;margin:5px;padding:10px;background:#2196F3;color:white;border-radius:5px;text-decoration:none;'>📋 View Customers</a>
    <a href="/logout" style='display:inline-block;margin:5px;padding:10px;background:#f44336;color:white;border-radius:5px;text-decoration:none;'>🚪 Logout</a>
    </div>
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

# ---------------- SEARCH CUSTOMER ----------------
@app.route("/search")
def search_customer():
    if "license" not in session:
        return redirect("/")
    query = request.args.get("query", "").strip()
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM customers WHERE name LIKE ? OR mobile LIKE ? ORDER BY id DESC",
        (f"%{query}%", f"%{query}%")
    ).fetchall()
    conn.close()
    html = "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    html += f"<h2 style='color:#4CAF50;'>Search Results for '{query}'</h2>"
    if not rows:
        html += "<p>No customer found.</p>"
    else:
        for r in rows:
            html += f"""
            <p>
            <b>{r['name']}</b> | {r['mobile']}<br>
            L:{r['length']} C:{r['chest']} W:{r['waist']} |
            Shoulder:{r['shoulder']} Poncha:{r['poncha']} Batton:{r['batton']} Packet:{r['packet']} Zip:{r['zip']}<br>
            Shalwar:{r['shalwar']} Collar:{r['collar']} Ghara:{r['ghara']} Amount:{r['amount']}<br>
            Added:{r['created_at']}
            </p><hr>
            """
    html += '<br><a href="/main" style="padding:10px;background:#2196F3;color:white;text-decoration:none;border-radius:5px;">🔙 Back</a>'
    return html

# ---------------- VIEW CUSTOMERS ----------------
@app.route("/list")
def list_customers():
    if "license" not in session:
        return redirect("/")
    conn = get_db()
    rows = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    conn.close()
    html = "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
    html += "<h2 style='color:#4CAF50;'>All Customers</h2>"
    for r in rows:
        html += f"""
        <p>
        <b>{r['name']}</b> | {r['mobile']}<br>
        L:{r['length']} C:{r['chest']} W:{r['waist']} |
        Shoulder:{r['shoulder']} Poncha:{r['poncha']} Batton:{r['batton']} Packet:{r['packet']} Zip:{r['zip']}<br>
        Shalwar:{r['shalwar']} Collar:{r['collar']} Ghara:{r['ghara']} Amount:{r['amount']}<br>
        Added:{r['created_at']}
        </p><hr>
        """
    html += '<br><a href="/main" style="padding:10px;background:#2196F3;color:white;text-decoration:none;border-radius:5px;">🔙 Back</a>'
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
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <h2 style='color:#4CAF50;'>Admin Login</h2>
    <form method='post'>
      <input type='password' name='password' placeholder='Admin Password' style='width:100%;padding:10px;margin:10px 0;border-radius:5px;border:1px solid #ccc;'><br>
      <button style='width:100%;padding:10px;background:#4CAF50;color:white;border:none;border-radius:5px;'>Login</button>
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
    html += f"<h2 style='color:#4CAF50;'>Admin Dashboard</h2>"
    html += f"<p>Total Customers: {total_customers}<br>Active Licenses: {active_licenses}<br>Blocked Licenses: {blocked_licenses}</p>"
    html += "<table border=1 cellpadding=5 style='border-collapse:collapse;width:100%;'>"
    html += "<tr style='background:#4CAF50;color:white;'><th>License</th><th>Name</th><th>Status</th><th>Last Login</th><th>Action</th></tr>"
    for l in licenses:
        html += f"<tr><td>{l['license']}</td><td>{l['name']}</td><td>{l['status']}</td><td>{l['last_login'] or ''}</td>"
        html += f"<td><a href='/admin/activate/{l['license']}' style='padding:5px;background:#2196F3;color:white;border-radius:3px;text-decoration:none;'>Activate</a> | "
        html += f"<a href='/admin/block/{l['license']}' style='padding:5px;background:#f44336;color:white;border-radius:3px;text-decoration:none;'>Block</a></td></tr>"
    html += "</table><br>"
    html += """
    <h3>Add License</h3>
    <td>{l['machine_id'] or ''}</td>
    <form method='post' action='/admin/add'>
      License: <input name='license' required style='padding:5px;margin:5px;'><br>
      Name: <input name='name' required style='padding:5px;margin:5px;'><br>
      <button style='padding:5px;background:#4CAF50;color:white;border:none;border-radius:5px;'>Add</button>
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