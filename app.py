from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

# --- ML IMPORTS ---
try:
    from lstm_model import predict_stock_price
    ML_AVAILABLE = True
    print("✅ Machine Learning modules loaded successfully.")
except ImportError as e:
    ML_AVAILABLE = False
    print(f"⚠️  ML modules not found: {e}. Prediction feature will be disabled.")

from sentiment_analyzer import get_stock_sentiment

app = Flask(__name__, static_folder='static', template_folder='static')
CORS(app)

# --- IN-MEMORY CACHE ---
data_cache = {}
CACHE_DURATION = 300  # 5 minutes

def get_cached_data(ticker, interval, period):
    """Fetches data from Yahoo Finance or Cache to prevent rate limits."""
    # Create a unique key for the cache
    cache_key = f"{ticker}_{interval}_{period}"
    now = time.time()
    
    # Check cache validity
    if cache_key in data_cache:
        entry = data_cache[cache_key]
        if now - entry['timestamp'] < CACHE_DURATION:
            return entry['data']
    
    try:
        # Download data
        df = yf.download(ticker, interval=interval, period=period, progress=False, auto_adjust=True)
        
        # --- CRITICAL FIXES FOR DATA FORMAT ---
        
        # 1. Flatten MultiIndex columns (Fixes 'DataFrame has no attribute tolist')
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # 2. Ensure data is numeric (Fixes 'str - str' error)
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 3. Drop any rows with missing data (NaNs) created by conversion
        df.dropna(inplace=True)

        if not df.empty:
            data_cache[cache_key] = {'data': df, 'timestamp': now}
            
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

def calculate_macd(df):
    df = df.copy()
    # Ensure 'Close' is a Series (single list of numbers)
    if isinstance(df['Close'], pd.DataFrame):
        close_prices = df['Close'].iloc[:, 0]
    else:
        close_prices = df['Close']

    df['EMA_12'] = close_prices.ewm(span=12, adjust=False).mean()
    df['EMA_26'] = close_prices.ewm(span=26, adjust=False).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['signal_line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df

def generate_signals(df):
    long, short = [], []
    
    # Ensure columns are 1D arrays for comparison
    macd = df['MACD'].values.flatten()
    signal = df['signal_line'].values.flatten()
    
    for i in range(2, len(df)):
        if macd[i] > signal[i] and macd[i-1] < signal[i-1]:
            long.append(i)
        elif macd[i] < signal[i] and macd[i-1] > signal[i-1]:
            short.append(i)
    
    real_long = [i+1 for i in long if i+1 < len(df)]
    real_short = [i+1 for i in short if i+1 < len(df)]
    return real_long, real_short

def calculate_profits(df, buy_indices, sell_indices):
    if not buy_indices or not sell_indices:
        return {'total_profit': 0, 'avg_profit_pct': 0, 'num_trades': 0, 'win_rate': 0}
    
    # Safely extract Open prices as 1D float arrays
    open_prices = df['Open'].values.flatten()
    
    try:
        buy_prices = [float(open_prices[i]) for i in buy_indices]
        sell_prices = [float(open_prices[i]) for i in sell_indices]
    except (IndexError, ValueError) as e:
        print(f"Error extracting prices: {e}")
        return {'total_profit': 0, 'avg_profit_pct': 0, 'num_trades': 0, 'win_rate': 0}
    
    if not buy_prices or not sell_prices:
        return {'total_profit': 0, 'avg_profit_pct': 0, 'num_trades': 0, 'win_rate': 0}

    # Align trades
    if sell_prices and buy_prices and (sell_indices[0] < buy_indices[0]):
        sell_prices = sell_prices[1:]
    
    min_len = min(len(buy_prices), len(sell_prices))
    buy_prices = buy_prices[:min_len]
    sell_prices = sell_prices[:min_len]
    
    profits = [(s - b) for s, b in zip(sell_prices, buy_prices)]
    rel_profits = [(p / b * 100) for p, b in zip(profits, buy_prices) if b != 0]
    
    winning = sum(1 for p in profits if p > 0)
    
    return {
        'total_profit': float(sum(profits)),
        'avg_profit_pct': float(np.mean(rel_profits)) if rel_profits else 0,
        'num_trades': len(profits),
        'win_rate': (winning / len(profits) * 100) if profits else 0
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<ticker>')
def get_stock_data(ticker):
    interval = request.args.get('interval', '1d')
    period = request.args.get('period', '1y')
    df = get_cached_data(ticker, interval, period)
    
    if df.empty: 
        return jsonify({'error': 'No data found'}), 404
    
    df = calculate_macd(df)
    
    # Helper to convert series to list safely
    def to_list(col_name):
        # Flatten ensures we get a simple list even if DataFrame structure is weird
        return df[col_name].values.flatten().tolist()

    return jsonify({
        'dates': df.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'close': to_list('Close'),
        'macd': np.nan_to_num(to_list('MACD')).tolist(),
        'signal_line': np.nan_to_num(to_list('signal_line')).tolist(),
        'open': to_list('Open'),
        'high': to_list('High'),
        'low': to_list('Low')
    })

@app.route('/api/signals/<ticker>')
def get_signals(ticker):
    interval = request.args.get('interval', '1d')
    period = request.args.get('period', '1y')
    df = get_cached_data(ticker, interval, period)
    
    if df.empty: return jsonify({'error': 'No data found'}), 404
    
    df = calculate_macd(df)
    buy_ix, sell_ix = generate_signals(df)
    
    # Safe data extraction
    open_prices = df['Open'].values.flatten()
    
    buy_signals = [{'date': df.index[i].strftime('%Y-%m-%d %H:%M:%S'), 'price': float(open_prices[i])} for i in buy_ix]
    sell_signals = [{'date': df.index[i].strftime('%Y-%m-%d %H:%M:%S'), 'price': float(open_prices[i])} for i in sell_ix]
    
    return jsonify({'buy_signals': buy_signals, 'sell_signals': sell_signals})

@app.route('/api/backtest/<ticker>')
def backtest(ticker):
    interval = request.args.get('interval', '1d')
    period = request.args.get('period', '1y')
    df = get_cached_data(ticker, interval, period)
    
    if df.empty: return jsonify({'error': 'No data found'}), 404
    
    df = calculate_macd(df)
    buy_ix, sell_ix = generate_signals(df)
    metrics = calculate_profits(df, buy_ix, sell_ix)
    return jsonify(metrics)

@app.route('/api/predict/<ticker>')
def predict_price(ticker):
    if not ML_AVAILABLE:
        return jsonify({'error': 'ML libraries not installed.'}), 500

    # FIX: Use 'max' to ensure we get enough data for the model
    # instead of hardcoding '2y' which might fail for some stocks.
    interval = '1d'
    period = 'max' 
    
    df = get_cached_data(ticker, interval, period)
    
    # We need at least 100 data points to train the LSTM
    if df.empty or len(df) < 100: 
        return jsonify({'error': f'Not enough historical data for {ticker} (found {len(df)} days, need 100+)'}), 404
    
    try:
        print(f"🤖 Training LSTM for {ticker} with {len(df)} days of data...")
        
        # Use a slightly larger lookback if we have plenty of data
        lookback_days = 60
        
        result = predict_stock_price(df, lookback=lookback_days, prediction_days=7, epochs=5)
        
        if 'error' not in result:
            last_date = df.index[-1]
            future_dates = pd.date_range(start=last_date, periods=8, freq='D')[1:]
            result['prediction_dates'] = future_dates.strftime('%Y-%m-%d').tolist()
            
        return jsonify(result)
    except Exception as e:
        print(f"LSTM Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment/<ticker>')
def get_sentiment(ticker):
    days = int(request.args.get('days', 7))
    result = get_stock_sentiment(ticker, days=days)
    return jsonify(result)

if __name__ == '__main__':
    print("="*50)
    print("🚀 MACD & LSTM Stock Server Running")
    if ML_AVAILABLE:
        print("✅ TensorFlow/ML: ENABLED (Apple Silicon Optimized)")
    else:
        print("❌ TensorFlow/ML: DISABLED")
    print("="*50)
    app.run(debug=True, port=5000)