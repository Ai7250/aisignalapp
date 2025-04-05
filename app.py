import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from sklearn.ensemble import RandomForestClassifier

st.title("📈 AI Price Action Signal (Demo)")

# Download BTC 1-min data (last 1 day)
data = yf.download("BTC-USD", interval="1m", period="1d")

# Indicators
data['rsi'] = ta.momentum.RSIIndicator(data['Close']).rsi()
data['ema'] = ta.trend.EMAIndicator(data['Close'], window=10).ema_indicator()
data['future'] = data['Close'].shift(-1)
data['target'] = (data['future'] > data['Close']).astype(int)
data.dropna(inplace=True)

X = data[['Open', 'High', 'Low', 'Close', 'rsi', 'ema']]
y = data['target']

# Train model
model = RandomForestClassifier()
model.fit(X[:-50], y[:-50])
pred = model.predict([X.iloc[-1]])

st.subheader("Latest Candle:")
st.dataframe(data[['Open', 'High', 'Low', 'Close']].tail(1))

if pred[0] == 1:
    st.success("🔼 Signal: Call (UP)")
else:
    st.error("🔽 Signal: Put (DOWN)")
