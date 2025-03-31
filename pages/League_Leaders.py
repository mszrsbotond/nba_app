import streamlit as st
import pandas as pd

# set the page orientation for wide
st.set_page_config(
    layout="wide",
)

# read in the file that contains all the 
df = pd.read_csv("combined_nba_stats.csv")

# all the seasons we have live data for
seasons_to_choose_from = [
    "2024-25", "2023-24", "2022-23", "2021-22", "2020-21",
    "2019-20", "2018-19", "2017-18", "2016-17", "2015-16",
    "2014-15", "2013-14", "2012-13", "2011-12", "2010-11",
    "2009-10", "2008-09", "2007-08", "2006-07", "2005-06",
    "2004-05", "2003-04", "2002-03", "2001-02", "2000-01",
    "1999-00", "1998-99", "1997-98", "1996-97"
]


# ----------------------------------------------------------------------------------------------- Top 5 Averages ------------------------------------------------------------------------------------------

st.title("Top Players by Stat and Season")

# select which season's stat you want to see
season_select = st.selectbox(
    "Season (avg)", seasons_to_choose_from
)

# define the 5 best players by any stat any season
def top5_players_by_stat(season, stat):
     # only looking at the correct season
     correct_season = df[df["Season"] == season]

     # sorting by the given stat and only giving back the top 5
     data_top5 = correct_season.sort_values(by=stat, ascending=False).head(5)

     # setting Name as index
     data_top5 = data_top5.set_index("Name")

     # instead of showing every column, only show the selected stat, the one we sort by too
     data_top5 = data_top5[stat]
     return data_top5


# set 3 columns for the stats to show
col1, col2, col3 = st.columns(3)

# show stats in the 1st column
with col1:
    st.write("POINTS PER GAME")
    st.dataframe(top5_players_by_stat(season_select, "Points / Game"), use_container_width=False)

    st.write("BLOCKS PER GAME")
    st.dataframe(top5_players_by_stat(season_select, "Blocks / Game"), use_container_width=False)

    st.write("FIELD GOALS MADE PER GAME")
    st.dataframe(top5_players_by_stat(season_select, "FG Made / Game"), use_container_width=False)

# show stats in the 2nd column
with col2:
    st.write("ASSISTS PER GAME")
    st.dataframe(top5_players_by_stat(season_select, "Assists / Game"), use_container_width=False)

    st.write("STEALS PER GAME")
    st.dataframe(top5_players_by_stat(season_select, "Steals / Game"), use_container_width=False)
    
    st.write("THREE POINTERS MADE PER GAME")
    st.dataframe(top5_players_by_stat(season_select, "3PTs Made / Game"), use_container_width=False)

# show stats in the 3rd column
with col3:
    st.write("REBOUNDS PER GAME")
    st.dataframe(top5_players_by_stat(season_select, "Rebounds / Game"), use_container_width=False)

    st.write("FIELD GOAL PERCENTAGE")
    st.dataframe(top5_players_by_stat(season_select, "Field Goal %"), use_container_width=False)

    st.write("THREE POINTERS PERCENTAGE")
    st.dataframe(top5_players_by_stat(season_select, "Three-Pointers %"), use_container_width=False)


# ----------------------------------------------------------------------------------------------- Interesting Insights ------------------------------------------------------------------------------------------

st.header("Interesting Insights")

three_pointers_by_year = {}
three_pointer_percentage_by_year = {}

for season in seasons_to_choose_from[::-1]:  # Reverse the list to start from the earliest season
    sum_3s = df[df["Season"]==season]["Three-Pointers Made"].sum()
    percent_3s = df[df["Season"]==season]["Three-Pointers %"].mean()

    three_pointers_by_year[season] = sum_3s
    three_pointer_percentage_by_year[season] = percent_3s

# set 11 columns to place the color dots and description
col1, col2 = st.columns(2)

with col1:
    st.write("Total 3 Pointers made across seasons")
    made_3s_df = pd.DataFrame(three_pointers_by_year.items())
    made_3s_df = made_3s_df.rename(columns={0:"Season", 1:"3 Pointers Made"})
    made_3s_df = made_3s_df.set_index("Season")
    st.line_chart(made_3s_df)


with col2:
    st.write("Total 3 Pointers Percentage across seasons")
    percent_3s_df = pd.DataFrame(three_pointer_percentage_by_year.items())
    percent_3s_df = percent_3s_df.rename(columns={0:"Season", 1:"3 %"})
    percent_3s_df = percent_3s_df.set_index("Season")
    st.bar_chart(percent_3s_df)



st.caption("""Over the past few decades, the three-point shot has completely transformed the NBA. What was once a niche weapon used by only a handful of players has now become the focal point of modern offenses. The data tells an undeniable story—teams are taking more three-pointers than ever, but the shooting percentage has remained nearly the same. The first chart shows a steady rise in the total number of three-pointers made per season, particularly from the early 2010s onward. This aligns with the rise of analytics-driven basketball, where teams prioritize three-point attempts over mid-range shots. However, the second chart reveals a surprising fact: the league-wide three-point percentage hasn’t improved significantly. Despite the increased volume, shooting efficiency has hovered around 35-38%. This trend suggests that while teams are emphasizing the three-pointer, the difficulty of the shot hasn’t changed. More players are attempting threes, but the NBA hasn’t necessarily become better at making them—just more reliant on them.""")























##data_to_show_avg_df = data_to_show_avg.reset_index()
#c = alt.Chart(data_to_show_avg_df).mark_bar().encode(
#    x=alt.X("3PTs Made / Game", scale=alt.Scale(domain=[min_value_avg - (min_value_avg/30), max_value_avg + (max_value_avg/30)], clamp=True)),
#    y=alt.Y("Name", sort=None),
#)
#
#
## set 11 columns to place the color dots and description
#col1, col2 = st.columns(2)
#with col1:
#    my_chart = st.altair_chart(c, use_container_width= False)
#
