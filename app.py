import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from sklearn.ensemble import RandomForestClassifier

st.title("💶 AI Signal for EUR/USD (1-Min Demo)")

# Fetch EUR/USD 1-min data
data = yf.download("EURUSD=X", interval="1m", period="1d")

# Check if data is empty
if data.empty:
    st.error("❌ Data fetch failed! EUR/USD 1m data not available.")
    st.stop()

# Preprocess
data.dropna(inplace=True)
close_prices = data['Close'].fillna(method="ffill").astype(float)

# Indicators
data['rsi'] = RSIIndicator(close=close_prices).rsi()
data['ema'] = EMAIndicator(close=close_prices, window=10).ema_indicator()

# Create target
data['future'] = data['Close'].shift(-1)
data['target'] = (data['future'] > data['Close']).astype(int)
data.dropna(inplace=True)

# Features & Model
features = ['Open', 'High', 'Low', 'Close', 'rsi', 'ema']
X = data[features]
y = data['target']

model = RandomForestClassifier()
model.fit(X[:-50], y[:-50])

# Prediction
last_row = X.iloc[-1].values.reshape(1, -1)
pred = model.predict(last_row)

# Display latest candle & signal
st.subheader("📊 Latest EUR/USD Candle")
st.dataframe(data[['Open', 'High', 'Low', 'Close']].tail(1))

if pred[0] == 1:
    st.success("🔼 Signal: Call (UP)")
else:
    st.error("🔽 Signal: Put (DOWN)")
