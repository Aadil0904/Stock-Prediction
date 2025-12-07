from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import numpy as np
import pandas as pd
import os

# Import everything from our hybrid agents file
from agents import (
    MarketDataAgent, TechnicalAnalystAgent, PredictionAgent, 
    SentimentAgent, PortfolioManagerAgent, stock_tools
)

# AI Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent, AgentType

load_dotenv()
app = Flask(__name__, static_folder='static', template_folder='static')
CORS(app)

# --- 1. SETUP AGENTIC AI ---
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
    google_api_key=os.environ.get("GEMINI_API_KEY"),
    temperature=0
)

agent_executor = initialize_agent(
    tools=stock_tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
    verbose=True,
    handle_parsing_errors=True
)

# --- 2. SETUP LEGACY AGENTS (For Dashboard) ---
market_agent = MarketDataAgent()
tech_agent = TechnicalAnalystAgent()
pred_agent = PredictionAgent()
news_agent = SentimentAgent()
portfolio_agent = PortfolioManagerAgent()

@app.route('/')
def index():
    return render_template('index.html')

# ==========================================
# NEW ENDPOINT: AGENT CHAT
# ==========================================
@app.route('/api/agent/chat', methods=['POST'])
def agent_chat():
    data = request.json
    try:
        response = agent_executor.invoke(data.get('query'))
        return jsonify({'answer': response['output']})
    except Exception as e:
        return jsonify({'error': str(e)})

# ==========================================
# RESTORED ENDPOINTS: DASHBOARD SUPPORT
# ==========================================

@app.route('/api/stock/<ticker>')
def get_stock_data(ticker):
    interval = request.args.get('interval', '1d')
    period = request.args.get('period', '1y')
    
    df = market_agent.get_data(ticker, interval, period)
    if df.empty: return jsonify({'error': 'No data found'}), 404
    
    # Calculate MACD for the chart
    df, _, _ = tech_agent.analyze(df)
    
    # Helpers for JSON serialization
    def to_list(col): return df[col].values.flatten().tolist() if col in df else []
    
    return jsonify({
        'dates': df.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'close': to_list('Close'),
        'open': to_list('Open'),
        'high': to_list('High'),
        'low': to_list('Low'),
        'macd': np.nan_to_num(to_list('MACD')).tolist(),
        'signal_line': np.nan_to_num(to_list('signal_line')).tolist()
    })

@app.route('/api/signals/<ticker>')
def get_signals(ticker):
    df = market_agent.get_data(ticker)
    if df.empty: return jsonify({'error': 'No data'}), 404
    
    _, buy_ix, sell_ix = tech_agent.analyze(df)
    open_prices = df['Open'].values
    
    return jsonify({
        'buy_signals': [{'date': df.index[i].strftime('%Y-%m-%d'), 'price': float(open_prices[i])} for i in buy_ix],
        'sell_signals': [{'date': df.index[i].strftime('%Y-%m-%d'), 'price': float(open_prices[i])} for i in sell_ix]
    })

@app.route('/api/backtest/<ticker>')
def backtest(ticker):
    df = market_agent.get_data(ticker)
    if df.empty: return jsonify({'error': 'No data'}), 404
    
    _, buy_ix, sell_ix = tech_agent.analyze(df)
    metrics = portfolio_agent.backtest(df, buy_ix, sell_ix)
    return jsonify(metrics)

@app.route('/api/predict/<ticker>')
def predict_price(ticker):
    df = market_agent.get_data(ticker)
    result = pred_agent.predict(df, ticker)
    
    # Add dummy dates for the chart if prediction succeeded
    if 'predictions' in result and not 'error' in result:
        last_date = df.index[-1]
        future_dates = pd.date_range(start=last_date, periods=8, freq='D')[1:]
        result['prediction_dates'] = future_dates.strftime('%Y-%m-%d').tolist()
        
    return jsonify(result)

@app.route('/api/sentiment/<ticker>')
def get_sentiment(ticker):
    return jsonify(news_agent.analyze(ticker))

if __name__ == '__main__':
    app.run(debug=True, port=5001)