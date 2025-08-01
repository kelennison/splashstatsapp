import base64  # add this import at the top
import kaleido
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
from splashstats import (
    get_data_for_season,  # Add this
    df, dfpercentiles_df, Attributes, AttNo,
    create_radar_chart, create_player_stats_table
)

import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)  # Enable CORS so your JS app can call the backend

from flask import send_from_directory

@app.route('/google39cdea0edaf02c9e.html')
def serve_verification_file():
    return send_from_directory('../react-app/build', 'google39cdea0edaf02c9e.html')

@app.route('/api/players', methods=['GET'])
def get_players():
    season = request.args.get('season', '2025')  # Default to 2025
    season_type = request.args.get('type', 'regular')  # New parameter

    # Adjust season for playoffs if needed
    if season_type == 'playoffs' and season == '2025':
        effective_season = '2025'
    else:
        effective_season = season
        
    df, _, _, _ = get_data_for_season(effective_season, season_type)
    players = df.index.tolist()
    return jsonify(players)

@app.route('/api/radar', methods=['POST'])
def get_radar():
    data = request.get_json()
    season = data.get('season', '2025')
    season_type = data.get('season_type', 'regular')
    df, dfpercentiles_df, Attributes, AttNo = get_data_for_season(season,season_type)
    
    player1 = data.get('player1')
    player2 = data.get('player2') or None
    player3 = data.get('player3') or None
    player4 = data.get('player4') or None
    min_games = data.get('min_games', 0.4)
    
    # Generate the radar chart using your function
    fig = create_radar_chart(player1, df, dfpercentiles_df, Attributes, AttNo, player2, player3, player4)
    
    # Convert the Matplotlib figure to an image (for the radar chart) as before
    img_io = io.BytesIO()
    fig.savefig(img_io, format='png', bbox_inches="tight")
    img_io.seek(0)
    chart_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    
    # Build a list of selected players for the stats table
    selected_players = [p for p in [player1, player2, player3, player4] if p]
    
    # Generate the stats table as a Plotly figure
    table_fig = create_player_stats_table(selected_players, df)
    
    # Convert the Plotly figure to JSON
    table_json = table_fig.to_json()
    
    # Return both the static radar chart and the interactive table JSON
    return jsonify({
        "chart": chart_base64,
        "table_json": table_json
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
