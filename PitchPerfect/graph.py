from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # Serve the HTML page
    return render_template('chart.html')
teamid = 119
@app.route('/get_data')
def get_data():
    # Read CSV file (adjust file path as needed)
    batters_csv = pd.read_csv(f'dataset/2024/batters/{teamid}.csv')
    pitchers_csv = pd.read_csv(f'dataset/2024/pitchers/{teamid}.csv')

    # Convert DataFrame to dictionaries for JSON response
    batters_data = batters_csv.to_dict(orient='records')
    pitchers_data = pitchers_csv.to_dict(orient='records')

    return jsonify({'batters': batters_data, 'pitchers': pitchers_data})

if __name__ == '__main__':
    app.run(debug=True)
