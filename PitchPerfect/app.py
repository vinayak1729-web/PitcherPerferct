from flask import Flask, render_template, request, redirect, url_for, session, jsonify , flash
import json
from modules.teamDetails import get_team_data
import google.generativeai as genai
import os
from dotenv import load_dotenv
import pandas as pd
# Load environment variables
load_dotenv()
app = Flask(__name__)
app.secret_key = "supersecretkey"
genai.configure(api_key=os.getenv("API_KEY"))

defaultprompt = """you are the ai coach of baseball
                    your main focus is on players stats , their mental state , team strategy , their coordination, and team win probability
                    you have to make the analysis of real coach easier 
                    you have to help the players mentally and physically ( by guiding)
                    you have to give ideas to coach on building the most effiect team lineup ( means arrange ment of players ) against the opponent team player
                    you will provided my the teams details , player details and rest you have to anaylse , like for team the current active players list would be given and some of the past matches insights and now u have to predict the win/lose percentange of them based on it 
                    your name is pitcherperfect ai , made by team surya prabha , with the help of gemini and mlb stats 
                    you have to suggest and give the insights to coach about the who can be the new best player who can be kept in team from the minor leage team 
                    your tone must be friendly and like a guide , u may sometime have to guide also to coach , fan , player , mentally and also by sports pont of view 
                    You are a professional, highly skilled mental doctor, and health guide.
                    You act as a best friend to those who talk to you , but you have to talk based on their mental health , by seeing his age intrests qualities , if you dont know ask him indirectly by asking his/her studing or any work doing currently. 
                    You can assess if someone is under mental stress by judging their communication.
                    you are a ai coach but if is in mental instability then you have to help him 
                    you are unisex ( pretend to one who like the one )
"""

#prompt = "This is my assessment of close-ended questions and open-ended questions, so you have to talk to me accordingly."

# Create the model
generation_config = {
    "temperature": 2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
    system_instruction=defaultprompt + " " 
)

def gemini_chat(user_input):
    try:
        # Send the user input to the model
        response = chat_session.send_message(user_input)
        return response.text
    except Exception as e:
        print(f"Error during chat: {e}")
        return "An error occurred. Please try again."
    
chat_session = model.start_chat()
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
       
        if teamDetail:
                GeminiDetails = gemini_chat(
        f"Give a brief about the team {teamDetail['name']} ({teamDetail['league']}) established in {teamDetail['first_year']}. Include performance and emojis. dont introduce about you there only the content"
                 )
        else:
             GeminiDetails = "Team details are not available."

        return render_template("home.html", user=user, teams=teams, team_id=team_id, teamDetail=teamDetail , feedbackgemini = GeminiDetails )

    return redirect(url_for("login"))


@app.route("/get_data")
def get_data():
    # Check if the user is logged in and has a team
    if "user" not in session:
        return jsonify({"error": "User not logged in"}), 401

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

    if not team_id:
        return jsonify({"error": "Team ID not found"}), 404

    # Dynamically load CSV data based on team_id
    try:
        batters_csv = pd.read_csv(f'dataset/2024/batters/{team_id}.csv')
        pitchers_csv = pd.read_csv(f'dataset/2024/pitchers/{team_id}.csv')
    except FileNotFoundError:
        return jsonify({"error": "CSV files not found for the team"}), 404

    # Convert DataFrame to JSON-serializable dictionaries
    batters_data = batters_csv.to_dict(orient='records')
    pitchers_data = pitchers_csv.to_dict(orient='records')

    return jsonify({"batters": batters_data, "pitchers": pitchers_data})

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
