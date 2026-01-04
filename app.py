from flask import Flask, request, redirect, render_template_string
import json
import os

app = Flask(__name__)

CUSTOMER_FILE = "customers.json"
LICENSE_FILE = "licenses.json"
ADMIN_PASSWORD = "smart123"  # Admin login password

# ---------------------- DATA ----------------------
def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return []

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# ---------------------- LICENSE CHECK ----------------------
def check_license(code):
    licenses = load_data(LICENSE_FILE)
    for lic in licenses:
        if lic["license"] == code:
            return lic["status"] == "active"
    return False

# ---------------------- HOME PAGE (TAILOR LICENSE INPUT) ----------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        license_code = request.form.get("license").strip()
        if check_license(license_code):
            return redirect("/main")
        else:
            return "<h2>Access Denied ❌ Invalid or Blocked License</h2><br><a href='/'>Back</a>"
    return """
    <div style="max-width:400px;margin:auto;text-align:center;">
    <h2>Enter Your License Code</h2>
    <form method="post">
        <input name="license" type="text" placeholder="License Code" required style="width:100%;padding:10px;margin:10px 0;"><br>
        <button type="submit" style="width:100%;padding:10px;background-color:green;color:white;border:none;border-radius:5px;">Enter</button>
    </form>
    </div>
    """

# ---------------------- MAIN APP ----------------------
@app.route("/main")
def main_page():
    return """
    <div style="max-width:500px;margin:auto;">
    <h2 style="color:darkred;text-align:center;">Smart Tailor – Add Customer</h2>
    <form method="post" action="/add">
        Name:<br><input name="name" required style="width:100%;padding:8px;margin:5px 0;"><br>
        Mobile:<br><input name="mobile" required style="width:100%;padding:8px;margin:5px 0;"><br>
        Length:<br><input name="length" style="width:100%;padding:8px;margin:5px 0;"><br>
        Chest:<br><input name="chest" style="width:100%;padding:8px;margin:5px 0;"><br>
        Waist:<br><input name="waist" style="width:100%;padding:8px;margin:5px 0;"><br>
        Shoulder:<br><input name="shoulder" style="width:100%;padding:8px;margin:5px 0;"><br>
        Poncha:<br><input name="poncha" style="width:100%;padding:8px;margin:5px 0;"><br>
        Batton:<br><input name="batton" style="width:100%;padding:8px;margin:5px 0;"><br>
        Packet:<br><input name="packet" style="width:100%;padding:8px;margin:5px 0;"><br>
        Zip:<br><input name="zip" style="width:100%;padding:8px;margin:5px 0;"><br>
        Shalwar Length:<br><input name="shalwar" style="width:100%;padding:8px;margin:5px 0;"><br>
        Collar:<br><input name="collar" style="width:100%;padding:8px;margin:5px 0;"><br>
        Ghara:<br><input name="ghara" style="width:100%;padding:8px;margin:5px 0;"><br>
        Amount:<br><input name="amount" style="width:100%;padding:8px;margin:5px 0;"><br>
        <button type="submit" style="width:100%;padding:10px;background-color:green;color:white;border:none;border-radius:5px;margin-top:10px;">Save Customer</button>
    </form>
    <br>
    <a href='/search'><button style="width:48%;padding:10px;background-color:blue;color:white;border:none;border-radius:5px;margin:1%;">Search Customer</button></a>
    <a href='/list'><button style="width:48%;padding:10px;background-color:orange;color:white;border:none;border-radius:5px;margin:1%;">View All Customers</button></a>
    </div>
    """

# ---------------------- ADD CUSTOMER ----------------------
@app.route("/add", methods=["POST"])
def add():
    data = load_data(CUSTOMER_FILE)
    data.append(dict(request.form))
    save_data(CUSTOMER_FILE, data)
    return redirect("/main")

# ---------------------- SEARCH CUSTOMER ----------------------
@app.route("/search", methods=["GET", "POST"])
def search():
    html = """
    <div style="max-width:500px;margin:auto;">
    <h2 style="color:purple;text-align:center;">Search Customer</h2>
    <form method="post">
        <input name="query" placeholder="Name or Mobile" required style="width:100%;padding:8px;margin:5px 0;">
        <button type="submit" style="width:100%;padding:10px;background-color:blue;color:white;border:none;border-radius:5px;margin-top:5px;">Search</button>
    </form>
    """
    if request.method == "POST":
        data = load_data(CUSTOMER_FILE)
        query = request.form["query"].lower()
        found = [c for c in data if query in c.get("mobile","").lower() or query in c.get("name","").lower()]
        if found:
            for c in found:
                html += f"<p>{c}</p>"
        else:
            html += "<p>No customer found</p>"
    html += '<br><a href="/main"><button style="width:100%;padding:10px;background-color:green;color:white;border:none;border-radius:5px;">Back</button></a></div>'
    return html

# ---------------------- VIEW ALL ----------------------
@app.route("/list")
def list_customers():
    data = load_data(CUSTOMER_FILE)
    html = "<div style='max-width:500px;margin:auto;'><h2 style='color:darkgreen;text-align:center;'>All Customers</h2>"
    for c in data:
        html += f"<p>{c}</p>"
    html += '<br><a href="/main"><button style="width:100%;padding:10px;background-color:green;color:white;border:none;border-radius:5px;">Back</button></a></div>'
    return html

# ---------------------- ADMIN DASHBOARD ----------------------
@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
    licenses = load_data(LICENSE_FILE)

    # Admin login
    if request.method == "POST":
        action = request.form.get("action")
        pw = request.form.get("password", "")
        license_code = request.form.get("license_code", "")
        name = request.form.get("name", "")
        if pw != ADMIN_PASSWORD:
            return "<h2>Wrong admin password ❌</h2><br><a href='/admin'>Back</a>"

        # ------------------- ACTIONS -------------------
        if action == "add":
            licenses.append({"license": license_code, "name": name, "status": "active"})
        elif action == "block":
            for lic in licenses:
                if lic["license"] == license_code:
                    lic["status"] = "blocked"
        elif action == "activate":
            for lic in licenses:
                if lic["license"] == license_code:
                    lic["status"] = "active"
        elif action == "delete":
            licenses = [lic for lic in licenses if lic["license"] != license_code]

        save_data(LICENSE_FILE, licenses)

    # ------------------- DASHBOARD HTML -------------------
    html = """
    <div style='max-width:700px;margin:auto;text-align:center;'>
    <h2>Admin Dashboard - Tailor Licenses</h2>
    <table border=1 style='border-collapse:collapse;width:100%;margin:auto;'>
    <tr><th>License</th><th>Name</th><th>Status</th><th>Actions</th></tr>
    """
    for lic in licenses:
        html += f"""
        <tr>
            <td>{lic['license']}</td>
            <td>{lic['name']}</td>
            <td>{lic['status']}</td>
            <td>
                <form method='post' style='display:inline;'>
                    <input type='hidden' name='password' value='{ADMIN_PASSWORD}'>
                    <input type='hidden' name='license_code' value='{lic['license']}'>
                    <button name='action' value='activate'>Activate</button>
                    <button name='action' value='block'>Block</button>
                    <button name='action' value='delete'>Delete</button>
                </form>
            </td>
        </tr>
        """
    html += "</table><br>"

    # Add new license form
    html += """
    <h3>Add New License</h3>
    <form method='post'>
        <input type='hidden' name='password' value='{0}'>
        License Code: <input name='license_code' required>
        Tailor Name: <input name='name' required>
        <button name='action' value='add'>Add License</button>
    </form>
    </div>
    """.format(ADMIN_PASSWORD)

    return html

# ---------------------- RUN ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)