import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import time
import os
from lstm_model import predict_stock_price
from sentiment_analyzer import get_stock_sentiment

# --- BASE AGENT ---
class Agent:
    def __init__(self, name):
        self.name = name

    def log(self, message):
        print(f"[{self.name}] {message}")

# --- 1. MARKET DATA AGENT ---
class MarketDataAgent(Agent):
    """Fetches and manages stock data with caching."""
    def __init__(self):
        super().__init__("MarketDataAgent")
        self.cache = {}
        self.cache_duration = 300  # 5 minutes

    def get_data(self, ticker, interval='1d', period='max'):
        cache_key = f"{ticker}_{interval}_{period}"
        now = time.time()

        # Check Cache
        if cache_key in self.cache:
            if now - self.cache[cache_key]['timestamp'] < self.cache_duration:
                self.log(f"Returning cached data for {ticker}")
                return self.cache[cache_key]['data']

        self.log(f"Fetching fresh data for {ticker}...")
        try:
            df = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=True)
            
            # Clean Data (Flatten MultiIndex & Numeric Conversion)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df.dropna(inplace=True)

            if not df.empty:
                self.cache[cache_key] = {'data': df, 'timestamp': now}
            
            return df
        except Exception as e:
            self.log(f"Error: {e}")
            return pd.DataFrame()

# --- 2. TECHNICAL ANALYST AGENT ---
class TechnicalAnalystAgent(Agent):
    """Calculates indicators and generates signals."""
    def __init__(self):
        super().__init__("TechnicalAnalystAgent")

    def analyze(self, df):
        self.log("Calculating MACD and generating signals...")
        df = df.copy()
        
        # Calculate MACD
        close = df['Close'] if isinstance(df['Close'], pd.Series) else df['Close'].iloc[:, 0]
        df['EMA_12'] = close.ewm(span=12, adjust=False).mean()
        df['EMA_26'] = close.ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['signal_line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # Generate Signals
        macd = df['MACD'].values.flatten()
        signal = df['signal_line'].values.flatten()
        long_signals, short_signals = [], []

        for i in range(2, len(df)):
            if macd[i] > signal[i] and macd[i-1] < signal[i-1]:
                long_signals.append(i)
            elif macd[i] < signal[i] and macd[i-1] > signal[i-1]:
                short_signals.append(i)
        
        # Execution on NEXT candle
        buy_indices = [i+1 for i in long_signals if i+1 < len(df)]
        sell_indices = [i+1 for i in short_signals if i+1 < len(df)]

        return df, buy_indices, sell_indices

# --- 3. PREDICTION AGENT ---
class PredictionAgent(Agent):
    """Runs AI models to forecast prices."""
    def __init__(self):
        super().__init__("PredictionAgent")

    def predict(self, df, ticker):
        self.log(f"Running LSTM model for {ticker}...")
        if len(df) < 100:
            return {'error': 'Insufficient data'}
        
        try:
            return predict_stock_price(df, lookback=60, prediction_days=7, epochs=5)
        except Exception as e:
            self.log(f"Prediction failed: {e}")
            return {'error': str(e)}

# --- 4. SENTIMENT AGENT ---
class SentimentAgent(Agent):
    """Analyzes news sentiment."""
    def __init__(self):
        super().__init__("SentimentAgent")

    def analyze(self, ticker):
        self.log(f"Analyzing news sentiment for {ticker}...")
        return get_stock_sentiment(ticker, days=7)

# --- 5. PORTFOLIO MANAGER AGENT ---
class PortfolioManagerAgent(Agent):
    """Simulates trading and calculates risk/reward."""
    def __init__(self, initial_capital=10000.0, transaction_fee=0.001):
        super().__init__("PortfolioManager")
        self.initial_capital = initial_capital
        self.fee = transaction_fee

    def backtest(self, df, buy_indices, sell_indices):
        self.log("Running backtest simulation...")
        cash = self.initial_capital
        shares = 0
        open_prices = df['Open'].values.flatten()

        events = []
        for i in buy_indices: events.append((i, 'buy', float(open_prices[i])))
        for i in sell_indices: events.append((i, 'sell', float(open_prices[i])))
        events.sort(key=lambda x: x[0])

        for _, action, price in events:
            if action == 'buy' and cash > 0:
                shares = cash / (price * (1 + self.fee))
                cash = 0
            elif action == 'sell' and shares > 0:
                cash = shares * price * (1 - self.fee)
                shares = 0
        
        final_value = cash if cash > 0 else (shares * float(open_prices[-1]))
        total_profit = final_value - self.initial_capital
        roi = (total_profit / self.initial_capital) * 100
        
        # Calculate Win Rate
        wins = 0
        trades = min(len(buy_indices), len(sell_indices))
        if trades > 0:
            for i in range(trades):
                if open_prices[sell_indices[i]] > open_prices[buy_indices[i]]:
                    wins += 1
        
        win_rate = (wins / trades * 100) if trades > 0 else 0

        return {
            'total_profit': round(total_profit, 2),
            'roi': round(roi, 2),
            'final_value': round(final_value, 2),
            'num_trades': len(events),
            'win_rate': round(win_rate, 2)
        }