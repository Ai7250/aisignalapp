import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from ta.momentum import RSIIndicator
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="💶 EUR/USD AI Signal", layout="wide")
st.title("💶 EUR/USD AI Signal with Debugging")

# Step 1: Define Parameters
symbol = "EURUSD=X"
interval = "1m"
period = "1d"

# Step 2: Fetch Data
st.markdown(f"📥 **Fetching {interval} data for {symbol}...**")
try:
    data = yf.download(tickers=symbol, interval=interval, period=period)
    if data.empty:
        st.error("❌ Data fetch failed! No data returned.")
        st.stop()
    st.success(f"✅ Data fetched! Shape: {data.shape}")
except Exception as e:
    st.error(f"❌ Error fetching data: {e}")
    st.stop()

# Step 3: Check Required Columns
required_cols = ['Open', 'High', 'Low', 'Close']
missing_cols = [col for col in required_cols if col not in data.columns]
if missing_cols:
    st.error(f"❌ Missing columns in data: {missing_cols}")
    st.stop()

# Step 4: Prepare Close Prices (ensure 1D)
close_prices = data['Close']
if isinstance(close_prices, pd.DataFrame) or len(close_prices.shape) > 1:
    close_prices = close_prices.squeeze()
st.success("✅ 'Close' prices ready.")

# Step 5: RSI Calculation
try:
    rsi = RSIIndicator(close=close_prices).rsi()
    data['rsi'] = rsi
    st.success("✅ RSI calculated.")
except Exception as e:
    st.error(f"❌ Error calculating RSI: {e}")
    data['rsi'] = np.nan

# Step 6: Candle Strength Calculation
try:
    data['candle_strength'] = (data['Close'] - data['Open']) / data['Open']
    candle_strength = data['candle_strength'].iloc[-1]
except Exception as e:
    candle_strength = None
    st.warning(f"⚠️ Candle strength error: {e}")

# Step 7: Gap Detection
try:
    gap = data['Open'].iloc[-1] - data['Close'].iloc[-2]
except Exception as e:
    gap = None
    st.warning(f"⚠️ Gap detection error: {e}")

# Step 8: Market Trend Detection
def detect_trend(df):
    recent = df['Close'].tail(20).tolist()  # convert to list for safe comparison
    if all(x < y for x, y in zip(recent, recent[1:])):
        return "Uptrend"
    elif all(x > y for x, y in zip(recent, recent[1:])):
        return "Downtrend"
    else:
        return "Ranging"

try:
    trend = detect_trend(data)
    st.success(f"📊 Market Trend: `{trend}`")
except Exception as e:
    trend = "Unknown"
    st.warning(f"⚠️ Trend detection error: {e}")

# Step 9: Support and Resistance Calculation
try:
    support = data['Low'].rolling(window=20).min().iloc[-1]
    resistance = data['High'].rolling(window=20).max().iloc[-1]
except Exception as e:
    support = resistance = None
    st.warning(f"⚠️ Support/Resistance error: {e}")

# Step 10: Best Price (Pullback Zone) Calculation
try:
    pullback_zone = data['Close'].rolling(window=20).mean()
    if not pullback_zone.empty and not pd.isna(pullback_zone.iloc[-1]):
        best_price = pullback_zone.iloc[-1]
    else:
        best_price = None
except Exception as e:
    best_price = None
    st.warning(f"⚠️ Error determining best price: {e}")

# Step 11: Display Key Information
st.markdown("### 📋 Market Snapshot")
col1, col2, col3 = st.columns(3)
col1.metric("🕯️ Candle Strength", f"{candle_strength:.5f}" if candle_strength is not None else "N/A")
col2.metric("🔀 Gap", f"{gap:.5f}" if gap is not None else "N/A")
col3.metric("📍 Best Price (Pullback)", f"{best_price:.5f}" if best_price is not None else "N/A")
col4, col5 = st.columns(2)
col4.metric("🟢 Support", f"{support:.5f}" if support is not None else "N/A")
col5.metric("🔴 Resistance", f"{resistance:.5f}" if resistance is not None else "N/A")
st.markdown(f"### 📊 Market Trend: `{trend}`")

# Step 12: Plot Candlestick Chart with Key Levels
try:
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candles'
    )])
    fig.update_layout(title='EUR/USD 1m Candle Chart', xaxis_rangeslider_visible=False)
    if support is not None:
        fig.add_hline(y=support, line_dash="dot", line_color="green", annotation_text="Support", opacity=0.4)
    if resistance is not None:
        fig.add_hline(y=resistance, line_dash="dot", line_color="red", annotation_text="Resistance", opacity=0.4)
    if best_price is not None:
        fig.add_hline(y=best_price, line_dash="dash", line_color="blue", annotation_text="Best Price Zone", opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.warning(f"⚠️ Error displaying chart: {e}")
