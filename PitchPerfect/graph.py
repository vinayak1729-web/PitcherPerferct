# from flask import Flask, jsonify, render_template
# import pandas as pd

# app = Flask(__name__)
# app.secret_key = "your_secret_key"



# @app.route("/get_data")
# def get_data(team_id):
#     try:
#         batters_csv = pd.read_csv(f'dataset/2024/batters/{team_id}.csv')
#         pitchers_csv = pd.read_csv(f'dataset/2024/pitchers/{team_id}.csv')
#     except FileNotFoundError:
#         return jsonify({"error": "CSV files not found for the team"}), 404

#     batters_data = batters_csv.to_dict(orient='records')
#     pitchers_data = pitchers_csv.to_dict(orient='records')

#     # MLB Average for comparison
#     mlb_avg_batter = {
#         "year": "2024",
#         "woba": 0.310,
#         "slg": 0.399,
#         "ba": 0.243,
#         "est_ba": 0.243,
#         "est_slg": 0.397,
#         "est_woba": 0.312,
#     }

#     mlb_avg_pitcher = {
#         "woba": 0.310,
#         "slg": 0.399,
#         "ba": 0.243,
#         "est_ba": 0.243,
#         "est_slg": 0.397,
#         "est_woba": 0.312,
#     }

#     return jsonify({
#         "batters": batters_data,
#         "pitchers": pitchers_data,
#         "mlb_avg_batter": mlb_avg_batter,
#         "mlb_avg_pitcher": mlb_avg_pitcher
#     })

from flask import Flask, jsonify, render_template, request
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route("/")
def index():
   return  render_template('chart.html')
@app.route("/get_data")
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

if __name__ == '__main__':
    app.run(debug=True)
