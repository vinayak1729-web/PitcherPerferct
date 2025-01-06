from flask import Flask, render_template
import requests

app = Flask(__name__)

team_id = 119  # Example team ID (Los Angeles Dodgers)
team_roster_url = "https://statsapi.mlb.com/api/v1/teams/{team_id}/roster?season=2024"
player_details_url = "https://statsapi.mlb.com/api/v1/people/{player_id}"

@app.route('/')
def home():
    # Fetch the team roster
    response = requests.get(team_roster_url.format(team_id=team_id))
    roster_data = response.json()

    # Initialize lists to hold different player categories
    active_players = []
    minor_league_players = []
    traded_players = []

    # Classify players based on status and get additional details
    for player in roster_data["roster"]:
        player_id = player["person"]["id"]
        player_name = player["person"]["fullName"]
        player_position = player["position"]["name"]
        player_status = player["status"]["description"]

        # Get detailed player information
        player_response = requests.get(player_details_url.format(player_id=player_id))
        player_details = player_response.json()
        details = player_details["people"][0]
        
        # Extract player details
        dob = details["birthDate"]
        height = details["height"]
        weight = details["weight"]
        batside = details["batSide"]["description"]
        pitchside = details["pitchHand"]["description"]
        strike_zone_top = details["strikeZoneTop"]
        strike_zone_bottom = details["strikeZoneBottom"]
        
        player_info = {
            "name": player_name,
            "position": player_position,
            "status": player_status,
            "dob": dob,
            "height": height,
            "weight": weight,
            "batside": batside,
            "pitchside": pitchside,
            "strike_zone_top": strike_zone_top,
            "strike_zone_bottom": strike_zone_bottom
        }
        
        # Categorize players
        if player_status == "Active":
            active_players.append(player_info)
        elif "Minor League" in player_status:
            minor_league_players.append(player_info)
        elif "Traded" in player_status:
            traded_players.append(player_info)

    # Render the template with player data
    return render_template('playerDetails.html', active_players=active_players, minor_league_players=minor_league_players, traded_players=traded_players)

if __name__ == '__main__':
    app.run(debug=True)
