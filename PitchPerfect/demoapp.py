import os
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)

# Utility function to read and process CSV data
def read_team_data(team_id):
    try:
        batters_csv = pd.read_csv(f'dataset/2024/batters/{team_id}.csv')
        pitchers_csv = pd.read_csv(f'dataset/2024/pitchers/{team_id}.csv')
    except FileNotFoundError as e:
        raise FileNotFoundError(f"CSV files not found for team ID {team_id}") from e

    batters_data = batters_csv.to_dict(orient='records')
    pitchers_data = pitchers_csv.to_dict(orient='records')
    print(batters_data,pitchers_data , type(batters_data))
    return batters_data, pitchers_data


@app.route("/get_data", methods=["GET", "POST"])
def get_data():
    team_id = request.args.get('team_id')  # Get team_id from the query parameter
    if not team_id:
        return jsonify({"error": "Team ID is required"}), 400

    try:
        batters_data, pitchers_data = read_team_data(team_id)
    except FileNotFoundError:
        return jsonify({"error": "CSV files not found for the team"}), 404

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

# Function to use batters and pitchers data for further analysis
def analysis(team_id):
    try:
        batters_data, pitchers_data = read_team_data(team_id)
    except FileNotFoundError:
        print(f"Error: CSV files not found for team ID {team_id}")
        return None

    

# Example usage of analysis function
if __name__ == "__main__":
    team_id = "119"  # Example team_id
    result = analysis(team_id)
    if result:
        print("Analysis Result:", result)

    app.run(debug=True)
