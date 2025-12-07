import os
import json
import google.generativeai as genai
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SentimentAnalyzer:
    """Analyze stock sentiment using Google Gemini"""
    
    def __init__(self):
        # 1. Setup NewsAPI
        self.news_api_key = os.environ.get('NEWS_API_KEY')
        self.newsapi = None
        if self.news_api_key:
            self.newsapi = NewsApiClient(api_key=self.news_api_key)
            
        # 2. Setup Google Gemini
        self.gemini_key = os.environ.get('GEMINI_API_KEY')
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash') # Or 'gemini-pro'
        else:
            print("⚠️ Warning: GEMINI_API_KEY not found. Sentiment analysis will fail.")

    def get_stock_news(self, ticker, days=7):
        """Fetches news from NewsAPI"""
        if not self.newsapi: return []
        
        try:
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            # Fetch news
            response = self.newsapi.get_everything(
                q=ticker,
                from_param=from_date.strftime('%Y-%m-%d'),
                to=to_date.strftime('%Y-%m-%d'),
                language='en',
                sort_by='relevancy',
                page_size=15
            )
            
            if not response or 'articles' not in response:
                return []

            # Deduplicate articles
            seen = set()
            unique_articles = []
            for art in response['articles']:
                if art['title'] and art['title'] not in seen:
                    seen.add(art['title'])
                    unique_articles.append(art)
            
            return unique_articles[:10] # Limit to top 10 for the LLM
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def analyze_stock_sentiment(self, ticker, days=7):
        """Uses Gemini to analyze the news list"""
        
        # 1. Get News
        articles = self.get_stock_news(ticker, days)
        if not articles:
            return {
                'overall_sentiment': 0.0,
                'sentiment_label': 'Neutral',
                'num_articles': 0,
                'articles': [],
                'reasoning': "No news found."
            }

        if not self.model:
            return {'error': 'Gemini API key missing'}

        # 2. Prepare Prompt for Gemini
        headlines_text = "\n".join([f"- {a['title']} (Source: {a['source']['name']})" for a in articles])
        
        prompt = f"""
        You are a financial analyst agent. Analyze the following news headlines for the stock '{ticker}':

        {headlines_text}

        Your task:
        1. Determine the overall market sentiment score between -1 (Very Negative) and 1 (Very Positive).
        2. Provide a 1-sentence reasoning summary.
        3. Assign a sentiment label (Bullish, Bearish, or Neutral).

        Return ONLY valid JSON in this format:
        {{
            "score": 0.0,
            "label": "Neutral",
            "reasoning": "Summary here..."
        }}
        """

        try:
            # 3. Call Gemini
            response = self.model.generate_content(prompt)
            
            # 4. Clean and Parse JSON
            # Gemini might add markdown ```json ... ``` wrappers
            text_response = response.text.strip()
            if text_response.startswith("```"):
                text_response = text_response.replace("```json", "").replace("```", "")
            
            result = json.loads(text_response)
            
            # 5. Format for Frontend
            # We map the raw articles back so the frontend can display links
            formatted_articles = [{
                'title': a['title'],
                'url': a['url'],
                'source': a['source']['name'],
                'sentiment': 0 # We don't score individual articles to save tokens, just the aggregate
            } for a in articles]

            return {
                'overall_sentiment': float(result.get('score', 0)),
                'sentiment_label': result.get('label', 'Neutral'),
                'num_articles': len(articles),
                'articles': formatted_articles,
                'reasoning': result.get('reasoning', '') # New field!
            }

        except Exception as e:
            print(f"Gemini Error: {e}")
            return {
                'overall_sentiment': 0.0,
                'sentiment_label': 'Error',
                'num_articles': len(articles),
                'articles': [],
                'error': str(e)
            }

# Helper function used by app.py
def get_stock_sentiment(ticker, days=7):
    analyzer = SentimentAnalyzer()
    return analyzer.analyze_stock_sentiment(ticker, days)