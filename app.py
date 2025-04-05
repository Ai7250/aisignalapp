import streamlit as st
import yfinance as yf
import pandas as pd
import ta
from sklearn.ensemble import RandomForestClassifier

st.title("📈 AI Price Action Signal (Demo)")

# Step 1: Download data
data = yf.download("BTC-USD", interval="1m", period="1d")

# Step 2: Drop NaNs early
data.dropna(inplace=True)

# Step 3: Indicators (use only Series, not DataFrames)
close_prices = data['Close']

# RSI & EMA calculation
rsi_series = ta.momentum.RSIIndicator(close=close_prices).rsi()
ema_series = ta.trend.EMAIndicator(close=close_prices, window=10).ema_indicator()

# Add to dataframe
data['rsi'] = rsi_series
data['ema'] = ema_series

# Step 4: Create target column
data['future'] = data['Close'].shift(-1)
data['target'] = (data['future'] > data['Close']).astype(int)

# Step 5: Clean again
data.dropna(inplace=True)

# Step 6: Features & Labels
features = ['Open', 'High', 'Low', 'Close', 'rsi', 'ema']
X = data[features]
y = data['target']

# Step 7: Train model (avoid last 50 rows for testing)
model = RandomForestClassifier()
model.fit(X[:-50], y[:-50])

# Step 8: Prediction
last_row = X.iloc[-1].values.reshape(1, -1)  # Proper shape (1,6)
pred = model.predict(last_row)

# Step 9: Display Output
st.subheader("📊 Latest Candle:")
st.dataframe(data[['Open', 'High', 'Low', 'Close']].tail(1))

if pred[0] == 1:
    st.success("🔼 Signal: Call (UP)")
else:
    st.error("🔽 Signal: Put (DOWN)")
