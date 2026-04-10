import streamlit as st
import plotly.graph_objects as go

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Atlas Earth ROI Calculator", layout="centered")
st.title("🌍 Atlas Earth Profit & ROI Dashboard")

# --- SIDEBAR: INPUT UTENTE ---
st.sidebar.header("I tuoi Terreni")
c = st.sidebar.number_input("Comuni", min_value=0, value=10)
r = st.sidebar.number_input("Rari", min_value=0, value=5)
e = st.sidebar.number_input("Epici", min_value=0, value=2)
l = st.sidebar.number_input("Leggendari", min_value=0, value=1)

st.sidebar.header("Parametri Boost")
ore_boost = st.sidebar.slider("Ore di Boost attivo al giorno", 0, 24, 20)
giorni_srb = st.sidebar.slider("Giorni di Super Rent Boost (50x) al mese", 0, 4, 2)
bonus_badge = st.sidebar.selectbox("Bonus Badge Passport", [0, 5, 10, 15, 20, 25], index=0) / 100

st.sidebar.header("Analisi Investimento")
investimento = st.sidebar.number_input("Soldi investiti ($)", min_value=0.0, value=0.0, step=10.0)

# --- LOGICA DI CALCOLO ---
R_VALS = {"Comune": 0.0000000011, "Raro": 0.0000000016, "Epico": 0.0000000022, "Leggendario": 0.0000000044}
totale_terreni = c + r + e + l

# --- NUOVA LOGICA BOOST INTERNAZIONALE (ITALIA) vs USA ---
st.sidebar.header("Localizzazione")
regione = st.sidebar.radio("Mercato di riferimento", ["Internazionale (Italia)", "USA"])

def calcola_boost(totale, regione):
    if regione == "USA":
        if totale <= 150: return 30
        if totale <= 220: return 20
        if totale <= 290: return 15
        if totale <= 360: return 12
        if totale <= 430: return 10
        if totale <= 500: return 8
        if totale <= 625: return 7
        if totale <= 750: return 6
        if totale <= 875: return 5
        if totale <= 1000: return 4
        if totale <= 1500: return 3
        return 2
    else: # TABELLA INTERNAZIONALE (ITALIA)
        if totale <= 60: return 20
        if totale <= 110: return 15
        if totale <= 160: return 12
        if totale <= 210: return 8  # <--- Qui scatta l'8x dopo i 160 terreni
        if totale <= 260: return 7
        if totale <= 310: return 6
        if totale <= 360: return 5
        if totale <= 460: return 4
        if totale <= 560: return 3
        return 2

boost_std = calcola_boost(totale_terreni, regione)

# Rendimento base al secondo (con badge)
rend_base_sec = (c*R_VALS["Comune"] + r*R_VALS["Raro"] + e*R_VALS["Epico"] + l*R_VALS["Leggendario"]) * (1 + bonus_badge)

# Calcolo Mensile (considerando SRB e ore di boost)
giorni_normali = 30.44 - giorni_srb
# Entrate giorni normali
sec_boost_day = ore_boost * 3600
sec_no_boost_day = (24 - ore_boost) * 3600
rend_giornaliero_std = (sec_boost_day * rend_base_sec * boost_std) + (sec_no_boost_day * rend_base_sec)

# Entrate giorni SRB (solitamente 50x per 24h o ore specifiche, qui ipotizziamo 24h di boost disponibile)
rend_giornaliero_srb = (sec_boost_day * rend_base_sec * 50) + (sec_no_boost_day * rend_base_sec)

mensile = (rend_giornaliero_std * giorni_normali) + (rend_giornaliero_srb * giorni_srb)
annuale = mensile * 12

# --- VISUALIZZAZIONE RISULTATI ---
col1, col2, col3 = st.columns(3)
col1.metric("Mensile", f"${mensile:.2f}")
col2.metric("Annuale", f"${annuale:.2f}")
col3.metric("Boost Attuale", f"{boost_std}x")

# --- GRAFICO A TORTA ---
fig = go.Figure(data=[go.Pie(
    labels=list(R_VALS.keys()), 
    values=[c, r, e, l],
    hole=.4,
    marker_colors=['#BDC3C7', '#3498DB', '#9B59B6', '#F1C40F']
)])
fig.update_layout(title_text="Distribuzione Terreni")
st.plotly_chart(fig)

# --- SEZIONE BREAK-EVEN ---
st.subheader("📊 Analisi del Rientro (Break-even)")
if investimento > 0:
    mesi_per_be = investimento / mensile if mensile > 0 else 0
    st.write(f"Per recuperare il tuo investimento di **${investimento:.2f}**:")
    st.info(f"Tempo stimato: **{mesi_per_be:.1f} mesi** ({mesi_per_be/12:.1f} anni)")
    
    # Progress bar verso il recupero in un anno (esempio)
    progresso = min(annuale / investimento, 1.0) if investimento > 0 else 0
    st.write(f"Ritorno annuo sull'investimento (ROI): **{(annuale/investimento)*100:.1f}%**")
    st.progress(progresso)
else:
    st.success("Stai giocando in modalità Free-to-Play! Ogni centesimo è profitto puro.")

st.divider()
st.caption("Nota: I calcoli si basano sulle tabelle di rendimento 2026. Il Super Rent Boost è calcolato assumendo boost attivo per le ore selezionate.")
