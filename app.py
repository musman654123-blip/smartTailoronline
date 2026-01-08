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
    # Customers table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mobile TEXT,
        length TEXT,
        chest TEXT,
        waist TEXT,
        shoulder TEXT,
        sleeve TEXT,
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
    # Licenses table
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
    lic = conn.execute("SELECT * FROM licenses WHERE license=?", (code,)).fetchone()
    conn.close()
    if lic and lic["status"] == "active":
        return True
    return False

def update_last_login(code):
    conn = get_db()
    conn.execute("UPDATE licenses SET last_login=? WHERE license=?",
                 (datetime.now().strftime("%Y-%m-%d %H:%M"), code))
    conn.commit()
    conn.close()

# ---------------- TAILOR LOGIN ----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        code = request.form.get("license")
        if check_license(code):
            session["license"] = code
            update_last_login(code)
            return redirect("/main")
        else:
            return "<h3 style='color:red;text-align:center'>❌ Invalid or Blocked License</h3>"
    return """
    <h2 style='text-align:center;color:green;'>Smart Tailor Login</h2>
    <form method="post" style='max-width:400px;margin:auto;padding:20px;border:2px solid #4CAF50;border-radius:10px;background:#f2f2f2'>
        <input name="license" placeholder="Enter License" required style='width:100%;padding:10px;margin:10px 0;border-radius:5px;border:1px solid #ccc;'><br>
        <button style='width:100%;padding:10px;background:#4CAF50;color:white;border:none;border-radius:5px;font-size:16px;'>Login</button>
    </form>
    """

# ---------------- MAIN (TAILOR) ----------------
@app.route("/main")
def main():
    if "license" not in session:
        return redirect("/")
    return """
    <div style='max-width:600px;margin:auto;padding:20px;background:#f9f9f9;border-radius:10px;border:2px solid #4CAF50'>
    <h2 style='color:#4CAF50;'>Add Customer</h2>
    <form method="post" action="/add">
      Name: <input name="name" required style='width:100%;padding:10px;margin:5px 0;'><br>
      Mobile: <input name="mobile" required style='width:100%;padding:10px;margin:5px 0;'><br>
      Length: <input name="length" style='width:100%;padding:10px;margin:5px 0;'><br>
      Chest: <input name="chest" style='width:100%;padding:10px;margin:5px 0;'><br>
      Waist: <input name="waist" style='width:100%;padding:10px;margin:5px 0;'><br>
      Shoulder: <input name="shoulder" style='width:100%;padding:10px;margin:5px 0;'><br>
      Sleeve: <input name="sleeve" style='width:100%;padding:10px;margin:5px 0;'><br>
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
    (name,mobile,length,chest,waist,shoulder,sleeve,poncha,batton,packet,zip,shalwar,collar,ghara,amount,created_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        request.form["name"],
        request.form["mobile"],
        request.form.get("length"),
        request.form.get("chest"),
        request.form.get("waist"),
        request.form.get("shoulder"),
        request.form.get("sleeve"),
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

# ---------------- LIST CUSTOMERS ----------------
@app.route("/list")
def list_customers():
    if "license" not in session:
        return redirect("/")
    conn = get_db()
    rows = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    conn.close()
    html = "<h2>All Customers</h2>"
    for r in rows:
        html += f"""
        <p><b>{r['name']}</b> | {r['mobile']}<br>
        L:{r['length']} C:{r['chest']} W:{r['waist']} S:{r['shoulder']} Sleeve:{r['sleeve']}<br>
        Poncha:{r['poncha']} Batton:{r['batton']} Packet:{r['packet']} Zip:{r['zip']}<br>
        Shalwar:{r['shalwar']} Collar:{r['collar']} Ghara:{r['ghara']} Amount:{r['amount']}<br>
        Added:{r['created_at']}
        </p><hr>
        """
    html += '<br><a href="/main">Back</a>'
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
        return "<h3 style='color:red'>❌ Wrong Password</h3>"
    return """
    <h2 style='text-align:center'>Admin Login</h2>
    <form method='post' style='max-width:300px;margin:auto'>
        <input name="password" placeholder="Password" required style='width:100%;padding:10px'><br><br>
        <button style='width:100%;padding:10px'>Login</button>
    </form>
    """

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin-login")
    conn = get_db()
    licenses = conn.execute("SELECT * FROM licenses").fetchall()
    active_count = conn.execute("SELECT COUNT(*) FROM licenses WHERE status='active'").fetchone()[0]
    conn.close()
    html = f"<h2>Admin Dashboard</h2><p>Active Licenses: {active_count}</p><hr>"
    html += "<table border=1 cellpadding=5 style='border-collapse:collapse;width:100%'>"
    html += "<tr style='background:#4CAF50;color:white;'><th>License</th><th>Name</th><th>Status</th><th>Last Login</th><th>Action</th></tr>"
    for l in licenses:
        html += f"<tr><td>{l['license']}</td><td>{l['name']}</td><td>{l['status']}</td><td>{l['last_login'] or ''}</td>"
        html += f"<td><a href='/admin/activate/{l['license']}'>Activate</a> | <a href='/admin/block/{l['license']}'>Block</a></td></tr>"
    html += "</table><hr>"
    html += """
    <h3>Add License</h3>
    <form method='post' action='/admin/add'>
        License: <input name='license' required><br>
        Name: <input name='name' required><br>
        <button>Add</button>
    </form>
    """
    return html

# ---------------- ADMIN ADD LICENSE ----------------
@app.route("/admin/add", methods=["POST"])
def admin_add():
    license_code = request.form["license"]
    name = request.form["name"]
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO licenses (license,name,status,last_login) VALUES (?,?,?,?)",
                 (license_code,name,"active",""))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ---------------- ADMIN BLOCK ----------------
@app.route("/admin/block/<lic>")
def admin_block(lic):
    if not session.get("admin"):
        return redirect("/admin-login")
    conn = get_db()
    conn.execute("UPDATE licenses SET status='blocked' WHERE license=?", (lic,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ---------------- ADMIN ACTIVATE ----------------
@app.route("/admin/activate/<lic>")
def admin_activate(lic):
    if not session.get("admin"):
        return redirect("/admin-login")
    conn = get_db()
    conn.execute("UPDATE licenses SET status='active' WHERE license=?", (lic,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=True)