import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from sklearn.ensemble import RandomForestClassifier

st.title("📈 AI Price Action Signal (Demo)")

# Step 1: Download BTC 1-min data (last 1 day)
data = yf.download("BTC-USD", interval="1m", period="1d")

# Step 2: Drop rows with NaN
data.dropna(inplace=True)

# Step 3: Close as 1D float series
close_prices = data['Close'].astype(float)

# Step 4: Calculate RSI & EMA
rsi = RSIIndicator(close=close_prices).rsi()
ema = EMAIndicator(close=close_prices, window=10).ema_indicator()

# Step 5: Add indicators to data
data['rsi'] = rsi
data['ema'] = ema

# Step 6: Target creation
data['future'] = data['Close'].shift(-1)
data['target'] = (data['future'] > data['Close']).astype(int)

# Step 7: Drop any new NaNs
data.dropna(inplace=True)

# Step 8: Define features and labels
features = ['Open', 'High', 'Low', 'Close', 'rsi', 'ema']
X = data[features]
y = data['target']

# Step 9: Train-test split
model = RandomForestClassifier()
model.fit(X[:-50], y[:-50])

# Step 10: Predict last signal
last_row = X.iloc[-1].values.reshape(1, -1)
pred = model.predict(last_row)

# Step 11: Display
st.subheader("📊 Latest Candle")
st.dataframe(data[['Open', 'High', 'Low', 'Close']].tail(1))

if pred[0] == 1:
    st.success("🔼 Signal: Call (UP)")
else:
    st.error("🔽 Signal: Put (DOWN)")
