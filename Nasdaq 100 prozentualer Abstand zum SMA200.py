import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st

# Name des Index oder der Aktie
ticker = "^NDX"

# Download der historischen Daten für beliebige Zeiträume bis heute
start_date = (pd.to_datetime("today") - pd.DateOffset(years=30)).strftime('%Y-%m-%d')
end_date = pd.to_datetime("today").strftime('%Y-%m-%d')
nasdaq = yf.Ticker(ticker)
hist = nasdaq.history(start=start_date, end=end_date, interval='1d')

# Berechnung des SMA 200
hist['SMA200'] = hist['Close'].rolling(window=200).mean()

# Relativer Abstand von SMA 200 zu dem jeweiligen Schlusskurs in Prozent
hist['PctDistFromSMA200'] = ((hist['High'] - hist['SMA200']) / hist['SMA200']) * 100

# 2. Y-Achse
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Nasdaq 100 Chart ins Diagramm hinzufügen
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['Close'],
    marker_color='blue',
    name='Nasdaq 100',
    line=dict(width=2)
), secondary_y=False)

# SMA 200 Abstand zum Diagramm hinzufügen
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['PctDistFromSMA200'],
    marker_color='red',
    name='Pct Distance from SMA 200',
    line=dict(width=2)
), secondary_y=True)

# Layout designen
fig.update_layout(
    title={'text': 'Nasdaq 100 and Percentage Distance from SMA 200 (Last 3 Years)', 'x': 0.5},
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='black')
)

fig.update_xaxes(
    showgrid=True,
    color='black'
)

fig.update_yaxes(
    showgrid=True,
    color='black'
)

fig.update_yaxes(
    title_text="Nasdaq 100", 
    secondary_y=False,
    type='log'
)

fig.update_yaxes(
    title_text="Pct Distance from SMA 200", 
    secondary_y=True
)

fig.update_xaxes(rangebreaks=[
    dict(bounds=['sat', 'mon']),
    dict(values=["2021-12-25", "2022-01-01"])
])

fig.update_xaxes(rangeslider_visible=True)

fig.show()

st.plotly_chart(fig)
