import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from ta.momentum import RSIIndicator
import plotly.graph_objects as go

st.set_page_config(page_title="EUR/USD AI Signal", layout="wide")

st.title("💶 EUR/USD AI Signal with Debugging")

# 🧠 Step 1: Data Fetch
symbol = 'EURUSD=X'
interval = '1m'
st.write(f"📥 Fetching {interval} data for: {symbol}")
data = yf.download(tickers=symbol, interval=interval, period="2d")

if data.empty:
    st.error("⚠️ Data not available. Check internet or symbol.")
    st.stop()

st.success(f"✅ Data fetched! Shape: {data.shape}")

# 📊 Step 2: Clean & Prepare
data = data.dropna()
data['Close'] = data['Close'].astype(float)
close_prices = data['Close']

# 🧠 Step 3: Calculate RSI + Handle Error
try:
    rsi = RSIIndicator(close=close_prices.squeeze()).rsi()
    data['RSI'] = rsi
    st.success("✅ RSI calculated.")
except Exception as e:
    st.error(f"❌ Error calculating RSI: {e}")
    st.stop()

# 📈 Step 4: Detect Trend
def detect_trend(data):
    highs = data['High'].rolling(window=3).max()
    lows = data['Low'].rolling(window=3).min()
    if highs.iloc[-1] > highs.iloc[-2] and lows.iloc[-1] > lows.iloc[-2]:
        return "Uptrend"
    elif highs.iloc[-1] < highs.iloc[-2] and lows.iloc[-1] < lows.iloc[-2]:
        return "Downtrend"
    else:
        return "Sideways"

trend = detect_trend(data)
st.info(f"📊 Market Trend: {trend}")

# 💪 Step 5: Candle Strength
last_candle = data.iloc[-1]
candle_strength = abs(last_candle['Close'] - last_candle['Open'])
st.write(f"🕯️ Candle Strength: {candle_strength:.5f}")

# 🔍 Step 6: Gap Up/Down Check
gap = last_candle['Open'] - data.iloc[-2]['Close']
st.write(f"🔀 Gap Detected: {gap:.5f}")

# 📉 Step 7: Support & Resistance Detection
def find_support_resistance(df, lookback=20):
    recent = df[-lookback:]
    support = recent['Low'].min()
    resistance = recent['High'].max()
    return support, resistance

support, resistance = find_support_resistance(data)
st.write(f"🟢 Support: {support:.5f}")
st.write(f"🔴 Resistance: {resistance:.5f}")

# 🧭 Step 8: Best Price (Pullback Zone)
best_price = None
if trend == "Uptrend":
    best_price = data['Low'].rolling(window=10).min().iloc[-1]
elif trend == "Downtrend":
    best_price = data['High'].rolling(window=10).max().iloc[-1]

st.write(f"📍 Best Price Zone: {best_price:.5_
