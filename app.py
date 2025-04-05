import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="EUR/USD AI Signal", layout="wide")
st.title("💶 EUR/USD AI Signal with Debugging")

# Step 1: Download EUR/USD 1-minute data
symbol = "EURUSD=X"
st.info(f"📥 Fetching 1m data for: {symbol}")
data = yf.download(symbol, interval="1m", period="1d")

# Step 2: Check if data fetched
if data.empty:
    st.error("❌ Data NOT fetched. 'data' is empty.")
    st.stop()
else:
    st.success(f"✅ Data fetched! Shape: {data.shape}")
    st.dataframe(data.tail())

# Step 3: Drop NaNs
data.dropna(inplace=True)

# Step 4: Fix Close prices (ensure 1D)
if 'Close' not in data.columns:
    st.error("❌ 'Close' column not found in data.")
    st.stop()

close_prices = data['Close'].fillna(method="ffill").astype(float)

if close_prices.empty:
    st.error("❌ 'Close' series is empty after processing.")
    st.stop()
else:
    st.success("✅ 'Close' prices ready.")
    st.line_chart(close_prices)

# Step 5: RSI Indicator
try:
    data['rsi'] = RSIIndicator(close=close_prices).rsi()
    st.success("✅ RSI calculated.")
    st.line_chart(data['rsi'].dropna())
except Exception as e:
    st.error(f"❌ Error calculating RSI: {e}")
    st.stop()

# Step 6: EMA Indicator
try:
    data['ema'] = EMAIndicator(close=close_prices, window=10).ema_indicator()
    st.success("✅ EMA calculated.")
    st.line_chart(data['ema'].dropna())
except Exception as e:
    st.error(f"❌ Error calculating EMA: {e}")
    st.stop()

# Step 7: Create Target
data['future'] = data['Close'].shift(-1)
data['target'] = (data['future'] > data['Close']).astype(int)
data.dropna(inplace=True)

if data['target'].empty:
    st.error("❌ 'target' column is empty.")
    st.stop()
else:
    st.success("✅ Target column created.")
    st.write(data[['Close', 'future', 'target']].tail())

# Step 8: Train RandomForest Model
features = ['Open', 'High', 'Low', 'Close', 'rsi', 'ema']
X = data[features]
y = data['target']

if X.empty or y.empty:
    st.error("❌ Features or Labels are empty.")
    st.stop()

model = RandomForestClassifier()
model.fit(X[:-50], y[:-50])

# Step 9: Predict on last candle
last_row = X.iloc[-1].values.reshape(1, -1)
pred = model.predict(last_row)

# Step 10: Show latest candle & prediction
st.subheader("📊 Latest EUR/USD Candle")
st.dataframe(data[['Open', 'High', 'Low', 'Close']].tail(1))

st.subheader("🤖 AI Signal")
if pred[0] == 1:
    st.success("🔼 Signal: CALL (Price Up)")
else:
    st.error("🔽 Signal: PUT (Price Down)")
