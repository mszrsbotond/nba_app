import streamlit as st
import pandas as pd
from datetime import datetime as dt
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import BoxScoreTraditionalV2
import datetime

# set the page layout to wide
st.set_page_config(
    layout="wide",
)

# set up pages
query_params = st.query_params
#basic is the home page (main.py)
page = query_params.get("page", ["home"])[0]
game_id = query_params.get("game_id", [None])[0]  # Default to None

# set default day for today, so when pages opens it shows last night's results
day = datetime.date(dt.now().year, dt.now().month, dt.now().day)

# show a calendar selector where user can pick the date
if page == "home":
    # calendar selector
    day = st.date_input(
        "Date", datetime.date(dt.now().year, dt.now().month, dt.now().day)
    )

# set a today day so we can calculate the difference between todays date and the chosen one
today = datetime.date(dt.now().year, dt.now().month, dt.now().day)
# calculate the difference between todays date and the chosen one
day_from_today = (today-day).days



# load in games for the chosen day
def load_game_results(day):
    # load in the games data (every game occures twice in both team's perspective), 00 means NBA
    gamefinder = leaguegamefinder.LeagueGameFinder(date_from_nullable=day, date_to_nullable=day, league_id_nullable="00")

    # choose first occurences of games
    games_first = pd.DataFrame(gamefinder.get_data_frames()[0]).drop_duplicates(subset=["GAME_ID"], keep="first")
    # choose last occurences of games
    games_last = pd.DataFrame(gamefinder.get_data_frames()[0]).drop_duplicates(subset=["GAME_ID"], keep="last")
    # combine the two, if two rows have the same GAME_ID, convert them into one row
    games = games_first.merge(games_last, how="left", left_on="GAME_ID", right_on="GAME_ID")
    # drop season ID for both
    games = games.drop(columns=["SEASON_ID_x", "SEASON_ID_y"])
    
    # url for team logos
    team_url = "https://cdn.nba.com/logos/nba/{}/global/L/logo.svg"
    # url for games (recap)
    game_url = "https://www.nba.com/game/cle-vs-det-{}%3Fwatch?watchRecap=true"
    # set the logo url for the 1st team
    games["IMAGE_x"] = games["TEAM_ID_x"].apply(lambda pid: team_url.format(pid))
    # set the logo url for the 2nd team
    games["IMAGE_y"] = games["TEAM_ID_y"].apply(lambda pid: team_url.format(pid))
    # set the game url for the recap (same for both teams who play against each other)
    games["RECAP"] = games["GAME_ID"].apply(lambda pid: game_url.format(pid))
    return games


# create the "score boxes", that show the current day's games
def score_box(num_of_game):
    team_1_logo = games.iloc[num_of_game]["IMAGE_x"]
    team_2_logo = games.iloc[num_of_game]["IMAGE_y"]

    team_1_abbr = games.iloc[num_of_game]["TEAM_ABBREVIATION_x"]
    team_2_abbr = games.iloc[num_of_game]["TEAM_ABBREVIATION_y"]

    team_1_pts = games.iloc[num_of_game]["PTS_x"]
    team_2_pts = games.iloc[num_of_game]["PTS_y"]

    game_recap = games.iloc[num_of_game]["RECAP"]
    game_id = games.iloc[num_of_game]["GAME_ID"]
    return st.markdown(f"""
    <style>
        .scoreboard {{
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: #c2ddff;
            padding: 20px;
            border-radius: 20px;
            width: fit-content;
            margin-top: 30px;
        }}
        .team {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}
        .team img {{
            width: 60px;
            height: 60px;
            margin-right: 15px;
        }}
        .team-name {{
            font-size: 25px;
            color: black;
            font-weight: bold;
        }}
        .score {{
            font-size: 25px;
            font-weight: bold;
            color: black;
            margin-left: 50px;
        }}
        .box-score {{
            font-size: 15px;
            font-weight: bold;
            color: black;
            margin-top: 0px;
            margin-bottom: 0px;
        }}
        .game-recap {{
            font-size: 15px;
            font-weight: bold;
            color: black;
            margin-top: 0px;
            margin-bottom: 0px;
        }}
    </style>

    <div class="scoreboard">
        <div class="team">
            <img src="{team_1_logo}" alt="Team 1">
            <span class="team-name">{team_1_abbr}</span>
            <span class="score">{team_1_pts}</span>
        </div>
        <div class="team">
            <img src="{team_2_logo}" alt="Team 2">
            <span class="team-name">{team_2_abbr}</span>
            <span class="score">{team_2_pts}</span>
        </div>
        <span class="box-score"><a href="?page={game_id}" target="_self" style="color: black; text-decoration: none;">Boxscore</a></span>
        <span class="game-recap"><a href="{game_recap}" target="_blank" style="color: black; text-decoration: none;">Game Recap</a></span>
    </div>
""", unsafe_allow_html=True)


# Set the target depending on the chosen day
day_of_games = (dt.now() - pd.Timedelta(days=day_from_today+1)).strftime('%m/%d/%Y')

# loading in game results of the day
games = load_game_results(day_of_games)



# loading in box score for a specific game
def box_score_load_in(game_id):
    # load in boxscore with the given game id
    box_score = BoxScoreTraditionalV2(game_id=game_id)
    # get dataframes
    box_score = pd.DataFrame(box_score.get_data_frames()[0])
    # url for player pictures
    player_url = "https://cdn.nba.com/headshots/nba/latest/1040x760/{}.png"
    # create an image column, adding the players image url
    box_score["IMAGE"] = box_score["PLAYER_ID"].apply(lambda pid: player_url.format(pid))

    # convert to int and instead of None add 0s so we can calculate with the cells of the column
    box_score["FGA"] = box_score["FGA"].astype("Int64").fillna(0)
    box_score["FGM"] = box_score["FGM"].astype("Int64").fillna(0)
    box_score["FG3A"] = box_score["FG3A"].astype("Int64").fillna(0)
    box_score["FG3M"] = box_score["FG3M"].astype("Int64").fillna(0)
    box_score["FTA"] = box_score["FTA"].astype("Int64").fillna(0)
    box_score["FTM"] = box_score["FTM"].astype("Int64").fillna(0)

    # make fg column, fgm - fga
    box_score["FG"] = box_score["FGM"].astype(str) + " - " + box_score["FGA"].astype(str)
    # make 3pt column, fg3m - fg3a
    box_score["3PT"] = box_score["FG3M"].astype(str) + " - " + box_score["FG3A"].astype(str)
    # make ft column, ftm - fta
    box_score["FT"] = box_score["FTM"].astype(str) + " - " + box_score["FTA"].astype(str)

    # convert minutes into datetime format
    box_score["MIN"] = pd.to_datetime(box_score["MIN"], format="%M.000000:%S")
    # fill None with 0s
    box_score["MIN"] = box_score["MIN"].dt.minute.fillna(0)
    # calculate some kind of efficiency, but its really simplified, it wont be shown either, the only use case is that to show the best player from each team, and I short them by this value
    box_score["EFF"] = box_score["PTS"] + box_score["REB"] + box_score["AST"] + box_score["STL"] + box_score["BLK"] - box_score["TO"] - box_score["PF"] + (box_score["FG_PCT"] * box_score["FGA"]) + (box_score["FT_PCT"] * box_score["FTA"])
    # rename +/- column
    box_score = box_score.rename(columns= {"PLUS_MINUS": "+/-"})
    # sort values by team_id, so that the order of the teams will be the same in the box score too
    box_score = box_score.sort_values(by="TEAM_ID")
    # get the two cities (Clippers is LA, Lakers is Los Angeles)
    teams = box_score["TEAM_CITY"].unique()
    # 1st team
    team1_df = box_score[box_score["TEAM_CITY"] == teams[0]]
    # 2nd team
    team2_df = box_score[box_score["TEAM_CITY"] == teams[1]]
    return team1_df, team2_df

# team data for the teams that played in the box score page
def teams_in_game_load_in(game_id):
    # load in boxscore
    teams_data = BoxScoreTraditionalV2(game_id=game_id)
    # make dataframe
    teams_data = pd.DataFrame(teams_data.get_data_frames()[1])
    # make a team name column
    teams_data["TEAM"] = teams_data["TEAM_CITY"] + " " + teams_data["TEAM_NAME"]
    # logo url
    team_url = "https://cdn.nba.com/logos/nba/{}/global/L/logo.svg"
    # make logo column
    teams_data["LOGO"] = teams_data["TEAM_ID"].apply(lambda pid: team_url.format(pid))
    # sort by team id 
    teams_data = teams_data.sort_values(by="TEAM_ID")
    return pd.DataFrame(teams_data)

# create a result box showing logo, name and score
def result_box(team1_name, team2_name, team1_logo, team2_logo, team1_score, team2_score):
    return st.markdown(f"""
    <style>
        .scoreboard {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: #c2ddff;
            padding: 20px;
            border-radius: 20px;
            width: fit-content;
            margin: 30px auto;
        }}
        .team {{
            display: flex;
            align-items: center;
            margin-bottom: 5px;
        }}
        .team img {{
            width: 100px;
            height: 100px;
            margin-right: 15px;
            margin-left: 15px;
        }}
        .team-name {{
            font-size: 25px;
            color: black;
            font-weight: bold;
            margin-right: 15px;
        }}
        .score {{
            font-size: 35px;
            font-weight: bold;
            color: black;
            margin-left: 50px;
            margin-right: 50px;
        }}
    </style>

    <div class="scoreboard">
        <div class="team">
            <img src="{team1_logo}" alt="Team 1">
            <span class="team-name">{team1_name}</span>
            <span class="score">{team1_score}</span>
            <span class="score">{team2_score}</span>
            <span class="team-name">{team2_name}</span>
            <img src="{team2_logo}" alt="Team 2">
        </div>
""", unsafe_allow_html=True)

# create a best player from both teams box
def best_players(team1_best_player, team2_best_player):
    return st.markdown(f"""
    <style>
        .board {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: #c2ddff;
            padding: 0px;
            border-radius: 20px;
            width: fit-content;
            margin: auto auto;
            margin-bottom: 30px;
        }}
        .title {{
            font-size: 40px;
            color: black;
            font-weight: bold;
            margin-bottom: 0px;
            margin-top: 0px;
        }}
        .player-container {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .player {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 0px;
            text-align: center;
        }}
        .player img {{
            width: auto;
            height: 200px;
            margin-right: 10px;
            margin-left: 10px;
        }}
        .player-name {{
            font-size: 22px;
            color: black;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stats-name {{
            font-size: 32px;
            font-weight: bold;
            color: black;
            line-height: 70px;
            margin-left: 20px;
            margin-right: 20px;
            justify-content: center;
        }}
        .stats {{
            text-align: center;
            font-size: 35px;
            line-height: 70px;
            font-weight: bold;
            color: black;
            margin-left: 50px;
            margin-right: 50px;
        }}
    </style>

    <div class="board">
        <div class="title">
            <span>Best Perfomances</span>
        </div>
        <div class="player-container">
            <div class="player">
                <div class="player-name">{team1_best_player["PLAYER_NAME"].values[0]}</div>
                <img src="{team1_best_player["IMAGE"].values[0]}" alt="Player 1">
            </div>
            <div class="stats">
                <span>{team1_best_player["PTS"].values[0].astype(int)}<br>{team1_best_player["AST"].values[0].astype(int)}<br>{team1_best_player["REB"].values[0].astype(int)}</span>
            </div>
            <div class="stats-name">PTS<br>AST<br>REB</div>
            <div class="stats">
                <span>{team2_best_player["PTS"].values[0].astype(int)}<br>{team2_best_player["AST"].values[0].astype(int)}<br>{team2_best_player["REB"].values[0].astype(int)}</span>
            </div>
            <div class="player">
                <div class="player-name">{team2_best_player["PLAYER_NAME"].values[0]}</div>
                <img src="{team2_best_player["IMAGE"].values[0]}" alt="Player 2">
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# create a box for both starting fives (pics of players)
def starting5_box(team1_starting5, team2_starting5):

    # define players
    team1_starter1 = team1_starting5.iloc[0][["PLAYER_NAME", "IMAGE"]]
    team1_starter2 = team1_starting5.iloc[1][["PLAYER_NAME", "IMAGE"]]
    team1_starter3 = team1_starting5.iloc[2][["PLAYER_NAME", "IMAGE"]]
    team1_starter4 = team1_starting5.iloc[3][["PLAYER_NAME", "IMAGE"]]
    team1_starter5 = team1_starting5.iloc[4][["PLAYER_NAME", "IMAGE"]]
    team2_starter1 = team2_starting5.iloc[0][["PLAYER_NAME", "IMAGE"]]
    team2_starter2 = team2_starting5.iloc[1][["PLAYER_NAME", "IMAGE"]]
    team2_starter3 = team2_starting5.iloc[2][["PLAYER_NAME", "IMAGE"]]
    team2_starter4 = team2_starting5.iloc[3][["PLAYER_NAME", "IMAGE"]]
    team2_starter5 = team2_starting5.iloc[4][["PLAYER_NAME", "IMAGE"]]

    return st.markdown(f"""
    <style>
        .board {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background-color: #c2ddff;
            padding: 0px;
            border-radius: 20px;
            width: 1000px;
            margin: auto auto;
            margin-bottom: 30px;
        }}
        .title {{
            font-size: 40px;
            color: black;
            font-weight: bold;
            margin-bottom: 0px;
            margin-top: 0px;
        }}
        .players-container {{
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .players {{
            display: flex;
            flex-direction: row;
            align-items: center;
            margin-bottom: 0px;
            text-align: center;
        }}
        .players img {{
            width: auto;
            height: 100px;
            margin-right: -30px;
            margin-left: -30px;
        }}
        .players-name {{
            font-size: 22px;
            color: black;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .tab-space {{
            display: inline-block;
            width: 150px; /* Adjust width for tab spacing */
        }}
    </style>

    <div class="board">
        <div class="title">
            <span>Starting 5</span>
        </div>
        <div class="players-container">
            <div class="players">
                <img src="{team1_starter1['IMAGE']}" alt="Player 1">
                <img src="{team1_starter2['IMAGE']}" alt="Player 2">
                <img src="{team1_starter3['IMAGE']}" alt="Player 3">
                <img src="{team1_starter4['IMAGE']}" alt="Player 4">
                <img src="{team1_starter5['IMAGE']}" alt="Player 5">
                <span class="tab-space"></span>
            </div>
            <div class="players">
                <img src="{team2_starter1['IMAGE']}" alt="Player 1">
                <img src="{team2_starter2['IMAGE']}" alt="Player 2">
                <img src="{team2_starter3['IMAGE']}" alt="Player 3">
                <img src="{team2_starter4['IMAGE']}" alt="Player 4">
                <img src="{team2_starter5['IMAGE']}" alt="Player 5">
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)



#---------HOME-------------

# loop thorugh the games on the given day and show them
if page == "home":   
    row = st.columns(4)
    for i in range(len(games)):
        col = row[i % 4]
        with col:
            score_box(i)



#---------BOXSCORE-------------

# this is the boxscore page
else:
    # get the current url of the page bc it contains the game id
    current_url = st.query_params
    game_id_from_url = current_url["page"]

    # load in teams with the game id
    teams = teams_in_game_load_in(game_id_from_url)

    # get the required data for both teams
    team1_name = teams["TEAM"].values[0]
    team2_name = teams["TEAM"].values[1]
    team1_logo = teams["LOGO"].values[0]
    team2_logo = teams["LOGO"].values[1]
    team1_score = teams["PTS"].values[0]
    team2_score = teams["PTS"].values[1]

    # show the result of the game
    result_box(team1_name, team2_name, team1_logo, team2_logo, team1_score, team2_score)

    # load in box scores for both teams
    team1_df, team2_df = box_score_load_in(game_id_from_url)

    # getting the best player of team1
    team1_best_player = team1_df.sort_values(by="EFF", ascending = False).head(1)
    # getting the best player of team2
    team2_best_player = team2_df.sort_values(by="EFF", ascending = False).head(1)

    # showing the best players
    best_players(team1_best_player, team2_best_player)

    # get team1 starting 5
    team1_starting5 = team1_df[team1_df["START_POSITION"] != ""]
    # get team2 starting 5
    team2_starting5 = team2_df[team2_df["START_POSITION"] != ""]

    # show the starting fives
    starting5_box(team1_starting5, team2_starting5)

    # show the team logo above box score
    def logo(num_of_team):
        image_html = f"""
            <img src="{teams.iloc[num_of_team]['LOGO']}" alt="Team Logo" style="height:100px;">
                """
        return image_html
    
    # box scores for both teams
    st.markdown(logo(0), unsafe_allow_html=True)
    st.dataframe(team1_df, use_container_width=True, hide_index=True, height=len(team1_df)*38 , column_order = ("PLAYER_NAME", "MIN", "FG", "3PT", "FT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TO", "PF", "+/-", "PTS"))
    st.markdown(logo(1), unsafe_allow_html=True)
    st.dataframe(team2_df, use_container_width=True, hide_index=True, height=len(team2_df)*38 , column_order = ("PLAYER_NAME", "MIN", "FG", "3PT", "FT", "OREB", "DREB", "REB", "AST", "STL", "BLK", "TO", "PF", "+/-", "PTS"))


