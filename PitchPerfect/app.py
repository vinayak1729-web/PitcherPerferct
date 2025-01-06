from flask import Flask, render_template, request, redirect, url_for, session, jsonify , flash
import json
from teamDetails import get_team_data

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Simulated MLB team data
teams = {
    "American League": {
        "East": [
            {"name": "New York Yankees", "id": 147},
            {"name": "Tampa Bay Rays", "id": 139},
            {"name": "Boston Red Sox", "id": 111},
            {"name": "Toronto Blue Jays", "id": 141},
            {"name": "Baltimore Orioles", "id": 110},
        ],
        "Central": [
            {"name": "Cleveland Guardians", "id": 114},
            {"name": "Minnesota Twins", "id": 142},
            {"name": "Chicago White Sox", "id": 145},
            {"name": "Kansas City Royals", "id": 118},
            {"name": "Detroit Tigers", "id": 116},
        ],
        "West": [
            {"name": "Houston Astros", "id": 117},
            {"name": "Texas Rangers", "id": 140},
            {"name": "Oakland Athletics", "id": 133},
            {"name": "Seattle Mariners", "id": 136},
            {"name": "Los Angeles Angels", "id": 108},
        ],
    },
    "National League": {
        "East": [
            {"name": "New York Mets", "id": 121},
            {"name": "Washington Nationals", "id": 120},
            {"name": "Atlanta Braves", "id": 144},
            {"name": "Miami Marlins", "id": 146},
            {"name": "Philadelphia Phillies", "id": 143},
        ],
        "Central": [
            {"name": "St. Louis Cardinals", "id": 138},
            {"name": "Cincinnati Reds", "id": 113},
            {"name": "Pittsburgh Pirates", "id": 134},
            {"name": "Chicago Cubs", "id": 112},
            {"name": "Milwaukee Brewers", "id": 158},
        ],
        "West": [
            {"name": "San Francisco Giants", "id": 137},
            {"name": "San Diego Padres", "id": 135},
            {"name": "Colorado Rockies", "id": 115},
            {"name": "Arizona Diamondbacks", "id": 109},
            {"name": "Los Angeles Dodgers", "id": 119},
        ],
    },
}

# Simulated database (JSON file)
db_file = "database/db.json"

# Initialize db.json if not exists
try:
    with open(db_file, "r") as f:
        pass
except FileNotFoundError:
    with open(db_file, "w") as f:
        json.dump([], f)

# Helper functions
def save_user(user_data):
    with open(db_file, "r+") as f:
        data = json.load(f)
        data.append(user_data)
        f.seek(0)
        json.dump(data, f)

def get_user(email):
    with open(db_file, "r") as f:
        users = json.load(f)
        for user in users:
            if user["email"] == email:
                return user
    return None

@app.route("/")
def home():
    if "user" in session:
        user = session["user"]
        team_name = user.get("team")
        team_id = None

        # Find the team ID by iterating through the teams dictionary
        for league, divisions in teams.items():
            for division, teams_list in divisions.items():
                for team in teams_list:
                    if team["name"] == team_name:
                        team_id = team["id"]
                        break
                if team_id:
                    break
            if team_id:
                break

        teamDetail = get_team_data(team_id) if team_id else None

        return render_template("home.html", user=user, teams=teams, team_id=team_id, teamDetail=teamDetail)

    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]
        team = request.form.get("team")

        if get_user(email):
            return "User already exists!"

        user = {"name": name, "email": email, "password": password, "role": role, "team": team}
        save_user(user)
        return redirect(url_for("login"))

    return render_template("signup.html", teams=teams)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_user(email)
        if user and user["password"] == password:
            session["user"] = user
            return redirect(url_for("home"))
        return "Invalid credentials!"

    return render_template("login.html")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        user = session["user"]
        user["name"] = request.form["name"]
        user["password"] = request.form["password"]
        user["team"] = request.form["team"]
        session["user"] = user

        # Update user in db.json
        with open(db_file, "r+") as f:
            users = json.load(f)
            for u in users:
                if u["email"] == user["email"]:
                    u.update(user)
                    break
            f.seek(0)
            json.dump(users, f)

    return render_template("profile.html", user=session["user"], teams=teams)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
