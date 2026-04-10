import streamlit as st
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Atlas Earth IT Tracker", layout="wide")
st.title("🌍 Atlas Earth Italy: Calculator & Tracker")

# --- SIDEBAR: INPUT TERRENI ---
st.sidebar.header("🏰 I tuoi Terreni")
c = st.sidebar.number_input("Comuni", min_value=0, value=0)
r = st.sidebar.number_input("Rari", min_value=0, value=0)
e = st.sidebar.number_input("Epici", min_value=0, value=0)
l = st.sidebar.number_input("Leggendari", min_value=0, value=0)

st.sidebar.header("⚡ Parametri Boost")
ore_boost_daily = st.sidebar.slider("Ore di Boost standard al giorno", 0, 24, 20)
ore_srb_effettive = st.sidebar.slider("Ore di SRB (50x) coperte su 32 totali", 0, 32, 28)
bonus_badge = st.sidebar.selectbox("Bonus Badge Passport %", [0, 5, 10, 15, 20, 25], index=0) / 100

st.sidebar.header("💰 Investimento")
investimento = st.sidebar.number_input("Soldi investiti ($)", min_value=0.0, value=0.0, format="%.2f")

# --- LOGICA DI CALCOLO (TABELLA ITALIA 2026) ---
totale_terreni = c + r + e + l

def get_boost_italia(n):
    if n <= 60: return 20
    if n <= 110: return 15
    if n <= 160: return 12
    if n <= 210: return 8
    if n <= 260: return 7
    if n <= 310: return 6
    if n <= 360: return 5
    if n <= 460: return 4
    if n <= 560: return 3
    return 2

boost_std = get_boost_italia(totale_terreni)

# Rendita base per secondo
R_VALS = {"Comune": 0.0000000011, "Raro": 0.0000000016, "Epico": 0.0000000022, "Leggendario": 0.0000000044}
rend_base_sec = (c*R_VALS["Comune"] + r*R_VALS["Raro"] + e*R_VALS["Epico"] + l*R_VALS["Leggendario"]) * (1 + bonus_badge)

# Calcolo Ciclo 14 Giorni (336 ore)
ore_totali_cycle = 336
# SRB (32 ore)
rend_srb = (ore_srb_effettive * 3600 * rend_base_sec * 50) + ((32 - ore_srb_
