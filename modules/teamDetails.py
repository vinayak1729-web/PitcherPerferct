import requests
def get_team_data(team_id):
    team_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}"
    response = requests.get(team_url)
    if response.status_code == 200:
        team_data = response.json()
        team_info = team_data.get("teams", [{}])[0]  # Safely handle missing keys
        return {
            "id": team_info.get("id"),
            "name": team_info.get("name"),
            "first_year": team_info.get("firstYearOfPlay"),
            "league": team_info.get("league", {}).get("name"),
            "active": team_info.get("active", False),
        }
    return None
