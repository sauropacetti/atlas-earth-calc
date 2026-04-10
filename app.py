import streamlit as st
import plotly.graph_objects as go
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
import pandas as pd

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Atlas Earth IT Calc", layout="wide")
st.title("🌍 Atlas Earth Italy Calculator & Tracker")

# --- SIDEBAR: INPUT UTENTE ---
st.sidebar.header("🏰 I tuoi Terreni")
c = st.sidebar.number_input("Comuni", min_value=0, value=10)
r = st.sidebar.number_input("Rari", min_value=0, value=5)
e = st.sidebar.number_input("Epici", min_value=0, value=2)
l = st.sidebar.number_input("Leggendari", min_value=0, value=1)

st.sidebar.header("⚡ Parametri Boost")
ore_boost_daily = st.sidebar.slider("Ore di Boost standard al giorno", 0, 24, 20)
ore_srb_effettive = st.sidebar.slider("Ore di SRB (50x) coperte su 32 totali", 0, 32, 28)
bonus_badge = st.sidebar.selectbox("Bonus Badge Passport %", [0, 5, 10, 15, 20, 25], index=0) / 100

st.sidebar.header("💰 Investimento")
investimento = st.sidebar.number_input("Soldi investiti ($)", min_value=0.0, value=0.0)

# --- LOGICA DI CALCOLO (ITALIA) ---
totale_terreni = c + r + e + l

def get_boost_italia(n):
    if n <= 70: return 20
    if n <= 100: return 15
    if n <= 135: return 10
    if n <= 170: return 8
    if n <= 200: return 7
    if n <= 250: return 6
    if n <= 300: return 5
    if n <= 350: return 4
    if n <= 400: return 3
    return 2

boost_std = get_boost_italia(totale_terreni)

# Valori di rendimento base al secondo
R_VALS = {"Comune": 0.0000000011, "Raro": 0.0000000016, "Epico": 0.0000000022, "Leggendario": 0.0000000044}
rend_base_sec = (c*R_VALS["Comune"] + r*R_VALS["Raro"] + e*R_VALS["Epico"] + l*R_VALS["Leggendario"]) * (1 + bonus_badge)

# Calcolo Bi-settimanale (14 giorni = 336 ore)
ore_totali_14gg = 336
# Rendimento durante il periodo SRB (32 ore)
rend_srb_periodo = (ore_srb_effettive * 3600 * rend_base_sec * 50) + \
                   ((32 - ore_srb_effettive) * 3600 * rend_base_sec)
# Rendimento fuori SRB (304 ore)
ore_fuori_evento = ore_totali_14gg - 32
percentuale_boost_daily = ore_boost_daily / 24
rend_normale_periodo = (ore_fuori_evento * percentuale_boost_daily * 3600 * rend_base_sec * boost_std) + \
                        (ore_fuori_evento * (1 - percentuale_boost_daily) * 3600 * rend_base_sec)

# Proiezioni
tot_14gg = rend_srb_periodo + rend_normale_periodo
mensile = (tot_14gg / 14) * 30.44
annuale = (tot_14gg / 14) * 365

# --- LAYOUT PRINCIPALE: METRICHE ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Mensile Stimato", f"${mensile:.2f}")
m2.metric("Annuale Stimato", f"${annuale:.2f}")
m3.metric("Boost Attuale", f"{boost_std}x")
m4.metric("Terreni Totali", totale_terreni)

# --- GRAFICI E ANALISI ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Distribuzione Portafoglio")
    fig = go.Figure(data=[go.Pie(
        labels=list(R_VALS.keys()), 
        values=[c, r, e, l],
        hole=.4,
        marker_colors=['#BDC3C7', '#3498DB', '#9B59B6', '#F1C40F']
    )])
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("📈 Analisi ROI")
    if investimento > 0:
        mesi = investimento / mensile if mensile > 0 else 0
        st.write(f"**Break-even:** {mesi:.1f} mesi")
        st.write(f"**Ritorno Annuo (ROI):** {(annuale/investimento)*100:.1f}%")
        st.progress(min((annuale/investimento), 1.0))
    else:
        st.success("Modalità Free-to-Play: Profitto 100%")

# --- SEZIONE GOOGLE SHEETS (DIARIO) ---
st.divider()
st.header("📝 Diario Guadagni Reali")

try:
    # Connessione
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    
    # Apertura foglio (Assicurati che il nome sia identico!)
    sh = client.open("Atlas_Earth_Data").worksheet("Guadagni")
    
    with st.form("form_registro"):
        d_col, v_col = st.columns(2)
        data_log = d_col.date_input("Data", date.today())
        valore_log = v_col.number_input("Totale Accumulato ($)", format="%.4f")
        btn = st.form_submit_button("Salva nel Cloud")
        
        if btn:
            sh.append_row([str(data_log), valore_log])
            st.toast("Dato inviato con successo!", icon="✅")

    # Visualizzazione dati
    st.subheader("Ultimi record salvati")
    record_storici = sh.get_all_records()
    if record_storici:
        df_storico = pd.DataFrame(record_storici)
        st.dataframe(df_storico.tail(7), use_container_width=True)
    else:
        st.info("Nessun dato presente nel foglio Google.")

except Exception as e:
    st.error("⚠️ Errore di connessione a Google Sheets. Verifica i Secrets e la condivisione del foglio.")
    if st.checkbox("Mostra dettaglio errore"):
        st.code(str(e))
