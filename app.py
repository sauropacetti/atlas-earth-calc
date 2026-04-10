import streamlit as st
import plotly.graph_objects as go

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Atlas Earth IT Calc", layout="centered")
st.title("🇮🇹 Atlas Earth Italy Calculator")

# --- SIDEBAR: INPUT UTENTE ---
st.sidebar.header("I tuoi Terreni")
c = st.sidebar.number_input("Comuni", min_value=0, value=10)
r = st.sidebar.number_input("Rari", min_value=0, value=5)
e = st.sidebar.number_input("Epici", min_value=0, value=2)
l = st.sidebar.number_input("Leggendari", min_value=0, value=1)

st.sidebar.header("Parametri Boost Standard")
ore_boost_daily = st.sidebar.slider("Ore di Boost standard al giorno", 0, 24, 20)
bonus_badge = st.sidebar.selectbox("Bonus Badge Passport %", [0, 5, 10, 15, 20, 25], index=0) / 100

st.sidebar.header("Parametri Super Rent Boost")
# Qui aggiungiamo il parametro richiesto
ore_srb_effettive = st.sidebar.slider("Ore di SRB (50x) coperte su 32 totali", 0, 32, 28)

st.sidebar.header("Analisi Investimento")
investimento = st.sidebar.number_input("Soldi investiti ($)", min_value=0.0, value=0.0)

# --- LOGICA DI CALCOLO ITALIA ---
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

# Rendimento base al secondo
R_VALS = {"Comune": 0.0000000011, "Raro": 0.0000000016, "Epico": 0.0000000022, "Leggendario": 0.0000000044}
rend_base_sec = (c*R_VALS["Comune"] + r*R_VALS["Raro"] + e*R_VALS["Epico"] + l*R_VALS["Leggendario"]) * (1 + bonus_badge)

# --- CALCOLO CICLO DI 14 GIORNI (2 SETTIMANE) ---
ore_totali_14gg = 336 # 14 giorni * 24 ore

# 1. Calcolo SRB (50x)
# Le ore che non copri con il 50x durante l'evento tornano a 1x (o boost std se l'evento è finito)
rend_srb_periodo = (ore_srb_effettive * 3600 * rend_base_sec * 50) + \
                   ((32 - ore_srb_effettive) * 3600 * rend_base_sec)

# 2. Calcolo Ore Normali (fuori dalle 32h di evento)
ore_fuori_evento = ore_totali_14gg - 32
percentuale_boost_utente = ore_boost_daily / 24
ore_normali_con_boost = ore_fuori_evento * percentuale_boost_utente
ore_normali_senza_boost = ore_fuori_evento * (1 - percentuale_boost_utente)

rend_normale_periodo = (ore_normali_con_boost * 3600 * rend_base_sec * boost_std) + \
                        (ore_normali_senza_boost * 3600 * rend_base_sec)

# 3. Totali e Proiezioni
totale_14_giorni = rend_srb_periodo + rend_normale_periodo
mensile = (totale_14_giorni / 14) * 30.44
annuale = (totale_14_giorni / 14) * 365

# --- INTERFACCIA ---
col1, col2, col3 = st.columns(3)
col1.metric("Mensile Est.", f"${mensile:.2f}")
col2.metric("Annuale Est.", f"${annuale:.2f}")
col3.metric("Boost Italia", f"{boost_std}x")

st.info(f"Stai sfruttando {ore_srb_effettive} ore di Super Boost (50x) ogni 2 settimane
