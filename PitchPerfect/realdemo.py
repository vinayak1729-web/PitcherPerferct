from flask import Flask, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('demo.html')

@app.route('/get_player_stats/<team_id>', methods=['GET'])
def get_player_stats(team_id):
    # Define the path for the batter and pitcher CSV files
    batter_file = f'dataset/2024/batters/{team_id}.csv'
    pitcher_file = f'dataset/2024/pitchers/{team_id}.csv'
    
    # Check if batter file exists, otherwise return error
    if os.path.exists(batter_file):
        batter_data = pd.read_csv(batter_file)
        batter_stats = batter_data.iloc[0]  # Extract stats from the first row
    else:
        return jsonify({'error': 'Batter data not found'}), 404

    # Check if pitcher file exists, otherwise return error
    if os.path.exists(pitcher_file):
        pitcher_data = pd.read_csv(pitcher_file)
        pitcher_stats = pitcher_data.iloc[0]  # Extract stats from the first row
    else:
        return jsonify({'error': 'Pitcher data not found'}), 404

    # Return the data as JSON
    stats = {
        'batter': {
            'ba': batter_stats['ba'],
            'est_ba': batter_stats['est_ba'],
            'slg': batter_stats['slg'],
            'est_slg': batter_stats['est_slg'],
            'woba': batter_stats['woba'],
            'est_woba': batter_stats['est_woba']
        },
        'pitcher': {
            'ba': pitcher_stats['ba'],
            'est_ba': pitcher_stats['est_ba'],
            'slg': pitcher_stats['slg'],
            'est_slg': pitcher_stats['est_slg'],
            'woba': pitcher_stats['woba'],
            'est_woba': pitcher_stats['est_woba']
        }
    }

    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True)
