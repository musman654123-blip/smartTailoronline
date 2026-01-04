from flask import Flask, request, redirect
import json
import os

app = Flask(__name__)
DATA_FILE = "customers.json"
PASSWORD = "smart123"

# ---------- DATA FUNCTIONS ----------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------- PASSWORD PAGE ----------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        pw = request.form.get("password")
        if pw == PASSWORD:
            return redirect("/main")
        else:
            return "<h2>Wrong password ❌</h2><br><a href='/'>Back</a>"
    return """
    <div style="max-width:400px;margin:auto;text-align:center;">
    <h2 style="color:darkblue;">Enter Password</h2>
    <form method="post">
        <input name="password" type="password" placeholder="Password" required style="width:100%;padding:10px;margin:10px 0;"><br>
        <button type="submit" style="width:100%;padding:10px;background-color:green;color:white;border:none;border-radius:5px;">Enter</button>
    </form>
    </div>
    """

# ---------- MAIN PAGE ----------
@app.route("/main")
def main_page():
    return """
    <div style="max-width:500px;margin:auto;">
    <h2 style="color:darkred;text-align:center;">Smart Tailor – Add Customer</h2>
    <form method="post" action="/add">
        Name:<br><input name="name" required><br>
        Mobile:<br><input name="mobile" required><br>
        Length:<br><input name="length"><br>
        Chest:<br><input name="chest"><br>
        Waist:<br><input name="waist"><br>
        Shoulder:<br><input name="shoulder"><br>
        Poncha:<br><input name="poncha"><br>
        Batton:<br><input name="batton"><br>
        Packet:<br><input name="packet"><br>
        Zip:<br><input name="zip"><br>
        Shalwar Length:<br><input name="shalwar"><br>
        Collar:<br><input name="collar"><br>
        Ghara:<br><input name="ghara"><br>
        Amount:<br><input name="amount"><br>
        <button type="submit">Save Customer</button>
    </form>
    <br>
    <a href='/search'>Search</a> | <a href='/list'>View All</a>
    </div>
    """

# ---------- ADD CUSTOMER ----------
@app.route("/add", methods=["POST"])
def add():
    data = load_data()
    data.append(dict(request.form))
    save_data(data)
    return redirect("/main")

# ---------- SEARCH ----------
@app.route("/search", methods=["GET", "POST"])
def search():
    html = "<h2>Search Customer</h2><form method='post'><input name='query' required><button>Search</button></form>"
    if request.method == "POST":
        data = load_data()
        q = request.form["query"].lower()
        found = [c for c in data if q in c.get("name","").lower() or q in c.get("mobile","")]
        html += "<br>".join(str(c) for c in found) if found else "<p>No record</p>"
    return html + "<br><a href='/main'>Back</a>"

# ---------- LIST ----------
@app.route("/list")
def list_customers():
    data = load_data()
    return "<br>".join(str(c) for c in data) + "<br><a href='/main'>Back</a>"

# ---------- ONLINE RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)