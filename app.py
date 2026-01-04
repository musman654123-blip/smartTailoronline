from flask import Flask, request, redirect
import json
import os

app = Flask(__name__)

CUSTOMER_FILE = "customers.json"
LICENSE_FILE = "licenses.json"
ADMIN_PASSWORD = "smart123"

# ---------------------- DATA HANDLING ----------------------
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

# ---------------------- TAILOR LICENSE PAGE ----------------------
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

# ---------------------- MAIN CUSTOMER APP ----------------------
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

# ---------------------- SEARCH ----------------------
@app.route("/search", methods=["GET", "POST"])
def search():
    html = "<div style='max-width:500px;margin:auto;'><h2>Search Customer</h2><form method='post'>"
    html += "<input name='query' placeholder='Name or Mobile' required style='width:100%;padding:8px;margin:5px 0;'>"
    html += "<button type='submit' style='width:100%;padding:10px;background-color:blue;color:white;border:none;border-radius:5px;margin-top:5px;'>Search</button></form>"
    if request.method=="POST":
        data = load_data(CUSTOMER_FILE)
        query = request.form["query"].lower()
        found = [c for c in data if query in c.get("mobile","").lower() or query in c.get("name","").lower()]
        if found:
            for c in found: html+=f"<p>{c}</p>"
        else: html+="<p>No customer found</p>"
    html += "<br><a href='/main'><button style='width:100%;padding:10px;background-color:green;color:white;border:none;border-radius:5px;'>Back</button></a></div>"
    return html

# ---------------------- VIEW ALL ----------------------
@app.route("/list")
def list_customers():
    data = load_data(CUSTOMER_FILE)
    html = "<div style='max-width:500px;margin:auto;'><h2>All Customers</h2>"
    for c in data: html+=f"<p>{c}</p>"
    html += "<br><a href='/main'><button style='width:100%;padding:10px;background-color:green;color:white;border:none;border-radius:5px;'>Back</button></a></div>"
    return html

# ---------------------- ADMIN BUTTON ROUTES ----------------------
@app.route("/admin")
def admin_dashboard():
    licenses = load_data(LICENSE_FILE)
    html = "<div style='max-width:700px;margin:auto;text-align:center;'><h2>Admin Dashboard - Tailor Licenses</h2>"
    html += "<table border=1 style='border-collapse:collapse;width:100%;margin:auto;'>"
    html += "<tr><th>License</th><th>Name</th><th>Status</th><th>Actions</th></tr>"
    for lic in licenses:
        html += f"<tr><td>{lic['license']}</td><td>{lic['name']}</td><td>{lic['status']}</td>"
        html += "<td>"
        html += f"<a href='/admin/activate/{lic['license']}'>Activate</a> | "
        html += f"<a href='/admin/block/{lic['license']}'>Block</a> | "
        html += f"<a href='/admin/delete/{lic['license']}'>Delete</a>"
        html += "</td></tr>"
    html += "</table><br>"
    html += """
    <h3>Add New License</h3>
    <form method='post' action='/admin/add'>
        License Code: <input name='license_code' required>
        Tailor Name: <input name='name' required>
        <button type='submit'>Add License</button>
    </form>
    </div>
    """
    return html

@app.route("/admin/activate/<code>")
def admin_activate(code):
    licenses = load_data(LICENSE_FILE)
    for lic in licenses:
        if lic["license"] == code:
            lic["status"] = "active"
    save_data(LICENSE_FILE, licenses)
    return redirect("/admin")

@app.route("/admin/block/<code>")
def admin_block(code):
    licenses = load_data(LICENSE_FILE)
    for lic in licenses:
        if lic["license"] == code:
            lic["status"] = "blocked"
    save_data(LICENSE_FILE, licenses)
    return redirect("/admin")

@app.route("/admin/delete/<code>")
def admin_delete(code):
    licenses = load_data(LICENSE_FILE)
    licenses = [lic for lic in licenses if lic["license"] != code]
    save_data(LICENSE_FILE, licenses)
    return redirect("/admin")

@app.route("/admin/add", methods=["POST"])
def admin_add():
    licenses = load_data(LICENSE_FILE)
    code = request.form.get("license_code")
    name = request.form.get("name")
    licenses.append({"license": code, "name": name, "status": "active"})
    save_data(LICENSE_FILE, licenses)
    return redirect("/admin")

# ---------------------- RUN ----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)