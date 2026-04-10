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
rend_srb = (ore_srb_effettive * 3600 * rend_base_sec * 50) + ((32 - ore_srb_effettive) * 3600 * rend_base_sec)
# Standard (304 ore)
ore_std = ore_totali_cycle - 32
p_boost = ore_boost_daily / 24
rend_std = (ore_std * p_boost * 3600 * rend_base_sec * boost_std) + (ore_std * (1 - p_boost) * 3600 * rend_base_sec)

# Proiezioni
mensile = ((rend_srb + rend_std) / 14) * 30.44
annuale = mensile * 12

# --- DASHBOARD METRICHE ---
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Mensile Stimato", f"${mensile:.2f}")
col_m2.metric("Annuale Stimato", f"${annuale:.2f}")
col_m3.metric("Boost Attuale", f"{boost_std}x")

# --- GRAFICO E ROI ---
c1, c2 = st.columns(2)
with c1:
    fig = go.Figure(data=[go.Pie(labels=list(R_VALS.keys()), values=[c, r, e, l], hole=.4, 
                                 marker_colors=['#BDC3C7', '#3498DB', '#9B59B6', '#F1C40F'])])
    fig.update_layout(title="Rarità Terreni", margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig, use_container_width=True)
with c2:
    st.subheader("📊 Analisi Economica")
    if investimento > 0:
        mesi_be = investimento / mensile if mensile > 0 else 0
        st.write(f"**Break-even:** {mesi_be:.1f} mesi")
        st.write(f"**ROI Annuo:** {(annuale/investimento)*100:.1f}%")
        st.progress(min((annuale/investimento), 1.0))
    else:
        st.info("Modalità Free-to-Play attiva.")

# --- DIARIO GUADAGNI (GOOGLE SHEETS) ---
st.divider()
st.header("📝 Diario Guadagni Reali")

try:
    # Connessione API
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    sh = client.open("Atlas_Earth_Data").worksheet("Guadagni")

    # Form di inserimento
    with st.form("registro_guadagni"):
        f1, f2 = st.columns(2)
        data_ins = f1.date_input("Data", date.today())
        valore_ins = f2.number_input("Totale Accumulato ($)", min_value=0.0, format="%.6f", step=0.000001)
        if st.form_submit_button("Salva nel Cloud"):
            sh.append_row([str(data_ins), float(valore_ins)])
            st.toast("Dato salvato!", icon="✅")
            st.rerun()

    # Visualizzazione Storico
    st.subheader("📈 Storico Progressi")
    raw_data = sh.get_all_values()
    if len(raw_data) > 1:
        df = pd.DataFrame(raw_data[1:], columns=["Data", "Guadagno Totale"])
        # Pulizia e conversione
        df['Data'] = pd.to_datetime(df['Data']).dt.date
        df['Guadagno Totale'] = df['Guadagno Totale'].astype(str).str.replace(',', '.')
        df['Guadagno Totale'] = pd.to_numeric(df['Guadagno Totale'], errors='coerce').fillna(0.0)
        
        # Calcolo differenze giornaliere
        df = df.sort_values("Data")
        df['Guadagno Giornaliero'] = df['Guadagno Totale'].diff().fillna(0.0)
        df_display = df.sort_values("Data", ascending=False)

        st.dataframe(
            df_display,
            column_config={
                "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "Guadagno Totale": st.column_config.NumberColumn("Totale ($)", format="%.6f"),
                "Guadagno Giornaliero": st.column_config.NumberColumn("Delta ($)", format="%.6f")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.info("Nessun dato nel foglio.")

except Exception as e:
    st.error("⚠️ Errore di connessione a Google Sheets.")
    if st.checkbox("Mostra dettagli errore"):
        st.code(str(e))
