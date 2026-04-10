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

st.sidebar.header("Parametri Boost")
ore_boost_daily = st.sidebar.slider("Ore di Boost standard al giorno", 0, 24, 20)
bonus_badge = st.sidebar.selectbox("Bonus Badge Passport %", [0, 5, 10, 15, 20, 25], index=0) / 100

st.sidebar.header("Analisi Investimento")
investimento = st.sidebar.number_input("Soldi investiti ($)", min_value=0.0, value=0.0)

# --- LOGICA DI CALCOLO INTERNAZIONALE ---
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
# In 14 giorni abbiamo:
# 1. 32 ore di SRB a 50x
# 2. Il resto del tempo a boost standard (se attivo) o 1x
ore_totali_14gg = 14 * 24 # 336 ore
ore_srb = 32
ore_normali = ore_totali_14gg - ore_srb # 304 ore

# Calcolo rendimento SRB (assumendo che nelle 32h l'utente sia boostato)
rend_srb_totale = ore_srb * 3600 * rend_base_sec * 50

# Calcolo rendimento ore normali
# Proporzione di ore boostate basata sulla media giornaliera dell'utente
percentuale_boost_utente = ore_boost_daily / 24
ore_normali_con_boost = ore_normali * percentuale_boost_utente
ore_normali_senza_boost = ore_normali * (1 - percentuale_boost_utente)

rend_normale_totale = (ore_normali_con_boost * 3600 * rend_base_sec * boost_std) + \
                      (ore_normali_senza_boost * 3600 * rend_base_sec)

# Totale Bi-settimanale e proiezioni
totale_14_giorni = rend_srb_totale + rend_normale_totale
mensile = (totale_14_giorni / 14) * 30.44
annuale = (totale_14_giorni / 14) * 365

# --- INTERFACCIA ---
col1, col2, col3 = st.columns(3)
col1.metric("Mensile Est.", f"${mensile:.2f}")
col2.metric("Annuale Est.", f"${annuale:.2f}")
col3.metric("Boost Italia", f"{boost_std}x")

st.write(f"**Nota:** Il calcolo include l'evento **SRB di 32 ore (50x)** ogni 2 giovedì.")

# --- GRAFICO A TORTA ---
fig = go.Figure(data=[go.Pie(
    labels=list(R_VALS.keys()), 
    values=[c, r, e, l],
    hole=.4,
    marker_colors=['#BDC3C7', '#3498DB', '#9B59B6', '#F1C40F']
)])
st.plotly_chart(fig)

# --- BREAK EVEN ---
if investimento > 0:
    st.subheader("📊 Analisi Rientro")
    mesi = investimento / mensile if mensile > 0 else 0
    st.info(f"Tempo stimato per il break-even: **{mesi:.1f} mesi**")
    st.write(f"ROI Annuo: **{(annuale/investimento)*100:.1f}%**")
