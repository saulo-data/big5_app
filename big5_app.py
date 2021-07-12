#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 10:49:11 2021

@author: saulo
"""


#importing libraries
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st


#set stremalit layout as wide by default
st.set_page_config(
    layout = "wide"
    )

#data url
url = "https://fbref.com/en/comps/Big5/{}/{}-Big-5-European-Leagues-Stats"
url_current = "https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats"


#seasons to be analysed
seasons = ["2017-2018", "2018-2019", "2019-2020"]

#data preparing
dfs = []

#former seasons
for season in seasons:
    league = pd.read_html(url.format(season, season))[0]
    league["Season"] = season
    dfs.append(league)
   
#current season
current = pd.read_html(url_current)[0]
current["Season"] = "Current"
dfs.append(current)

#concat formers and current seasons
big5 = pd.concat(dfs, ignore_index=True)
vals_to_replace = {"de GER": "Bundesliga", "eng ENG": "Premier League", "it ITA": "Serie A",
                     "fr FRA": "Ligue 1", "es ESP": "La Liga"}
big5["Country"] = big5["Country"].map(vals_to_replace)
big5 = big5.rename(columns = {"Country": "League"})



#=======================================================================
#app title
st.title("Top 5 European Leagues Data")
st.write("All these data were collected from FBRef.com. There you can verify the authenticity of this report.")
#=======================================================================

#=======================================================================
#creating a checkbox


if st.checkbox("Show Dataframe"):
    st.dataframe(big5)
#=======================================================================


#=======================================================================
#Select Box
leagues = big5.League.drop_duplicates()
st.header("Expected Goals Stats of the Current Season")
my_league = st.selectbox("Select a League for the Expected Goals Bar and Scatter Plot", leagues)


#xG Charts


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
st.write("In this plot you can notice how a squad has been performing since the 2017-2018 Season")
st.write(my_league)
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
st.header("Relationship between some numeric values of the dataset")
st.write("Highlight any part of any chart to plot some relationship")
st.altair_chart(faced, use_container_width=True)
#=======================================================================

#=======================================================================
#bar charts
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

st.subheader("Expected Goals Difference by 90 min, League Rank and Points per Game")
st.write("Notice how these three metrics are correlated since 2017-18 Season on Top 5 Leagues")
st.write("This plot is interactive")
st.altair_chart(barras, use_container_width=True)
#=======================================================================

