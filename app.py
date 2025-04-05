import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from ta.momentum import RSIIndicator
import datetime

st.set_page_config(page_title="💶 EUR/USD AI Signal", layout="wide")

st.title("💶 EUR/USD AI Signal with Debugging")
symbol = "EURUSD=X"
interval = "1m"
period = "1d"

# 📥 Fetch Data
st.write(f"📥 Fetching 1m data for: {symbol}")
data = yf.download(tickers=symbol, interval=interval, period=period)

if data.empty:
    st.error("❌ Failed to fetch data.")
    st.stop()

st.success(f"✅ Data fetched! Shape: {data.shape}")

# Ensure proper column
if 'Close' not in data.columns:
    st.error("❌ 'Close' column not found in data.")
    st.stop()

# Prepare close prices
close_prices = data['Close']
if isinstance(close_prices, pd.DataFrame) or len(close_prices.shape) > 1:
    close_prices = close_prices.squeeze()

st.success("✅ 'Close' prices ready.")

# 🧮 RSI Calculation with check
try:
    rsi = RSIIndicator(close=close_prices).rsi()
    data['rsi'] = rsi
    st.success("✅ RSI calculated.")
except Exception as e:
    st.error(f"❌ Error calculating RSI: {e}")
    st.stop()

# ✨ Candle Strength
data['candle_strength'] = (data['Close'] - data['Open']) / data['Open']
candle_strength = data['candle_strength'].iloc[-1]

# 🔍 Gap Detection
gap = data['Open'].iloc[-1] - data['Close'].iloc[-2]

# 📈 Trend Detection
def detect_trend(df):
    recent = df['Close'].tail(20)
    if all(x < y for x, y in zip(recent, recent[1:])):
        return "Uptrend"
    elif all(x > y for x, y in zip(recent, recent[1:])):
        return "Downtrend"
    else:
        return "Ranging"

trend = detect_trend(data)

# 📊 Support and Resistance (basic)
support = data['Low'].rolling(window=20).min().iloc[-1]
resistance = data['High'].rolling(window=20).max().iloc[-1]

# ⭐ Best Price (Pullback zone)
pullback_zone = data['Close'].rolling(window=20).mean()
best_price = pullback_zone.iloc[-1] if not pullback_zone.isna().iloc[-1] else None

# 📍 Display Key Info
st.markdown(f"### 📊 Market Trend: `{trend}`")
st.markdown(f"**🕯️ Candle Strength:** `{candle_strength:.5f}`")
st.markdown(f"**🔀 Gap Detected:** `{gap:.5f}`")
st.markdown(f"**🟢 Nearest Support:** `{support:.5f}`")
st.markdown(f"**🔴 Nearest Resistance:** `{resistance:.5f}`")

if best_price:
    st.markdown(f"**📍 Best Price (Pullback Zone):** `{best_price:.5f}`")
else:
    st.warning("❌ Best Price not found.")

# 📈 Show Candle Chart
import plotly.graph_objects as go
fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close']
)])
fig.update_layout(title='EUR/USD 1m Candle Chart', xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
