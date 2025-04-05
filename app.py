import streamlit as st
import websocket
import json
import pandas as pd
import numpy as np
import ta
from ta.momentum import RSIIndicator
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="💶 EUR/USD AI Signal via Deriv API", layout="wide")
st.title("💶 EUR/USD AI Signal via Deriv API (1-minute candles)")

# ----------------------------------------------------
# Step 1: API Connection Parameters
# Deriv demo WebSocket endpoint (app_id=1089 is a demo app id)
ws_url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

# Request for historical candles:
# "ticks_history" endpoint with granularity in seconds (60 for 1-min)
request_data = {
    "ticks_history": "frxEURUSD",
    "granularity": 60,   # 1 minute candles
    "count": 100,        # last 100 candles
    "end": "latest"
}

# ----------------------------------------------------
# Step 2: Function to Fetch Candle Data from Deriv API
def fetch_candle_data(ws_url, req):
    try:
        ws = websocket.create_connection(ws_url)
        ws.send(json.dumps(req))
        result = ws.recv()
        ws.close()
        response = json.loads(result)
        # Check if candles data is available in the response
        if "candles" in response:
            candles = response["candles"]
            df = pd.DataFrame(candles)
            # Convert epoch to datetime and set as index
            df['time'] = pd.to_datetime(df['epoch'], unit='s')
            # Convert open, high, low, close to float
            for col in ['open', 'high', 'low', 'close']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df.dropna(subset=['open','high','low','close'])
            df.set_index('time', inplace=True)
            return df
        else:
            st.error("No candle data returned from API.")
            return None
    except Exception as e:
        st.error(f"Error fetching candle data: {e}")
        return None

data = fetch_candle_data(ws_url, request_data)
if data is None or data.empty:
    st.stop()
else:
    st.success(f"✅ Data fetched! {data.shape[0]} candles received.")

# ----------------------------------------------------
# Step 3: Calculate RSI using 'ta' library
try:
    # Ensure we use the 'close' column (1D Series)
    rsi = RSIIndicator(close=data['close']).rsi()
    data['rsi'] = rsi
    st.success("✅ RSI calculated.")
except Exception as e:
    st.error(f"Error calculating RSI: {e}")
    data['rsi'] = np.nan

# ----------------------------------------------------
# Step 4: Calculate Candle Strength and Gap
try:
    # Candle strength: (close - open)/open
    data['candle_strength'] = (data['close'] - data['open']) / data['open']
    candle_strength = data['candle_strength'].iloc[-1]
except Exception as e:
    candle_strength = None
    st.warning(f"Candle strength error: {e}")

try:
    # Gap: difference between current candle's open and previous candle's close
    gap = data['open'].iloc[-1] - data['close'].iloc[-2]
except Exception as e:
    gap = None
    st.warning(f"Gap calculation error: {e}")

# ----------------------------------------------------
# Step 5: Trend Detection using Last 3 Candles (Higher High & Higher Low)
def detect_trend(df):
    if len(df) < 3:
        return "Unknown"
    last_highs = df['high'].tail(3).values
    last_lows  = df['low'].tail(3).values
    if last_highs[0] < last_highs[1] < last_highs[2] and last_lows[0] < last_lows[1] < last_lows[2]:
        return "Uptrend"
    elif last_highs[0] > last_highs[1] > last_highs[2] and last_lows[0] > last_lows[1] > last_lows[2]:
        return "Downtrend"
    else:
        return "Ranging"

try:
    trend = detect_trend(data)
    st.success(f"📊 Market Trend: {trend}")
except Exception as e:
    trend = "Unknown"
    st.warning(f"Trend detection error: {e}")

# ----------------------------------------------------
# Step 6: Support and Resistance Calculation (Rolling 20-candle window)
try:
    support = data['low'].rolling(window=20).min().iloc[-1]
    resistance = data['high'].rolling(window=20).max().iloc[-1]
except Exception as e:
    support = resistance = None
    st.warning(f"Support/Resistance error: {e}")

# ----------------------------------------------------
# Step 7: Best Price (Pullback Zone) Calculation based on Trend
def calculate_best_price(df, trend, window=3):
    recent = df.tail(window)
    if trend == "Uptrend":
        return float(recent['low'].min())
    elif trend == "Downtrend":
        return float(recent['high'].max())
    else:
        return None

try:
    best_price = calculate_best_price(data, trend)
except Exception as e:
    best_price = None
    st.warning(f"Error determining best price: {e}")

# ----------------------------------------------------
# Step 8: Display Key Metrics
st.markdown("### 📋 Market Snapshot")
col1, col2, col3 = st.columns(3)
col1.metric("🕯️ Candle Strength", f"{candle_strength:.5f}" if candle_strength is not None else "N/A")
col2.metric("🔀 Gap", f"{gap:.5f}" if gap is not None else "N/A")
col3.metric("📍 Best Price (Pullback)", f"{best_price:.5f}" if best_price is not None else "N/A")

col4, col5 = st.columns(2)
col4.metric("🟢 Support", f"{support:.5f}" if support is not None else "N/A")
col5.metric("🔴 Resistance", f"{resistance:.5f}" if resistance is not None else "N/A")
st.markdown(f"### 📊 Market Trend: {trend}")

# ----------------------------------------------------
# Step 9: Plot Candlestick Chart with Key Levels using Plotly
try:
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='Candles'
    )])
    fig.update_layout(title='EUR/USD 1m Candle Chart (Deriv API)', xaxis_rangeslider_visible=False)
    if support is not None:
        fig.add_hline(y=support, line_dash="dot", line_color="green", annotation_text="Support", opacity=0.4)
    if resistance is not None:
        fig.add_hline(y=resistance, line_dash="dot", line_color="red", annotation_text="Resistance", opacity=0.4)
    if best_price is not None:
        fig.add_hline(y=best_price, line_dash="dash", line_color="blue", annotation_text="Best Price Zone", opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.warning(f"Error displaying chart: {e}")
