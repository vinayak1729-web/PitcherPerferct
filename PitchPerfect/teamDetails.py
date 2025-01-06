import requests
def get_team_data(team_id):
    team_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}"
    response = requests.get(team_url)
    team_data = response.json()
    team_info = team_data["teams"][0]
    
    team_details = {
        "id": team_info["id"],
        "name": team_info["name"],
        "firstYearOfPlay": team_info["firstYearOfPlay"],
        "league": team_info["league"]["name"],
        "active": team_info["active"]
    }
    
    return team_details

