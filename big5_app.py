#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 10:49:11 2021

@author: saulo
"""


#libraries importing
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st


#setting the layout as "wide" by default
st.set_page_config(
    layout = "wide"
    )

#data url
url = "https://fbref.com/en/comps/Big5/{}/{}-Big-5-European-Leagues-Stats"
url_current = "https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats"


#seasons to be analysed
seasons = ["2017-2018", "2018-2019", "2019-2020", "2020-2021"]

#data preparation
dfs = []

#last seasons
for season in seasons:
    league = pd.read_html(url.format(season, season))[0]
    league["Season"] = season
    dfs.append(league)
   
#current season
current = pd.read_html(url_current)[0]
current["Season"] = "Current"
dfs.append(current)

#data concat
big5 = pd.concat(dfs, ignore_index=True)
vals_to_replace = {"de GER": "Bundesliga", "eng ENG": "Premier League", "it ITA": "Serie A",
                     "fr FRA": "Ligue 1", "es ESP": "La Liga"}
big5["Country"] = big5["Country"].map(vals_to_replace)
big5 = big5.rename(columns={"Country": "League"})




#=======================================================================
#app title
st.title("Top 5 European Leagues Data")
st.subheader("All these data were collected from [FBRef.com](https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats).")
st.write("""
         This app allows us to go deep inside the
         [Expected Goals metric(xG)](https://www.goal.com/en/news/what-is-xg-football-how-statistic-calculated/h42z0iiv8mdg1ub10iisg1dju) and performance.
        """)
#=======================================================================

#=======================================================================
#checkbox

if st.checkbox("Show Dataframe"):
    st.dataframe(big5)
#=======================================================================


#=======================================================================
#Select Box
leagues = big5.League.drop_duplicates()
st.header("xG of the current season")
my_league = st.selectbox("Select a League", leagues)


#xG graphs

barxG = alt.Chart(big5[(big5.League == my_league) & (big5["Season"] == "Current")]).mark_bar(
    cornerRadiusTopLeft=3,
    cornerRadiusTopRight=3
    ).encode(
    x = "Squad:N",
    y = "xG:Q",
    tooltip = ["W", "LgRk", "Top Team Scorer"],
    color = alt.condition(
        alt.datum.LgRk == 1,
        alt.value("green"),
        alt.value("lightgreen")
        )
      ).configure_axisX(
            labelAngle = -45
            )  
          


scatter_xg = alt.Chart(big5[(big5.League == my_league) & (big5.Season != "Current")]).mark_circle().encode(
        x = "Squad:N",
        y = "Season:O",
        size = "xG:Q",
        color = alt.Color("xG:Q", scale=alt.Scale(scheme='redyellowgreen')),
        tooltip = ["LgRk", "xG"]
        ).properties(
            height = 250
            ).configure_axisX(
            labelAngle = -45
            )  
                
                

st.altair_chart(barxG, use_container_width=True)

st.write("""
         Below we can see how a particular squad has been performing since 2017-78 season   
         """)
st.altair_chart(scatter_xg, use_container_width=True)
#=======================================================================


#=======================================================================
#Scatter Grid
interval = alt.selection_interval(encodings=['x'])

faced = alt.Chart(big5).mark_circle().encode(
    alt.X(alt.repeat("column"), type="quantitative"),
    alt.Y(alt.repeat("row"), type="quantitative"),
    color = alt.condition(interval, "GF", alt.value("black"),
                          scale=alt.Scale(scheme='greens')),    
    tooltip = ["Squad", "Season", "League", "LgRk",
               "Top Team Scorer", "Goalkeeper"]
    ).properties(
        width = 300,
        height = 150,
        selection = interval
        ).repeat(
        row = ["xG", "xGA", "xGD/90"],
        column = ["W", "D", "Pts/G"]
            )
st.header("Relationship between some numeric data of the dataset")
st.write("This plot is interactive")
st.write("")
st.altair_chart(faced, use_container_width=True)
#=======================================================================

#=======================================================================
#bar plot
interval = alt.selection_interval(encodings=['x'])

hist = alt.Chart(big5).mark_bar(
    cornerRadiusTopLeft=3,
    cornerRadiusTopRight=3
    ).encode(
    x = "LgRk:O",
    y = "mean(xGD/90)",
    color = alt.condition(interval, "LgRk", alt.value("black"),
                          sort="descending", scale=alt.Scale(scheme='greens'))
    ).properties(
        width = 1000,
        selection = interval
        )
        
barra2 = alt.Chart(big5).mark_bar(
    color = "#198a2e",
    cornerRadiusTopLeft=3,
    cornerRadiusTopRight=3
    ).encode(
    x = "mean(Pts/G)",
    y = "League:N"
    ).properties(
        width = 1000,
        height = 150
        ).transform_filter(
        interval
        )

barras = hist & barra2

st.header("Correlation between xGD/90, LgRk and Pts/G")
st.write("This plot is interactive")        
st.altair_chart(barras, use_container_width=True)

#=======================================================================
#squad
st.header("Which is the best formation for a particular squad?")
st.write("Go to [FBRef.com](https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats) -> Select a Squad -> Select a season from 2017-18 on -> Match Logs(National League) -> Copy the link")

equipe = st.text_input(label="Paste your link here", 
                       value="https://fbref.com/en/squads/822bd0ba/2020-2021/matchlogs/s10728/schedule/Liverpool-Scores-and-Fixtures-Premier-League")

squad = pd.read_html(equipe)[0]


time = alt.Chart(squad).mark_point().encode(
    x = "Opponent",
    y = "Formation",
    color = alt.Color("Result", scale=alt.Scale(scheme="dark2"), 
                      sort="descending"),
    shape = "Venue",
    size = "xG",
    tooltip = ["Date", "xGA", "Poss", "Captain"]
).properties(
    height = 300
).configure_axisX(
    labelAngle = -45
)

st.altair_chart(time, use_container_width=True)
#=======================================================================
#match
st.header("Look inside a match")
st.write("Go to [FBRef.com](https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats) -> Select a Squad-> Select a season from 2017-18 on -> Match Logs(National League) -> Match Report -> Copy the link")
partida = st.text_input(label="Paste your link here", 
                        value="https://fbref.com/en/matches/c2fc07f0/Liverpool-Crystal-Palace-May-23-2021-Premier-League")
match = pd.read_html(partida, header=1)[17]
jogo = alt.Chart(match).mark_point().encode(
        x = "Minute",
        y = "Outcome",
        color = alt.Color("Squad", scale=alt.Scale(scheme="dark2")),
        size = alt.Size("Distance", sort="descending", bin=alt.Bin(maxbins=6), title="Distance"),
        shape = "Body Part",
        tooltip = ["Player", "Distance"]
        ).properties(
            height = 300
            )
    
st.altair_chart(jogo, use_container_width=True)
#=======================================================================
st.write("Developed by [Saulo Faria](https://github.com/saulo-data)")
