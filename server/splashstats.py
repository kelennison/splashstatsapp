import matplotlib
matplotlib.use('Agg')  # Add this before other imports
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import plotly.graph_objects as go
import numpy as np
from PIL import Image
from io import BytesIO
import base64
from typing import List, Optional
from base64 import b64encode  # Add this import

plt.style.use('dark_background')

def calculate_percentiles(df, min_games=0.4):
    # Filter rows where games played is at least 70% of the maximum
    df_filtered = df

    # Select the last 9 columns for radar chart
    columns_for_radar = df.columns[-9:]

    # Define the number of columns to apply 'dense' method
    num_dense_columns = 3

    # Identify the first 3 columns for 'dense' method
    dense_columns = columns_for_radar[:num_dense_columns]

    # Identify the rest of the columns for 'average' method
    average_columns = columns_for_radar[num_dense_columns:-1]

    # Calculate percentiles using 'dense' method for the specified columns
    percentile_ranks_dense = df_filtered[dense_columns].rank(pct=True, method='dense') * 100

    # Calculate percentiles using 'average' method for the rest of the columns
    percentile_ranks_average = df_filtered[average_columns].rank(pct=True, method='average') * 100

    # Combine the percentiles back into the DataFrame
    dfpercentiles_df = pd.concat([percentile_ranks_dense, percentile_ranks_average], axis=1)

    # Reverse the percentile calculation for the last column
    last_column_percentile = 100 - df_filtered.iloc[:, -1].rank(pct=True) * 100

    # Add the last column percentile to the DataFrame
    dfpercentiles_df['Turnovers Per Game'] = last_column_percentile

    # Round the percentiles to one decimal place
    dfpercentiles_df = dfpercentiles_df.round(1)

    return dfpercentiles_df

# Helper Functions
def image_to_base64(image_path):
    with open(image_path, "rb") as f:
        return f"data:image/x-icon;base64,{b64encode(f.read()).decode('utf-8')}"

# Function to fetch and clean NBA data dynamically


def fetch_nba_data(season_type = 'regular',season='2023'):
    # Auto-adjust playoff seasons
    if season_type == 'playoffs' and int(season) > 2024:
        season = str(int(season) - 1)

    if season_type == 'regular':
        url = f"https://www.basketball-reference.com/leagues/NBA_{season}_per_game.html"
    else:
        url = f"https://www.basketball-reference.com/playoffs/NBA_{season}_per_game.html"

    html = pd.read_html(url, header=0)
    df = html[0]

    # Data cleaning
    raw = df.drop(df[df.Age == 'Age'].index)
    raw = raw.fillna(0)
    df = raw.drop(['Rk'], axis=1)

    # Standardize the team column name for playoffs data
    if season_type == 'playoffs' and 'Tm' in df.columns:
        df.rename(columns={'Tm': 'Team'}, inplace=True)

    # Handle 'TOT' team entries
    df['Team'] = df['Team'].astype(str)  # Convert all values in the 'Tm' column to strings
    df['Team'] = df.groupby('Player')['Team'].transform(lambda x: '/'.join(x.unique()))
    df = df[df['Team'] != 'TOT']
    df = df.drop_duplicates(subset='Player', keep='first')
    mask = df['Team'].str.contains('TOT/')
    df.loc[mask, 'Team'] = df.loc[mask, 'Team'].str.replace('TOT/', '')

    # Keep only relevant columns
    columns_to_keep = ['Player', 'Pos', 'Age', 'Team', 'G', 'MP', 'FG%', '3P%', 'FT%', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PTS']
    df = df[columns_to_keep]

    # Convert percentage columns to numeric and scale them
    columns_to_convert = ['FG%', '3P%', 'FT%']
    df[columns_to_convert] = df[columns_to_convert].apply(pd.to_numeric, errors='coerce') * 100
    df[columns_to_convert] = df[columns_to_convert].round(1)

    # Reorder and rename columns
    new_column_order = ['Player', 'Pos', 'Age', 'Team', 'G', 'MP', 'PTS', 'FG%', 'AST', 'TRB', 'STL', 'BLK', '3P%', 'FT%', 'TOV']
    df = df.loc[:, new_column_order]

    column_mapping = {
        'Pos': 'Position',
        'Team': 'Team',
        'G': 'Games',
        'MP': 'Minutes Per Game',
        'FG%': 'Field Goal %',
        '3P%': '3 Point %',
        'TRB': 'Rebounds Per Game',
        'AST': 'Assists Per Game',
        'BLK': 'Blocks Per Game',
        'TOV': 'Turnovers Per Game',
        'PTS': 'Points Per Game',
        'STL': 'Steals Per Game',
        'FT%': 'Free Throw %'
    }
    df.rename(columns=column_mapping, inplace=True)

    return df
# Add caching and season parameter to fetch_nba_data
cache = {}
def get_data_for_season(season, season_type='regular'):
    cache_key = (season, season_type)
    if cache_key in cache:
        return cache[cache_key]
    
    df = fetch_nba_data(season_type=season_type, season=season)
    df = df.set_index(df.columns[0])
    dfpercentiles_df = calculate_percentiles(df)
    Attributes = list(dfpercentiles_df.columns)
    AttNo = len(Attributes)
    
    cache[cache_key] = (df, dfpercentiles_df, Attributes, AttNo)
    return cache[cache_key]

# Load NBA player data dynamically
df = fetch_nba_data(season_type='regular',season='2025')
df = df.set_index(df.columns[0])

# Calculate percentiles
dfpercentiles_df = calculate_percentiles(df)

# Define radar chart attributes
Attributes = list(dfpercentiles_df.columns)
AttNo = len(Attributes)




# Define the radar chart function
def create_radar_chart(player, df, dfpercentiles_df, Attributes, AttNo, player2=None, player3=None, player4=None, min_games=0.4):
    try:
        values1 = dfpercentiles_df.loc[player].tolist()
        values1 += values1[:1]

        if player2:
            values2 = dfpercentiles_df.loc[player2].tolist()
            values2 += values2[:1]
        else:
            values2 = None

        if player3:
            values3 = dfpercentiles_df.loc[player3].tolist()
            values3 += values3[:1]
        else:
            values3 = None

        if player4:
            values4 = dfpercentiles_df.loc[player4].tolist()
            values4 += values4[:1]
        else:
            values4 = None

    except KeyError:
        return ("A player has not played the required minimum games.")

    angles1 = [n / float(AttNo) * 2 * np.pi for n in range(AttNo)]
    angles1 += angles1[:1]

    # Create the chart as before
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    # Create a figure and manually add axes
    fig = plt.figure(figsize=(6, 6),dpi=300)
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)

    plt.xticks(angles1[:AttNo], Attributes, color='black', fontsize=8)  # Smaller font size

    # Calculate label rotations
    label_rotations = np.linspace(0, 360, AttNo + 1)[:-1]
    for label, rotation in zip(ax.get_xticklabels(), label_rotations):
        label.set_rotation(rotation)

    ax.xaxis.grid(False)

    # Set y-axis ticks and labels
    yticks = [25, 50, 75, 100]
    ax.set_yticks(yticks)

    # Calculate minimum radius
    min_radius = np.min([np.min(values1)]) - 27
    min_radius1 = ax.get_ylim()[0]
    ax.set_ylim(bottom=min_radius1, top=100)

    ax.set_yticklabels([])

    # Add rectangular box for yticklabels
    for ytick in yticks:
        if ytick in [25, 50, 75, 100]:
            angle = np.deg2rad(90)
            radius = ytick
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            ax.text(angle, radius, str(ytick), ha='center', va='center', rotation='horizontal',
                    rotation_mode='anchor', fontsize=6, bbox=dict(boxstyle="round,pad=0.3", facecolor='black', edgecolor='#515353'), color='white')

    def add_image_to_polar(ax, image_path, angle, zoom=0.2):
        min_radius = ax.get_ylim()[0]
        x = min_radius * np.cos(np.deg2rad(angle))
        y = min_radius * np.sin(np.deg2rad(angle))
        img = plt.imread(image_path)
        imagebox = OffsetImage(img, zoom=zoom)
        ab = AnnotationBbox(imagebox, (x, y), frameon=False, pad=0.0)
        ax.add_artist(ab)

    add_image_to_polar(ax, "images/splash_stats_logo.png", angle=85, zoom=0.2)  # Smaller zoom

    # Plot and fill for player 1
    ax.plot(angles1, values1, color='#FF0000')
    ax.fill(angles1, values1, '#FF0000', alpha=0.25)

    # Get additional information from the DataFrame
    info_player = df.loc[player, ['Position', 'Team', 'Minutes Per Game']]

    # Adjust player 1 position to top left center
    text_player1 = plt.figtext(
        0.05, 1.2, f"{player}\n{info_player['Position']}, {info_player['Team']}\nMinutes Per Game: {info_player['Minutes Per Game']}", ha='left', va='center', fontsize=8, color="#FF0000", weight='bold')  # Smaller font size
    text_player1.set_text(
        f"{player}\n{info_player['Position']}, {info_player['Team']}\nMinutes Per Game: {info_player['Minutes Per Game']}")

    # Add text at the bottom right
    text = fig.text(0.05, -0.1, f"Graphic Design Inspired By\n McLachApp",
                    ha='left', va='center', fontsize=5, color='white', wrap=True)  # Smaller font size
    text2 = fig.text(0.95, -0.1, f"Designed By SplashStats\n Data from basketball-reference.com",
                     ha='right', va='center', fontsize=5, color='white', wrap=True)  # Smaller font size

    # Adding custom label rotations and scatter points for player 1
    angles = np.linspace(0, 2 * np.pi, len(ax.get_xticklabels()) + 1)
    angles[np.cos(angles) < 0] = angles[np.cos(angles) < 0] + np.pi
    angles = np.rad2deg(angles)

    # Customize rotations for specific ticks
    custom_rotations = [270, 310, 350, 35, 70, 290, 330, 10, 50]
    fontsize = 7  # Smaller font size

    for i, (label, angle) in enumerate(zip(ax.get_xticklabels(), angles)):
        x, y = label.get_position()
        lab = ax.text(x, y, label.get_text(), transform=label.get_transform(),
                      ha=label.get_ha(), va=label.get_va(), fontsize=fontsize)
        lab.set_rotation(custom_rotations[i])

    # Assuming Attributes2 is the list of attributes for the new radar chart
    columns_for_line = df.columns[-9:]

    # Calculate actual values for player 1
    values_a = df.loc[player, columns_for_line].tolist()
    values_a += values_a[:1]

    angles_a = [n / float(AttNo) * 2 * np.pi for n in range(AttNo)]
    angles_a += angles_a[:1]

    # Adding scatter points for player 1
    for i, (label, angle) in enumerate(zip(ax.get_xticklabels(), angles1)):
        x, y = label.get_position()
        rotation = custom_rotations[i]
        adjusted_angle = angle % 360
        ax.text(adjusted_angle, min(values1[i], 100), f'{float(values_a[i]):.1f}', color='#FF0000', ha='center', va='center',
                rotation_mode='anchor', fontsize=6, bbox=dict(boxstyle="circle,pad=0.15", facecolor='black', edgecolor='#FF0000'))  # Smaller font size
        ax.scatter(adjusted_angle, min(values1[i], 100), color='#FF0000', s=8)  # Smaller scatter size

    # Duplicates for player2, player 3 and player 4
    if player2:
        angles2 = [n / float(AttNo) * 2 * np.pi for n in range(AttNo)]
        angles2 += angles2[:1]
        values2 = dfpercentiles_df.loc[player2].tolist()
        values2 += values2[:1]

        # Plot and fill for player 2
        ax.plot(angles2, values2, color='#0000FF')
        ax.fill(angles2, values2, '#0000FF', alpha=0.25)
        info_player2 = df.loc[player2, ['Position', 'Team', 'Minutes Per Game']]
        text_player2 = plt.figtext(
            0.95, 1.2, f"{player2}\n{info_player2['Position']}, {info_player2['Team']}\nMinutes Per Game: {info_player2['Minutes Per Game']}", ha='right', va='center', fontsize=8, color="#0000FF", weight='bold')  # Smaller font size
        text_player2.set_text(
            f"{player2}\n{info_player2['Position']}, {info_player2['Team']}\nMinutes Per Game: {info_player2['Minutes Per Game']}")
        values_b = df.loc[player2, columns_for_line].tolist()
        values_b += values_b[:1]
        angles_b = [n / float(AttNo) * 2 * np.pi for n in range(AttNo)]
        angles_b += angles_b[:1]
        for i, (label, angle) in enumerate(zip(ax.get_xticklabels(), angles2)):
            x, y = label.get_position()
            rotation = custom_rotations[i]
            adjusted_angle = angle % 360
            ax.text(adjusted_angle, min(values2[i], 100), f'{float(values_b[i]):.1f}', color='#0000FF', ha='center', va='center',
                    rotation_mode='anchor', fontsize=6, bbox=dict(boxstyle="circle,pad=0.15", facecolor='black', edgecolor='#0000FF'))  # Smaller font size
            ax.scatter(adjusted_angle, min(values2[i], 100), color='#0000FF', s=8)  # Smaller scatter size

    if player3:
        angles3 = [n / float(AttNo) * 2 * np.pi for n in range(AttNo)]
        angles3 += angles3[:1]
        values3 = dfpercentiles_df.loc[player3].tolist()
        values3 += values3[:1]

        # Plot and fill for player 3
        ax.plot(angles3, values3, color='#00FF00')
        ax.fill(angles3, values3, '#00FF00', alpha=0.25)
        info_player3 = df.loc[player3, ['Position', 'Team', 'Minutes Per Game']]
        text_player3 = plt.figtext(
            0.05, 1.1, f"{player3}\n{info_player3['Position']}, {info_player3['Team']}\nMinutes Per Game: {info_player3['Minutes Per Game']}", ha='left', va='center', fontsize=8, color="#00FF00", weight='bold')  # Smaller font size
        text_player3.set_text(
            f"{player3}\n{info_player3['Position']}, {info_player3['Team']}\nMinutes Per Game: {info_player3['Minutes Per Game']}")
        values_c = df.loc[player3, columns_for_line].tolist()
        values_c += values_c[:1]
        angles_c = [n / float(AttNo) * 2 * np.pi for n in range(AttNo)]
        angles_c += angles_c[:1]
        for i, (label, angle) in enumerate(zip(ax.get_xticklabels(), angles3)):
            x, y = label.get_position()
            rotation = custom_rotations[i]
            adjusted_angle = angle % 360
            ax.text(adjusted_angle, min(values3[i], 100), f'{float(values_c[i]):.1f}', color='#00FF00', ha='center', va='center',
                    rotation_mode='anchor', fontsize=6, bbox=dict(boxstyle="circle,pad=0.15", facecolor='black', edgecolor='#00FF00'))  # Smaller font size
            ax.scatter(adjusted_angle, min(values3[i], 100), color='#00FF00', s=8)  # Smaller scatter size

    if player4:
        angles4 = [n / float(AttNo) * 2 * np.pi for n in range(AttNo)]
        angles4 += angles4[:1]
        values4 = dfpercentiles_df.loc[player4].tolist()
        values4 += values4[:1]

        # Plot and fill for player 4
        ax.plot(angles4, values4, color='#FFFF00')
        ax.fill(angles4, values4, '#FFFF00', alpha=0.25)
        info_player4 = df.loc[player4, ['Position', 'Team', 'Minutes Per Game']]
        text_player4 = plt.figtext(
            0.95, 1.1, f"{player4}\n{info_player4['Position']}, {info_player4['Team']}\nMinutes Per Game: {info_player4['Minutes Per Game']}", ha='right', va='center', fontsize=8, color="#FFFF00", weight='bold')  # Smaller font size
        text_player4.set_text(
            f"{player4}\n{info_player4['Position']}, {info_player4['Team']}\nMinutes Per Game: {info_player4['Minutes Per Game']}")
        values_d = df.loc[player4, columns_for_line].tolist()
        values_d += values_d[:1]
        angles_d = [n / float(AttNo) * 2 * np.pi for n in range(AttNo)]
        angles_d += angles_d[:1]
        for i, (label, angle) in enumerate(zip(ax.get_xticklabels(), angles4)):
            x, y = label.get_position()
            rotation = custom_rotations[i]
            adjusted_angle = angle % 360
            ax.text(adjusted_angle, min(values4[i], 100), f'{float(values_d[i]):.1f}', color='#FFFF00', ha='center', va='center',
                    rotation_mode='anchor', fontsize=6, bbox=dict(boxstyle="circle,pad=0.15", facecolor='black', edgecolor='#FFFF00'))  # Smaller font size
            ax.scatter(adjusted_angle, min(values4[i], 100), color='#FFFF00', s=8)  # Smaller scatter size

    ax.set_xticklabels([])

    # Additional tick parameters
    ax.tick_params(axis='x', labelsize=6, pad=15)  # Smaller font size and padding

    # Return the figure
    return fig


def create_player_stats_table(players, df):
    # Create a list to store table rows
    table_rows = []

    # Iterate through players and get their stats
    for player in players:
        player_stats = df.loc[player]
        table_row = [player] + player_stats.tolist()
        table_rows.append(table_row)

    # Get column names
    columns = ['Player'] + df.columns.tolist()
    row1 = 'red'
    row2 = 'blue'
    row3 = 'green'
    row4 = 'yellow'

    # Create the table with dark mode styling and player colors
    fig = go.Figure(data=[go.Table(
        columnwidth=[300, 140, 120, 150, 120, 150, 150, 140, 140, 180, 145, 145, 120, 130, 180],
        header=dict(
            values=columns,
            fill_color='#121212',
            font=dict(color='white', size=10),
            align='center'
        ),
        cells=dict(
            values=list(zip(*table_rows)),
            fill_color='#1a1a1a',
            font=dict(color=[[row1,row2,row3,row4]*4], size=10),  # Apply player colors
            height=30,
            align='center'
        )
    )])

    # Add dark mode layout configuration
    fig.update_layout(
        paper_bgcolor='#121212',
        plot_bgcolor='#1a1a1a',
        font=dict(size=10),
        autosize=True,  # Add this
        margin=dict(l=0, r=0, t=0, b=0),  # Remove all margins
        width=None,  # Let table determine its own width
        height=None  # Let table determine its own height
    )

    return fig

    