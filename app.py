import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="LB Quantum | Institutional Terminal", layout="wide")

# --- HEADER & STYLE ---
st.markdown("""
    <style>
    .main { background-color: #0b1016; color: #ffffff; }
    .title-text { font-size: 38px; font-weight: 800; color: #ffffff; margin-bottom: 0px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="title-text">LB QUANTUM ANALYTICS</p>', unsafe_allow_html=True)
st.caption("PREDICTIVE INTELLIGENCE | MULTI-FACTOR CONVERGENCE")
st.divider()

# --- TICKERS S&P 100 ---
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
            
            # Tendance (SMA 50)
            sma50 = prices.rolling(50).mean().iloc[-1]
            curr_p = prices.iloc[-1]
            trend = "Bullish" if curr_p > sma50 else "Bearish"
            
            # Algo Score
            score = 50
            if curr_p > sma50: score += 15
            if rsi < 35: score += 20
            if rsi > 70: score -= 20
            
            signal = "🟢 ACHAT FORT" if score >= 70 else "🔼 ACHAT" if score >= 60 else "🔻 VENTE" if score <= 40 else "⚪ NEUTRE"
            
            output.append({
                "Actif": t,
                "Prix ($)": round(curr_p, 2),
                "RSI": int(rsi),
                "Tendance": trend,
                "Confiance": f"{min(score, 98)}%",
                "Signal": signal,
                "Protection": round(curr_p * 0.95, 2)
            })
        except: continue
    
    df = pd.DataFrame(output)
    df.index = range(1, len(df) + 1)
    return df

# --- DASHBOARD ---
col_table, col_viz = st.columns([2, 1])

with col_table:
    st.subheader("Market Intelligence Scanner")
    df_final = get_market_intelligence()
    st.dataframe(df_final.sort_values(by="Confiance", ascending=False), use_container_width=True, height=500)

with col_viz:
    st.subheader("Technical Focus")
    selected = st.selectbox("Action :", df_final["Actif"].tolist())
    df_chart = yf.download(selected, period="6mo", progress=False)
    df_chart.columns = [c[0] if isinstance(c, tuple) else c for c in df_chart.columns]
    
    fig = go.Figure(data=[go.Candlestick(x=df_chart.index, open=df_chart['Open'], high=df_chart['High'], low=df_chart['Low'], close=df_chart['Close'])])
    fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

st.caption(f"© 2026 LB Quantum Analytics | Institutional Data Feed")
