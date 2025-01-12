
from flask import Flask, render_template
import requests
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

team_id = 119
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

@app.route('/team_players')
def team_PLayers():
    # Fetch the team roster
    response = requests.get(team_roster_url.format(team_id=team_id))
    roster_data = response.json()

    # Use ThreadPoolExecutor to fetch player details concurrently
    with ThreadPoolExecutor() as executor:
        players_info = list(executor.map(fetch_player_details, roster_data["roster"]))

    # Categorize players
    active_players = [p for p in players_info if p["status"] == "Active"]
    minor_league_players = [p for p in players_info if "Minor League" in p["status"]]
    traded_players = [p for p in players_info if "Traded" in p["status"]]

    # Render the template with player data
    return render_template('playerDetails.html', active_players=active_players, minor_league_players=minor_league_players, traded_players=traded_players)

if __name__ == '__main__':
    app.run(debug=True)
