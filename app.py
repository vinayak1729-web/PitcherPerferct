from flask import Flask, render_template, request, redirect, url_for, session, jsonify , flash
import json
from modules.teamDetails import get_team_data
import google.generativeai as genai
import csv
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import pandas as pd
import sqlite3
from functools import lru_cache

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

app = Flask(__name__)
app.secret_key = "your_secret_key"

db_file = "database/db.sqlite"

# Initialize SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create users table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT,
    team TEXT
)
''')
conn.commit()
conn.close()

# Helper functions
def save_user(user_data):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, email, password, role, team)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_data["name"], user_data["email"], user_data["password"], user_data["role"], user_data.get("team")))
    conn.commit()
    conn.close()

def get_user(email):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "password": user[3],
            "role": user[4],
            "team": user[5]
        }
    return None

def update_user(user):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET name = ?, password = ?, team = ?
        WHERE email = ?
    ''', (user["name"], user["password"], user["team"], user["email"]))
    conn.commit()
    conn.close()

def find_team_id_by_name(team_name, teams):
    """Utility function to find team ID by name."""
    for league, divisions in teams.items():
        for division, teams_list in divisions.items():
            for team in teams_list:
                if team["name"] == team_name:
                    return team["id"]
    return None

@app.route("/")
def home():

    if "user" in session:
        user = session["user"]
        team_name = user.get("team")
        
        # Get the team ID
        team_id = find_team_id_by_name(team_name, teams)
        
        # Fetch team details
        teamDetail = get_team_data(team_id) if team_id else None
        batters_data, pitchers_data = read_team_data(team_id)
        # Fetch Gemini details
        if teamDetail:
            prompt = (
                f"Give a brief about the team {teamDetail['name']} ({teamDetail['league']}) "
                f"established in {teamDetail['first_year']}. Include performance and emojis. "
                f"Don't introduce about yourself; only the content."
            )
            promptB = (
            f"""Provide a performance analysis of the team {teamDetail['name']} ({teamDetail['league']}) 
            established in {teamDetail['first_year']}. Analyze their batters' performance based on this data: {batters_data}. 
            Keep the summary concise, insightful, and easy for the coach to understand. Highlight key statistics, notable players, 
            and trends from the past 5 years. Include specific predictions for the batters' performance in 2025, 
            focusing on strengths and areas for improvement. Use an engaging tone with relevant emojis. 🎯⚾ STRICTLY GIVE IN 70 WORDS ONLY """
            )
            promptP = (
            f"""Provide a performance analysis of the team {teamDetail['name']} ({teamDetail['league']}) 
            established in {teamDetail['first_year']}. Analyze their pitchers' performance based on this data: {pitchers_data}. 
            Keep the summary concise, insightful, and easy for the coach to understand. Highlight key statistics, notable players, 
            and trends from the past 5 years. Include specific predictions for the pitchers' performance in 2025, 
            focusing on strengths and areas for improvement. Use an engaging tone with relevant emojis. 🚀⚾ STRICTLY GIVE IN 70 WORDS ONLY"""
            )



            BatterDetails = gemini_chat(promptB)
            PitchersDetais = gemini_chat(promptP)
            GeminiDetails = gemini_chat(prompt)
        else:
            GeminiDetails = "Team details are not available."

        return render_template(
            "home.html",
            user=user,
            teams=teams,
            team_id=team_id,
            teamDetail=teamDetail,
            feedbackgemini=GeminiDetails,
            BatterDetails=BatterDetails,
            PitchersDetais=PitchersDetais
        )

    return redirect(url_for("login"))

def read_team_data(team_id):
    try:
        batters_csv = pd.read_csv(f'dataset/2024/batters/{team_id}.csv')
        pitchers_csv = pd.read_csv(f'dataset/2024/pitchers/{team_id}.csv')
    except FileNotFoundError as e:
        raise FileNotFoundError(f"CSV files not found for team ID {team_id}") from e

    batters_data = batters_csv.to_dict(orient='records')
    pitchers_data = pitchers_csv.to_dict(orient='records')

    return batters_data, pitchers_data


@app.route("/get_data" ,methods=["GET", "POST"])
def get_data():
    team_id = request.args.get('team_id')  # Get team_id from the query parameter
    if not team_id:
        return jsonify({"error": "Team ID is required"}), 400

    try:
        batters_csv = pd.read_csv(f'dataset/2024/batters/{team_id}.csv')
        pitchers_csv = pd.read_csv(f'dataset/2024/pitchers/{team_id}.csv')
    except FileNotFoundError:
        return jsonify({"error": "CSV files not found for the team"}), 404

    batters_data = batters_csv.to_dict(orient='records')
    pitchers_data = pitchers_csv.to_dict(orient='records')

    mlb_avg_batter = {
        "year": "2024",
        "woba": 0.310,
        "slg": 0.399,
        "ba": 0.243,
        "est_ba": 0.243,
        "est_slg": 0.397,
        "est_woba": 0.312,
    }

    mlb_avg_pitcher = {
        "woba": 0.310,
        "slg": 0.399,
        "ba": 0.243,
        "est_ba": 0.243,
        "est_slg": 0.397,
        "est_woba": 0.312,
    }

    return jsonify({
        "batters": batters_data,
        "pitchers": pitchers_data,
        "mlb_avg_batter": mlb_avg_batter,
        "mlb_avg_pitcher": mlb_avg_pitcher
    })

@app.route("/chatbot", methods=["POST"])
def chatbot():
    # Get user input from the POST request
    user_input = request.json.get("message", "")

    # Check if user input is provided
    if not user_input:
        return jsonify({"response": "Please provide a message."}), 400

    # Fetch team details from the session
    if "user" in session:
        user = session["user"]
        team_name = user.get("team")
        team_id = find_team_id_by_name(team_name, teams)

        # Fetch team roster
        roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster?season=2024"
        roster_response = requests.get(roster_url)
        roster = roster_response.json().get("roster", [])

        # Separate batters and pitchers
        batters = []
        pitchers = []
        for player in roster:
            player_details = fetch_player_details(player)
            if player_details["position"] in ["Pitcher"]:
                pitchers.append(player_details)
            else:
                batters.append(player_details)

        # Format the roster data for chatbot context
        batters_data = "\n".join(
            [f"{b['name']} - {b['position']}, Status: {b['status']}" for b in batters]
        )
        pitchers_data = "\n".join(
            [f"{p['name']} - {p['position']}, Status: {p['status']}" for p in pitchers]
        )

        # Context for the chatbot
        context = (
            f"Here are the details for {team_name}'s players:\n\n "
            f"Batters:\n{batters_data}\n\n"
            f"Pitchers:\n{pitchers_data}\n\n"
            "You are the assistant coach. Provide strategies, analyze performance, "
            "and offer comparisons based on the above data. "
        )

        # Append the user input to the context
        chatbot_prompt = context + user_input

        # Generate response using Gemini API
        gemini_response = gemini_chat(chatbot_prompt)

        return jsonify({"response": gemini_response})

    # If no user in session, return an error message
    return jsonify({"response": "No team data available. Please log in."}), 400

# def get_team_id():
#      if "user" in session:
#         user = session["user"]
#         team_name = user.get("team")
        
#         # Get the team ID
#         team_id = find_team_id_by_name(team_name, teams)

#         return team_id 
     
team_roster_url = "https://statsapi.mlb.com/api/v1/teams/{team_id}/roster?season=2024"
player_details_url = "https://statsapi.mlb.com/api/v1/people/{player_id}"

def fetch_player_details(player):
    
    player_id = player["person"]["id"]
    player_name = player["person"]["fullName"]
    player_position = player["position"]["name"]
    player_status = player["status"]["description"]

    # Fetch player details
    player_response = requests.get(player_details_url.format(player_id=player_id))
    player_details = player_response.json()["people"][0]
    
    # Extract player details
    headshot_url = f'https://securea.mlb.com/mlb/images/players/head_shot/{player_id}.jpg'
    
    return {
        "id":player_id,
        "name": player_name,
        "position": player_position,
        "status": player_status,
        "dob": player_details["birthDate"],
        "height": player_details["height"],
        "weight": player_details["weight"],
        "batside": player_details["batSide"]["description"],
        "pitchside": player_details["pitchHand"]["description"],
        "strike_zone_top": player_details["strikeZoneTop"],
        "strike_zone_bottom": player_details["strikeZoneBottom"],
        "headshot_url": headshot_url
    }

# @app.route('/team_players')
# def team_PLayers():
#     team_id = get_team_id()
#     # Fetch the team roster
#     response = requests.get(team_roster_url.format(team_id=team_id))
#     roster_data = response.json()

#     # Use ThreadPoolExecutor to fetch player details concurrently
#     with ThreadPoolExecutor() as executor:
#         players_info = list(executor.map(fetch_player_details, roster_data["roster"]))

#     # Categorize players
#     active_players = [p for p in players_info if p["status"] == "Active"]
#     minor_league_players = [p for p in players_info if "Minor League" in p["status"]]
#     traded_players = [p for p in players_info if "Traded" in p["status"]]

#     # Render the template with player data
#     return render_template('team_players.html', active_players=active_players, minor_league_players=minor_league_players, traded_players=traded_players)

# Load team mapping
with open('dataset/team.json', 'r') as f:
    team_mapping = json.load(f)

def get_team_logo(team_id):
    return f'https://www.mlbstatic.com/team-logos/{team_id}.svg'

@app.route('/team_players', methods=['GET', 'POST'])
def team_players():
    team_id = request.args.get('team_id') or session.get('team_id')
    if not team_id:
        team_id = 119  # Default to Dodgers

    session['team_id'] = team_id

    status_filter = request.args.get('status', 'All')
    role_filters = request.args.getlist('roles')  # Get multiple roles

    # Fetch the team roster
    team_roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster?season=2024"
    response = requests.get(team_roster_url)
    roster_data = response.json()

    # Fetch player details concurrently
    def fetch_player_details(player):
        player_id = player["person"]["id"]
        player_name = player["person"]["fullName"]
        player_position = player["position"]["name"]
        player_status = player["status"]["description"]
        player_jersey = player.get("jerseyNumber", "N/A")  # Jersey number may not always exist
        player_response = requests.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}")
        player_details = player_response.json()["people"][0]
        return {
            "id": player_id,
            "name": player_name,
            "position": player_position,
            "type": player["position"].get("type", "N/A"),  # Position type
            "status": player_status,
            "jersey_number": player_jersey,
            "dob": player_details["birthDate"],
            "height": player_details["height"],
            "weight": player_details["weight"],
            "batside": player_details["batSide"]["description"],
            "pitchside": player_details["pitchHand"]["description"],
            "strike_zone_top": player_details.get("strikeZoneTop", "N/A"),
            "strike_zone_bottom": player_details.get("strikeZoneBottom", "N/A"),
            "headshot_url": f'https://securea.mlb.com/mlb/images/players/head_shot/{player_id}.jpg'
        }

    with ThreadPoolExecutor() as executor:
        players_info = list(executor.map(fetch_player_details, roster_data["roster"]))

    # Filter players
    if status_filter != 'All':
        players_info = [p for p in players_info if p["status"] == status_filter]
    if role_filters:
        players_info = [p for p in players_info if p["position"] in role_filters]

    team_logo = get_team_logo(team_id)

    return render_template(
        'team_players.html',
        players=players_info,
        team_logo=team_logo,
        team_mapping=team_mapping,
        selected_team=int(team_id),
        selected_status=status_filter,
        selected_roles=role_filters
    )

if __name__ == '__main__':
    app.run(debug=True)



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

    user = session.get("user", {})
    if request.method == "POST":
        update_field = request.form.get("update_field")
        new_value = request.form.get("new_value")

        # Check if the field to update is valid
        if not update_field:
            return "Field to update is required!", 400

        if not new_value and update_field != "team":
            return "New value is required!", 400

        # Update the user dictionary
        if update_field in ["name", "email", "password", "role"]:
            user[update_field] = new_value
        elif update_field == "team":
            user["team"] = request.form.get("new_value_team")
        else:
            return "Invalid field update!", 400

        # Save updated user info to session
        session["user"] = user

        # Update the database
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE users SET {update_field} = ? WHERE email = ?",
                (new_value if update_field != "team" else user["team"], user["email"]),
            )
            conn.commit()
        except sqlite3.Error as e:
            return f"Database error: {e}", 500
        finally:
            conn.close()

        return redirect(url_for("profile"))

    return render_template("profile.html", user=user, teams=teams)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
