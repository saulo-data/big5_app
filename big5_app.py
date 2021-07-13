#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 10:49:11 2021

@author: saulo
"""


#importação das bibliotecas
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st


#configuração do layout deste app como "wide"
st.set_page_config(
    layout = "wide"
    )

#url dos dados
url = "https://fbref.com/en/comps/Big5/{}/{}-Big-5-European-Leagues-Stats"
url_current = "https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats"


#temporadas a serem analisadas
seasons = ["2017-2018", "2018-2019", "2019-2020"]

#preparação dos dados
dfs = []

#temporadas passadas
for season in seasons:
    league = pd.read_html(url.format(season, season))[0]
    league["Season"] = season
    dfs.append(league)
   
#temporada atual
current = pd.read_html(url_current)[0]
current["Season"] = "Atual"
dfs.append(current)

#concatenação dos datasets
big5 = pd.concat(dfs, ignore_index=True)
vals_to_replace = {"de GER": "Bundesliga", "eng ENG": "Premier League", "it ITA": "Serie A",
                     "fr FRA": "Ligue 1", "es ESP": "La Liga"}
big5["Country"] = big5["Country"].map(vals_to_replace)
big5 = big5.rename(columns = {"Country": "Liga", "W": "Vitórias", "D": "Empates",
                              "L": "Derrotas", "Squad": "Equipe", "GA" :"GS",
                              "GD": "SG", "Top Team Scorer": "Artilheiro", 
                              "Season": "Temporada", "Goalkeeper": "Goleiro",
                              "Attendance": "Público", "Rk": "PosGeral",
                              "LgRk": "PosLiga", "MP": "P", "Pts/G": "Pts/P"})



#=======================================================================
#título do app
st.title("Dados sobre as principais ligas europeias")
st.subheader("Todos estes dados foram coletados de [FBRef.com](https://fbref.com/en/comps/Big5/Big-5-European-Leagues-Stats). Clique no link e verifique os dados diretos na página")
st.write("""
        Este app tem como finalidade mostrar correlações entre os dados referentes
        aos [Gols Esperados(xG)](https://footure.com.br/expected-goals-xg-o-que-e-e-como-usa-lo-na-analise-do-futebol/) e desempenho das equipes ao longo das temporadas nas principais ligas europeias.
        """)
#=======================================================================

#=======================================================================
#criação de uma checkbox

if st.checkbox("Exibir Dataframe"):
    st.dataframe(big5)
#=======================================================================


#=======================================================================
#Select Box
leagues = big5.Liga.drop_duplicates()
st.header("Gols Esperados da Temporada atual")
my_league = st.selectbox("Escolha uma liga e verifique os dados sobre xG na temporada em andamento", leagues)


#xG gráficos

barxG = alt.Chart(big5[(big5.Liga == my_league) & (big5["Temporada"] == "Atual")]).mark_bar(
    cornerRadiusTopLeft=3,
    cornerRadiusTopRight=3
    ).encode(
    x = "Equipe:N",
    y = "xG:Q",
    tooltip = ["Vitórias", "PosLiga", "Artilheiro"],
    color = alt.condition(
        alt.datum.PosLiga == 1,
        alt.value("green"),
        alt.value("lightgreen")
        )
      ).configure_axisX(
            labelAngle = -45
            )  
          


scatter_xg = alt.Chart(big5[(big5.Liga == my_league) & (big5.Temporada != "Atual")]).mark_circle().encode(
        x = "Equipe:N",
        y = "Temporada:O",
        size = "xG:Q",
        color = alt.Color("xG:Q", scale=alt.Scale(scheme='redyellowgreen')),
        tooltip = ["PosLiga", "xG"]
        ).properties(
            height = 250
            ).configure_axisX(
            labelAngle = -45
            )  
                
                

st.altair_chart(barxG, use_container_width=True)

st.write("""No gráfico abaixo, é possível notar o desempenho de cada equipe, na liga selecionada acima, desde a temporada 2017-18.
            Quanto maior e mais para o verde for o círculo, maior seu xG.""")
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
    tooltip = ["Equipe", "Temporada", "Liga", "PosLiga",
               "Artilheiro", "Goleiro"]
    ).properties(
        width = 300,
        height = 150,
        selection = interval
        ).repeat(
        row = ["xG", "xGA", "xGD/90"],
        column = ["Vitórias", "Empates", "Pts/P"]
            )
st.header("Correlação entre alguns dados numéricos do dataframe")
st.subheader("Esta seção nos permite notar diversas interações entre diferentes gráficos")
st.markdown("""
            *As linhas de gráficos correspondem às métricas de Gols Esperados(xG),
            Gols Esperados Contra(xGA) e Saldo de Gols Esperados por 90 min(xGD/90)*
            
            *As colunas de gráficos se referem ao número de vitórias, empates e 
            Pontos por Partida.*
            
            *A variação de cor salienta o número de Gols a Favor.*
            
            *Basta arrastar a área selecionada para gerar interatividade.*
            """)
st.write("")
st.altair_chart(faced, use_container_width=True)
#=======================================================================

#=======================================================================
#gráficos de barras
interval = alt.selection_interval(encodings=['x'])

hist = alt.Chart(big5).mark_bar(
    cornerRadiusTopLeft=3,
    cornerRadiusTopRight=3
    ).encode(
    x = "PosLiga:O",
    y = alt.Y("mean(xGD/90)", title="Média - xGD/90"),
    color = alt.condition(interval, "PosLiga", alt.value("black"),
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
    x = alt.X("mean(Pts/P)", title="Média - Pts/P"),
    y = "Liga:N"
    ).properties(
        width = 1000,
        height = 150
        ).transform_filter(
        interval
        )

barras = hist & barra2

st.header("Saldo de xG, Posição na Liga e Pontos por Partida")
st.subheader("Esta seção mostra as correlações entre as três variáveis supracitadas.")
st.write("""
                
        *O **primeiro gráfico** tem as posições nas ligas na horizontal, e na
        vertical, a média de Saldo de xG por 90 min.*
        
        *O **segundo gráfico** tem a média de pontos por partida na horizontal, e na
        vertical, as ligas.*
        
        *Selecione um intervalo no primeiro gráfico e veja sua correspondência 
        no segundo gráfico. Foram consideradas todas as temporadas desde 2017-18*
        
        *Basta arrastar a área selecionada para gerar interatividade.*
        
        """)
st.altair_chart(barras, use_container_width=True)

#=======================================================================
#partida
st.header("Estudo de uma partida")
st.subheader("Aqui é possível fazer uma breve observação do que foi a partida.")

partida = st.text_input(label="Cole aqui o link da partida", 
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

#=======================================================================
#equipe
st.header("Veja a campanha de uma equipe")
st.subheader("Escolha uma equipe e veja como esta está performando")

equipe = st.text_input(label="Cole aqui o link da sua equipe", 
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