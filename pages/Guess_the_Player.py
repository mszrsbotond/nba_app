# import the required libraries
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import commonallplayers
import datetime as dt
import pandas as pd
import streamlit as st

# set site logo

# set the title
st.title("NBA Player Guesser")

# set 11 columns to place the color dots and description
col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11 = st.columns(11)

# set green dot
with col2:
    st.image("greendot.png", width=25)
with col3:
    st.write("Correct")

# set yellow dot
with col5:
    st.image("yellowdot.png", width=20)
with col6:
    st.write("Higher")

# set red dot
with col8:
    st.image("reddot.png", width=20)
with col9:
    st.write("Lower")



# load teams data (division, conference)
@st.cache_data
def load_teams_data():
    teams = pd.read_csv("teams.csv")
    return teams


# get all players data
@st.cache_data
def get_player_stats():
    players_all = commonallplayers.CommonAllPlayers(is_only_current_season=1).get_data_frames()[0].dropna(how="any")
    return players_all

# choose a random player the user will have to guess
def get_random_player_stats():
    player = get_player_stats().sample(n=1)
    return player


# load in the matching further stats for the player with matching its id
@st.cache_data
def load_player_stats(id):
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=id).get_data_frames()[0].dropna(how="any")
    return player_info

# load in all players
players_all = get_player_stats()
# load in all teams
teams = load_teams_data()

# adjust the dataframe (add, remove columns, change types)
@st.cache_data
def adjust_df(id):
    # load in one players stats provided by the id
    player_stats = load_player_stats(id).reset_index(drop=True)

    # url for the images of players
    url = "https://cdn.nba.com/headshots/nba/latest/1040x760/{}.png"

    # set the image column with formating the url
    player_stats["IMAGE"] = player_stats["PERSON_ID"].apply(lambda pid: url.format(pid))

    # converting the birth date to datetime
    player_stats["BIRTHDATE"] = pd.to_datetime(player_stats["BIRTHDATE"], utc = True)

    # making a name column that combines the first and last name
    player_stats["NAME"] = player_stats["FIRST_NAME"] + " " + player_stats["LAST_NAME"]

    # making a team column that combines the city and team name
    player_stats["TEAM"] = player_stats["TEAM_CITY"] + " " + player_stats["TEAM_NAME"]

    # adding the team information (division, conference)
    player_stats = player_stats.merge(teams, left_on="TEAM", right_on="TEAM")

    # calculating the age
    player_stats["AGE"] = dt.datetime.now().year - player_stats["BIRTHDATE"].dt.year

    # setting the correct types
    player_stats = player_stats.astype({"AGE": "Int64","JERSEY": "Int64"})

    # only looking at active players
    active_players = player_stats[player_stats["GAMES_PLAYED_FLAG"] == "Y"]

    # setting which columns to show and use
    active_players = active_players[["NAME", "TEAM", "POSITION","AGE", "COUNTRY", "CONFERENCE", "DIVISION", "JERSEY", "IMAGE"]]

    # drop all players who have at least one unknown stat
    active_players = active_players.dropna(how="any")
    return active_players


# locking the random player in session state
if 'random_player_id' not in st.session_state:
    st.session_state.random_player_id = get_random_player_stats()["PERSON_ID"].values[0]

# defining the soolution player
solution_player = adjust_df(st.session_state.random_player_id)


# guessing a player with a selectbox and returning the stats of the player
def guess_a_player():
    # guess a player by selecting/typing his name
    guessed_player = st.selectbox(
        f"Player", players_all["DISPLAY_FIRST_LAST"]
    )

    # getting the id of the guessed player, so later we can pass it in to get the correct dataframe for him
    guessed_player_id = players_all[players_all["DISPLAY_FIRST_LAST"] == guessed_player]["PERSON_ID"]

    # getting the dataframe by using the id
    guessed_player_stats = adjust_df(guessed_player_id)
    return guessed_player_stats

# making a list of the already guessed players, so they dont disappear when the user guesses again
if 'already_guessed' not in st.session_state:
    st.session_state.already_guessed = []

# defining the guessed player
guessed_player = guess_a_player()

# styling the guessed players dataframe
styled_guessed_player = guessed_player.style.apply(
    lambda x: [
        # setting the backgroung green if the guessed column is correct
        'background-color: #2E8B57' if col in ["NAME", "TEAM", "POSITION", "COUNTRY", "COLLEGE", "CONFERENCE", "DIVISION"] and x[col] == solution_player[col].values[0] else
        # setting the background yellow if the guess is lower than the solution
        'background-color: #a08a06' if col in ["AGE", "JERSEY"] and x[col] < solution_player[col].values[0] else
        # setting the background red if the guess is higher than the solution
        'background-color: #B22222' if col in ["AGE", "JERSEY"] and x[col] > solution_player[col].values[0] else
        # setting the background green if the guessed column is correct (handling independently because how python handles numbers)
        'background-color: #2E8B57' if col in ["AGE", "JERSEY"] and abs(x[col] - solution_player[col].values[0]) < 0.01 else
        ''
        for col in guessed_player.columns
    ], axis=1
).format(precision=1)

# always inserting the last guessed player on the first place of the list
st.session_state.already_guessed.insert(0, styled_guessed_player)

# setting up a guess counter
guess_count = 0

length = len(st.session_state.already_guessed)
placeholder = st.empty()

# gameplay
with placeholder.container():
    # looping through the guesses
    for i, guessed in enumerate(st.session_state.already_guessed):
        # increase guess count
        guess_count += 1
        # displaying the amount of guesses left
        st.write(f"{10- (length - guess_count)} guesse(s) left")
        # if still have guesses left
        if i < 10:
            # show guessed player
            st.dataframe(guessed, use_container_width=True, hide_index=True, column_order = ("NAME", "TEAM", "POSITION","AGE", "COUNTRY", "CONFERENCE", "DIVISION", "JERSEY"))
            # if user guessed it
            if solution_player["NAME"].values == guessed_player["NAME"].values:
                # using containers so we can clear the screen
                with placeholder.container():
                    st.write("YOU GOT IT")
                    # display the solution player's image
                    st.image(f"{solution_player["IMAGE"].values[0]}", width=200)
                    # display the solution player's dataframe
                    st.dataframe(styled_guessed_player, use_container_width=True, hide_index=True, column_order = ("NAME", "TEAM", "POSITION","AGE", "COUNTRY", "CONFERENCE", "DIVISION", "JERSEY"))
                    # add button for restart
                    if st.button("Click to Restart", key=f"correct_guess{i}"):
                        # clearing the already guessed list
                        st.session_state.already_guessed = []
                        # making a new random solution player
                        st.session_state.random_player_id = get_random_player_stats()["PERSON_ID"].values[0]
                        st.rerun()
        # if its the last guess and user correctly guesses it
        elif i == 10:
            # show the guessed player's dataframe
            st.dataframe(guessed, use_container_width=True, hide_index=True, column_order = ("NAME", "TEAM", "POSITION","AGE", "COUNTRY", "CONFERENCE", "DIVISION", "JERSEY"))
            # if guessed is correct
            if solution_player["NAME"].values == guessed_player["NAME"].values:
                with placeholder.container():
                    st.write("YOU GOT IT")
                    # show solution player image
                    st.image(f"{solution_player["IMAGE"].values[0]}", width=200)
                    # show styled solution player's dataframe
                    st.dataframe(styled_guessed_player, use_container_width=True, hide_index=True, column_order = ("NAME", "TEAM", "POSITION","AGE", "COUNTRY", "CONFERENCE", "DIVISION", "JERSEY"))
                    # make button for restart
                    if st.button("Click to Restart", key=f"correct_guess{i}"):
                        # clearing the already guessed list
                        st.session_state.already_guessed = []
                        # making a new random solution player
                        st.session_state.random_player_id = get_random_player_stats()["PERSON_ID"].values[0]
                        st.rerun()
            # if user couldn't guess it and runs out of guesses
            else:
                with placeholder.container():
                    st.write("You are out of guesses, the solution is: ")
                    # show solution player picture
                    st.image(f"{solution_player["IMAGE"].values[0]}", width=200)
                    # show solution dataframe
                    st.dataframe(solution_player, use_container_width=True, hide_index=True, column_order = ("NAME", "TEAM", "POSITION","AGE", "COUNTRY", "CONFERENCE", "DIVISION", "JERSEY"))
                    # create button for restart
                    if st.button("Click to Restart"):
                        # clearing the already guessed list
                        st.session_state.already_guessed = []
                        # making a new random solution player
                        st.session_state.random_player_id = get_random_player_stats()["PERSON_ID"].values[0]
                        st.rerun()

