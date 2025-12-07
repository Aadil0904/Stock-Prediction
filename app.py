from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Import our new Agents
from agents import (
    MarketDataAgent, 
    TechnicalAnalystAgent, 
    PredictionAgent, 
    SentimentAgent, 
    PortfolioManagerAgent
)

load_dotenv()
app = Flask(__name__, static_folder='static', template_folder='static')
CORS(app)

# --- INITIALIZE AGENTS ---
market_agent = MarketDataAgent()
tech_agent = TechnicalAnalystAgent()
ai_agent = PredictionAgent()
news_agent = SentimentAgent()
portfolio_agent = PortfolioManagerAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock/<ticker>')
def get_stock_data(ticker):
    interval = request.args.get('interval', '1d')
    period = request.args.get('period', '1y')
    
    # Agent 1: Get Data
    df = market_agent.get_data(ticker, interval, period)
    if df.empty: return jsonify({'error': 'No data found'}), 404
    
    # Agent 2: Analyze Data
    df, _, _ = tech_agent.analyze(df)
    
    # Helper to convert to list
    def to_list(col): return df[col].values.flatten().tolist()

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
    
    df = market_agent.get_data(ticker, interval, period)
    if df.empty: return jsonify({'error': 'No data found'}), 404
    
    # Agent 2: Technical Analysis
    _, buy_ix, sell_ix = tech_agent.analyze(df)
    
    open_prices = df['Open'].values.flatten()
    buy_signals = [{'date': df.index[i].strftime('%Y-%m-%d %H:%M:%S'), 'price': float(open_prices[i])} for i in buy_ix]
    sell_signals = [{'date': df.index[i].strftime('%Y-%m-%d %H:%M:%S'), 'price': float(open_prices[i])} for i in sell_ix]
    
    return jsonify({'buy_signals': buy_signals, 'sell_signals': sell_signals})

@app.route('/api/backtest/<ticker>')
def backtest(ticker):
    interval = request.args.get('interval', '1d')
    period = request.args.get('period', '1y')
    
    df = market_agent.get_data(ticker, interval, period)
    if df.empty: return jsonify({'error': 'No data found'}), 404
    
    # Agent 2: Get Signals
    _, buy_ix, sell_ix = tech_agent.analyze(df)
    
    # Agent 5: Calculate Portfolio Performance
    metrics = portfolio_agent.backtest(df, buy_ix, sell_ix)
    
    return jsonify(metrics)

@app.route('/api/predict/<ticker>')
def predict_price(ticker):
    # Agent 1: Get Data (Request 'max' for training)
    df = market_agent.get_data(ticker, interval='1d', period='max')
    
    # Agent 3: Run Prediction
    result = ai_agent.predict(df, ticker)
    
    if 'error' not in result:
        last_date = df.index[-1]
        future_dates = pd.date_range(start=last_date, periods=8, freq='D')[1:]
        result['prediction_dates'] = future_dates.strftime('%Y-%m-%d').tolist()
        
    return jsonify(result)

@app.route('/api/sentiment/<ticker>')
def get_sentiment(ticker):
    # Agent 4: Analyze Sentiment
    result = news_agent.analyze(ticker)
    return jsonify(result)

if __name__ == '__main__':
    print("="*50)
    print("🤖 Agentic AI Stock System Initialized")
    print("   - MarketDataAgent: Ready")
    print("   - TechnicalAnalystAgent: Ready")
    print("   - PredictionAgent: Ready")
    print("   - SentimentAgent: Ready")
    print("   - PortfolioManagerAgent: Ready")
    print("="*50)
    app.run(debug=True, port=5001)