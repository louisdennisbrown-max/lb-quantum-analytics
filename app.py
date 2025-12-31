import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="LB Quantum | Institutional Terminal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b1016; color: #ffffff; }
    .stDataFrame { border: 1px solid #1e293b; border-radius: 10px; }
    .title-text { font-size: 38px; font-weight: 800; color: #ffffff; letter-spacing: -1px; margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<p class="title-text">LB QUANTUM ANALYTICS</p>', unsafe_allow_html=True)
st.markdown('<p style="color: #8b949e; font-weight: 500;">PREDICTIVE INTELLIGENCE | S&P 100 MARKET COVERAGE</p>', unsafe_allow_html=True)
st.divider()

# --- TOP 100 TICKERS ---
tickers_sp100 = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "BRK-B", "UNH", "LLY",
    "JPM", "XOM", "V", "MA", "AVGO", "HD", "PG", "COST", "JNJ", "ABBV",
    "CRM", "WMT", "BAC", "CVX", "MRK", "NFLX", "ADBE", "AMD", "PEP", "KO",
    "TMO", "WFC", "DIS", "CSCO", "ACN", "ABT", "ORCL", "LIN", "MCD", "INTC",
    "INTU", "VZ", "CMCSA", "AMGN", "PFE", "IBM", "TXN", "PM", "MS", "UNP",
    "HON", "RTX", "GS", "LOW", "CAT", "AXP", "QCOM", "GE", "SPGI", "BLK",
    "DE", "SYK", "AMAT", "PLD", "BA", "ISRG", "MDLZ", "TJX", "T", "GILD",
    "LRCX", "VRTX", "BKNG", "ETN", "REGN", "C", "MMC", "ADP", "CI", "ADI",
    "BSX", "ZTS", "MDT", "MU", "SCHW", "CVS", "WM", "LMT", "PANW", "FI",
    "NOW", "SNPS", "CDNS", "ELV", "CB", "TGT", "MO", "DHR", "ICE", "PGR"
]

@st.cache_data(ttl=3600)
def get_market_intelligence():
    # Téléchargement groupé pour la vitesse
    data = yf.download(tickers_sp100, period="1y", interval="1d", progress=False)['Close']
    output = []
    
    for t in tickers_sp100:
        try:
            prices = data[t].dropna()
            if len(prices) < 50: continue
            
            # Calcul RSI
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
            
            # Tendance
            sma50 = prices.rolling(50).mean().iloc[-1]
            curr_p = prices.iloc[-1]
            
            # Algorithme de score
            score = 50
            if curr_p > sma50: score += 15
            if rsi < 35: score += 20
            if rsi > 70: score -= 20
            
            # Signal
            if score >= 70: signal = "🟢 ACHAT FORT"
            elif score >= 60: signal = "🔼 ACHAT"
            elif score <= 40: signal = "🔻 VENTE"
            else: signal = "⚪ NEUTRE"
            
            output.append({
                "Actif": t,
                "Prix ($)": round(curr_p, 2),
                "Confiance": f"{min(score, 98)}%",
                "Signal": signal,
                "Protection (Stop)": round(curr_p * 0.95, 2)
            })
        except: continue
    
    df = pd.DataFrame(output)
    # ICI : On réinitialise l'index pour qu'il commence à 1
    df.index = range(1, len(df) + 1)
    return df

# --- DASHBOARD ---
col_table, col_viz = st.columns([1.8, 1])

with col_table:
    st.subheader("Signal Intelligence Board")
    with st.spinner("Analyse du S&P 100 en cours..."):
        df_final = get_market_intelligence()
    
    # Affichage du tableau trié par Confiance
    st.dataframe(df_final.sort_values(by="Confiance", ascending=False), use_container_width=True, height=550)

with col_viz:
    st.subheader("Technical Focus")
    selected = st.selectbox("Action à isoler :", df_final["Actif"].tolist())
    
    # Historique court pour le graph
    df_chart = yf.download(selected, period="6mo", progress=False)
    df_chart.columns = [c[0] if isinstance(c, tuple) else c for c in df_chart.columns]
    
    fig = go.Figure(data=[go.Candlestick(
        x=df_chart.index, open=df_chart['Open'], high=df_chart['High'],
        low=df_chart['Low'], close=df_chart['Close'],
        increasing_line_color='#00ff88', decreasing_line_color='#ff3366'
    )])
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"Analyse terminée pour {selected}. Convergence détectée.")

st.divider()
st.caption(f"LB QUANTUM ANALYTICS | Mise à jour : {datetime.now().strftime('%H:%M:%S')} | © 2026")
