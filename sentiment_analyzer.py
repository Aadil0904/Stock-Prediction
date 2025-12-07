from newsapi import NewsApiClient
from textblob import TextBlob
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SentimentAnalyzer:
    """Analyze stock sentiment from news articles"""
    
    def __init__(self, api_key=None):
        # SECURE FIX: Fetch key from environment variable if not provided
        self.api_key = api_key or os.environ.get('NEWS_API_KEY')
        self.newsapi = None
        
        if self.api_key:
            try:
                self.newsapi = NewsApiClient(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Could not initialize NewsAPI: {e}")
        else:
            print("Warning: No NEWS_API_KEY found. Sentiment analysis will be disabled.")
    
    def analyze_text_sentiment(self, text):
        if not text: return 0.0
        try:
            return TextBlob(text).sentiment.polarity
        except:
            return 0.0
    
    def get_stock_news(self, ticker, days=7):
        if not self.newsapi: return []
        
        try:
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            queries = [ticker]
            # Add company mapping logic here if needed
            
            all_articles = []
            for query in queries:
                try:
                    response = self.newsapi.get_everything(
                        q=query,
                        from_param=from_date.strftime('%Y-%m-%d'),
                        to=to_date.strftime('%Y-%m-%d'),
                        language='en',
                        sort_by='relevancy',
                        page_size=15
                    )
                    if response and 'articles' in response:
                        all_articles.extend(response['articles'])
                except Exception:
                    continue
            
            # Deduplicate
            seen = set()
            unique = []
            for art in all_articles:
                if art['title'] not in seen:
                    seen.add(art['title'])
                    unique.append(art)
            return unique[:15]
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def analyze_stock_sentiment(self, ticker, days=7):
        articles = self.get_stock_news(ticker, days)
        
        if not articles:
            return {
                'overall_sentiment': 0.0,
                'sentiment_label': 'Neutral',
                'num_articles': 0,
                'articles': [],
                'daily_sentiment': [],
                'error': 'No news found or API key missing.'
            }
        
        sentiments = []
        processed = []
        
        for art in articles:
            text = f"{art.get('title', '')} {art.get('description', '')}"
            score = self.analyze_text_sentiment(text)
            sentiments.append(score)
            
            processed.append({
                'title': art.get('title', 'No title'),
                'url': art.get('url', '#'),
                'source': art.get('source', {}).get('name', 'Unknown'),
                'sentiment': round(score, 2),
                'published_at': art.get('publishedAt', '')
            })
            
        avg_score = sum(sentiments) / len(sentiments) if sentiments else 0
        
        if avg_score > 0.05: label = 'Positive'
        elif avg_score < -0.05: label = 'Negative'
        else: label = 'Neutral'
        
        return {
            'overall_sentiment': round(avg_score, 3),
            'sentiment_label': label,
            'num_articles': len(articles),
            'articles': processed[:5]
        }

def get_stock_sentiment(ticker, days=7, api_key=None):
    analyzer = SentimentAnalyzer(api_key)
    return analyzer.analyze_stock_sentiment(ticker, days)