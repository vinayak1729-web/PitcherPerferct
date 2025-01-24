from flask import Flask, render_template, request,jsonify
import requests
import statsapi
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

# if __name__ == "__main__":
#     try:
#         # Start the chat session
#         chat_session = model.start_chat()

#         # Example usage
#         while True:
#             user_input = input("You: ")
#             if user_input.lower() == 'exit':
#                 print("Chat ended.")
#                 break

#             response = gemini_chat(user_input)
#             print("PitcherPerfect:", response)

#     except Exception as e:
#         print(f"Failed to start the chat session: {e}")


app = Flask(__name__)
chat_session = model.start_chat()
# MLB API URL
MLB_API_URL = 'https://statsapi.mlb.com/api/v1/schedule'

# MLB teams data (can be extended or dynamically fetched if needed)
teams_data = {
    "American League": {
        "East": [
            {"name": "New York Yankees", "id": 147},
            {"name": "Tampa Bay Rays", "id": 139},
            {"name": "Boston Red Sox", "id": 111},
            {"name": "Toronto Blue Jays", "id": 141},
            {"name": "Baltimore Orioles", "id": 110}
        ],
        "Central": [
            {"name": "Cleveland Guardians", "id": 114},
            {"name": "Minnesota Twins", "id": 142},
            {"name": "Chicago White Sox", "id": 145},
            {"name": "Kansas City Royals", "id": 118},
            {"name": "Detroit Tigers", "id": 116}
        ],
        "West": [
            {"name": "Houston Astros", "id": 117},
            {"name": "Texas Rangers", "id": 140},
            {"name": "Oakland Athletics", "id": 133},
            {"name": "Seattle Mariners", "id": 136},
            {"name": "Los Angeles Angels", "id": 108}
        ]
    },
    "National League": {
        "East": [
            {"name": "New York Mets", "id": 121},
            {"name": "Washington Nationals", "id": 120},
            {"name": "Atlanta Braves", "id": 144},
            {"name": "Miami Marlins", "id": 146},
            {"name": "Philadelphia Phillies", "id": 143}
        ],
        "Central": [
            {"name": "St. Louis Cardinals", "id": 138},
            {"name": "Cincinnati Reds", "id": 113},
            {"name": "Pittsburgh Pirates", "id": 134},
            {"name": "Chicago Cubs", "id": 112},
            {"name": "Milwaukee Brewers", "id": 158}
        ],
        "West": [
            {"name": "San Francisco Giants", "id": 137},
            {"name": "San Diego Padres", "id": 135},
            {"name": "Colorado Rockies", "id": 115},
            {"name": "Arizona Diamondbacks", "id": 109},
            {"name": "Los Angeles Dodgers", "id": 119}
        ]
    }
}


@app.route('/', methods=['GET', 'POST'])
def index():
    season = request.form.get('season', 2024)  # Default season
    home_team_filter = request.form.get('home_team', None)
    away_team_filter = request.form.get('away_team', None)

    response = requests.get(f"{MLB_API_URL}?sportId=1&season={season}")
    games_data = response.json().get("dates", [])

    matches = []
    for date_info in games_data:
        for game in date_info["games"]:
            home_team = game['teams']['home']['team']['name']
            away_team = game['teams']['away']['team']['name']
            home_score = game['teams']['home'].get('score', 'N/A')
            away_score = game['teams']['away'].get('score', 'N/A')

            game_date = game['gameDate']
            venue = game.get('venue', {}).get('name', 'N/A')
            game_pk = game['gamePk']

            home_team_logo = f'https://www.mlbstatic.com/team-logos/{game["teams"]["home"]["team"]["id"]}.svg'
            away_team_logo = f'https://www.mlbstatic.com/team-logos/{game["teams"]["away"]["team"]["id"]}.svg'

            # Apply filters
            if home_team_filter and home_team_filter != home_team:
                continue
            if away_team_filter and away_team_filter != away_team:
                continue

            matches.append({
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'game_date': game_date,
                'venue': venue,
                'game_pk': game_pk,
                'home_team_logo': home_team_logo,
                'away_team_logo': away_team_logo
            })

    return render_template('highlight.html', matches=matches, teams_data=teams_data)

@app.route('/game/<int:game_pk>')
def game_details(game_pk):
    game_details_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    response = requests.get(game_details_url)
    
    if response.status_code == 200:
        game_details = response.json()
        
        # Extract basic game details
        live_data = game_details.get("liveData", {})
        boxscore = live_data.get("boxscore", {})
        teams = boxscore.get("teams", {})
        home_team = teams.get("home", {}).get("team", {}).get("name", "Unknown")
        away_team = teams.get("away", {}).get("team", {}).get("name", "Unknown")
        home_score = teams.get("home", {}).get("runs", "N/A")
        away_score = teams.get("away", {}).get("runs", "N/A")
        game_date = game_details.get("gameData", {}).get("datetime", {}).get("dateTime", "N/A")
        venue = game_details.get("gameData", {}).get("venue", {}).get("name", "Unknown")
        status = game_details.get("gameData", {}).get("status", {}).get("detailedState", "N/A")

        # Extract plays and play details
        all_plays = live_data.get("plays", {}).get("allPlays", [])
        play_by_play = []
        for play in all_plays:
            result = play.get("result", {})
            matchup = play.get("matchup", {})
            about = play.get("about", {})
            count = play.get("count", {})
            
            play_details = {
                "description": result.get("description", "N/A"),
                "event": result.get("event", "N/A"),
                "eventType": result.get("eventType", "N/A"),
                "isOut": result.get("isOut", False),
                "rbi": result.get("rbi", 0),
                "homeScore": result.get("homeScore", 0),
                "awayScore": result.get("awayScore", 0),
                "inning": about.get("inning", "N/A"),
                "halfInning": about.get("halfInning", "N/A"),
                "startTime": about.get("startTime", "N/A"),
                "endTime": about.get("endTime", "N/A"),
                "balls": count.get("balls", 0),
                "strikes": count.get("strikes", 0),
                "outs": count.get("outs", 0),
                "batter": matchup.get("batter", {}).get("fullName", "Unknown"),
                "pitcher": matchup.get("pitcher", {}).get("fullName", "Unknown"),
                "batSide": matchup.get("batSide", {}).get("description", "Unknown"),
                "pitchHand": matchup.get("pitchHand", {}).get("description", "Unknown")
            }
            highlightdata = (
                            str(play_details["inning"]) +
                            play_details["description"] +
                            play_details["event"] +
                            play_details["batter"] +
                            play_details["pitcher"] +
                            str(play_details["homeScore"])
                            )
            print(highlightdata)

            play_by_play.append(play_details)
           # play_by_play_str =str(play_by_play)
        
            geminiHighlights = gemini_chat(f"Create an engaging and vivid commentary for the highlight reel of the match between {home_team} and {away_team}, played on {game_date} at {venue}. Include dynamic descriptions of the key moments and exciting play-by-play details: " + highlightdata)

        return render_template(
            'GameHighlights.html',
            home_team=home_team,
            away_team=away_team,
            home_score=home_score,
            away_score=away_score,
            game_date=game_date,
            venue=venue,
            status=status,
            play_by_play=play_by_play,
            geminiHighlights = geminiHighlights,
            
        )
    else:
        return jsonify({"error": "Failed to fetch game details"}), response.status_code


if __name__ == '__main__':
    app.run(debug=True)
