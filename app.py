import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from sklearn.ensemble import RandomForestClassifier

st.title("📈 AI Price Action Signal (Demo)")

# Step 1: Download data
data = yf.download("BTC-USD", interval="1m", period="1d")

# Step 2: Drop NaN rows early to avoid RSI errors
data.dropna(inplace=True)

# Step 3: Indicators (safely)
try:
    data['rsi'] = ta.momentum.RSIIndicator(data['Close']).rsi()
    data['ema'] = ta.trend.EMAIndicator(data['Close'], window=10).ema_indicator()
except Exception as e:
    st.error("Error calculating indicators: " + str(e))

# Step 4: Create target column
data['future'] = data['Close'].shift(-1)
data['target'] = (data['future'] > data['Close']).astype(int)
data.dropna(inplace=True)

# Step 5: Features and labels
X = data[['Open', 'High', 'Low', 'Close', 'rsi', 'ema']]
y = data['target']

# Step 6: Train model (skip last 50 rows)
model = RandomForestClassifier()
model.fit(X[:-50], y[:-50])

# Step 7: Predict next candle
pred = model.predict([X.iloc[-1]])

# Step 8: Display results
st.subheader("Latest Candle:")
st.dataframe(data[['Open', 'High', 'Low', 'Close']].tail(1))

if pred[0] == 1:
    st.success("🔼 Signal: Call (UP)")
else:
    st.error("🔽 Signal: Put (DOWN)")
