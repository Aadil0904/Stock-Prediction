import pandas as pd
import numpy as np
import yfinance as yf
import time
from langchain.tools import tool
from lstm_model import predict_stock_price
from sentiment_analyzer import get_stock_sentiment

# ==========================================
# PART 1: ORIGINAL AGENT CLASSES (With Debugging)
# ==========================================

class Agent:
    def __init__(self, name):
        self.name = name
    def log(self, message):
        print(f"[{self.name}] {message}")

class MarketDataAgent(Agent):
    def __init__(self):
        super().__init__("MarketDataAgent")
        self.cache = {}
        self.cache_duration = 300

    def get_data(self, ticker, interval='1d', period='1y'):
        cache_key = f"{ticker}_{interval}_{period}"
        if cache_key in self.cache:
            if time.time() - self.cache[cache_key]['timestamp'] < self.cache_duration:
                return self.cache[cache_key]['data']
        
        try:
            # self.log(f"Fetching data for {ticker}...")
            df = yf.download(ticker, interval=interval, period=period, progress=False)
            
            # Handle MultiIndex columns (common in new yfinance)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            for c in cols:
                if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
            
            df.dropna(inplace=True)
            
            if not df.empty:
                self.cache[cache_key] = {'data': df, 'timestamp': time.time()}
            return df
        except Exception as e:
            self.log(f"Error fetching data: {e}")
            return pd.DataFrame()

class TechnicalAnalystAgent(Agent):
    def __init__(self):
        super().__init__("TechnicalAnalystAgent")

    def analyze(self, df):
        df = df.copy()
        # Calculate MACD
        close = df['Close']
        df['EMA_12'] = close.ewm(span=12, adjust=False).mean()
        df['EMA_26'] = close.ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['signal_line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        macd = df['MACD'].values
        signal = df['signal_line'].values
        buy_indices = []
        sell_indices = []

        # Find Crossovers
        for i in range(1, len(df)):
            if macd[i] > signal[i] and macd[i-1] <= signal[i-1]:
                buy_indices.append(i)
            elif macd[i] < signal[i] and macd[i-1] >= signal[i-1]:
                sell_indices.append(i)
        
        self.log(f"Found {len(buy_indices)} Buy signals and {len(sell_indices)} Sell signals")
        return df, buy_indices, sell_indices

class PredictionAgent(Agent):
    def __init__(self):
        super().__init__("PredictionAgent")
    def predict(self, df, ticker):
        if len(df) < 50: return {'error': 'Insufficient data'}
        return predict_stock_price(df)

class SentimentAgent(Agent):
    def __init__(self):
        super().__init__("SentimentAgent")
    def analyze(self, ticker):
        return get_stock_sentiment(ticker)

class PortfolioManagerAgent(Agent):
    def __init__(self, initial_capital=10000.0):
        super().__init__("PortfolioManager")
        self.capital = initial_capital

    def backtest(self, df, buy_idx, sell_idx):
        cash = self.capital
        shares = 0
        opens = df['Open'].values
        
        # Combine buy/sell events and sort by time
        events = [(i, 'buy') for i in buy_idx] + [(i, 'sell') for i in sell_idx]
        events.sort()

        wins = 0
        closed_trades = 0
        last_buy_price = 0
        
        self.log(f"Starting backtest with ${self.capital} and {len(events)} events.")

        for i, action in events:
            price = float(opens[i])
            if action == 'buy' and cash > price:
                shares = cash / price
                cash = 0
                last_buy_price = price
            elif action == 'sell' and shares > 0:
                cash = shares * price
                shares = 0
                closed_trades += 1
                if price > last_buy_price:
                    wins += 1
        
        # Calculate final portfolio value
        final_val = cash + (shares * float(opens[-1])) if shares > 0 else cash
        profit = final_val - self.capital
        roi = (profit / self.capital) * 100 if self.capital > 0 else 0
        win_rate = (wins / closed_trades * 100) if closed_trades > 0 else 0

        self.log(f"Backtest Result: Profit=${profit:.2f}, ROI={roi:.2f}%")

        return {
            'total_profit': round(profit, 2),
            'roi': round(roi, 2),
            'final_value': round(final_val, 2),
            'win_rate': round(win_rate, 2),
            'num_trades': len(events)
        }

# ==========================================
# PART 2: AGENTIC TOOLS (For Chat)
# ==========================================
market_agent = MarketDataAgent()
tech_agent = TechnicalAnalystAgent()
pred_agent = PredictionAgent()
sent_agent = SentimentAgent()

@tool
def fetch_stock_price(ticker: str):
    """Fetches the latest stock price."""
    df = market_agent.get_data(ticker)
    if df.empty: return "No data found."
    return f"Latest Close for {ticker}: {df.iloc[-1]['Close']:.2f}"

@tool
def analyze_technicals(ticker: str):
    """Checks MACD technical signals."""
    df = market_agent.get_data(ticker)
    if df.empty: return "No data."
    _, buys, sells = tech_agent.analyze(df)
    
    last_signal = "NEUTRAL"
    if buys and sells:
        last_signal = "BUY" if buys[-1] > sells[-1] else "SELL"
    elif buys:
        last_signal = "BUY"
    elif sells:
        last_signal = "SELL"
        
    return f"Technical signal is {last_signal}."

@tool
def get_market_sentiment(ticker: str):
    """Gets news sentiment score."""
    res = sent_agent.analyze(ticker)
    return f"Sentiment: {res.get('sentiment_label', 'Unknown')} (Score: {res.get('overall_sentiment', 0)})."

@tool
def predict_future_price(ticker: str):
    """Predicts next day price."""
    df = market_agent.get_data(ticker)
    res = pred_agent.predict(df, ticker)
    
    # Safely extract the prediction number
    if 'predictions' in res and len(res['predictions']) > 0:
        price = res['predictions'][0]
        # Handle case where prediction might be a list inside a list
        if isinstance(price, list) or isinstance(price, np.ndarray):
            price = price[0]
        return f"Predicted price: {float(price):.2f}"
        
    return "Prediction failed."

stock_tools = [fetch_stock_price, analyze_technicals, get_market_sentiment, predict_future_price]