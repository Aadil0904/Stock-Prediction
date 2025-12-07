Here is a comprehensive and updated `README.md` for your project. It includes the new installation steps (especially for Apple Silicon), the security fixes (using `.env`), and details about the Machine Learning features.

You can save this as **`README.md`** in your project folder.

---

# 📈 MACD & LSTM Stock Predictor

A full-stack web application for stock market analysis. It combines technical indicators (**MACD**), deep learning price forecasting (**LSTM**), and news sentiment analysis (**NLP**) into a modern, interactive dashboard.

## 🚀 Features

- **Real-Time Data:** Fetches live stock data using Yahoo Finance (with smart caching to prevent rate limits).
- **Technical Analysis:** Automatic calculation of MACD, Signal Line, and EMA crossovers to generate Buy/Sell signals.
- **🤖 AI Price Prediction:** Uses a **Long Short-Term Memory (LSTM)** Neural Network to forecast stock prices 7 days into the future.
- **📰 Sentiment Analysis:** Analyzes recent news headlines using Natural Language Processing (FinBERT/TextBlob) to gauge market sentiment.
- **Backtesting Engine:** Simulates trading based on generated signals to calculate potential Win Rate and ROI.
- **Interactive UI:** Responsive Dark Mode dashboard built with vanilla JS and Chart.js.

---

## 🛠️ Tech Stack

- **Backend:** Python (Flask)
- **Data Processing:** Pandas, NumPy
- **Machine Learning:** TensorFlow / Keras (LSTM), Scikit-Learn
- **NLP:** NewsAPI, TextBlob
- **Frontend:** HTML5, CSS3 (Glassmorphism), JavaScript
- **Visualization:** Chart.js

---

## ⚙️ Installation Guide

### Prerequisites

- **Python 3.10** or **3.11** (Recommended for TensorFlow compatibility)
- **Git**

### Option A: For Apple Silicon (M1/M2/M3 Macs) - _Recommended_

Due to hardware acceleration requirements, use `conda` (Miniforge) to install optimized libraries.

1.  **Install Miniforge** from [conda-forge](https://github.com/conda-forge/miniforge).
2.  **Create and activate an environment:**
    ```bash
    conda create -n stock-env python=3.10
    conda activate stock-env
    ```
3.  **Install Apple-Optimized Dependencies:**
    ```bash
    pip install tensorflow-macos tensorflow-metal
    pip install -r requirements.txt
    ```

### Option B: Windows / Linux / Intel Macs

Standard installation using `pip`.

1.  **Create a virtual environment:**

    ```bash
    python -m venv venv

    # Windows
    venv\Scripts\activate

    # Mac/Linux
    source venv/bin/activate
    ```

2.  **Install Dependencies:**
    ```bash
    pip install tensorflow  # Standard CPU/GPU version
    pip install -r requirements.txt
    ```

---

## 🔑 Configuration

**Security Note:** This project uses environment variables to keep your API keys safe. Never commit your `.env` file.

1.  Get a free API Key from [NewsAPI.org](https://newsapi.org/).
2.  Create a file named `.env` in the root directory.
3.  Add your key:
    ```env
    NEWS_API_KEY=your_actual_api_key_here
    ```

---

## 🏃‍♂️ Running the Application

1.  Ensure your environment is active (`conda activate stock-env` or `source venv/bin/activate`).
2.  Start the Flask server:
    ```bash
    python app.py
    ```
3.  Open your browser and navigate to:
    ```
    http://localhost:5000
    ```

---

## 📡 API Endpoints

| Endpoint                  | Method | Description                                                        |
| :------------------------ | :----- | :----------------------------------------------------------------- |
| `/api/stock/<ticker>`     | GET    | Returns OHLCV data and calculated MACD/Signal lines.               |
| `/api/signals/<ticker>`   | GET    | Returns specific dates for Buy/Sell signals based on crossovers.   |
| `/api/predict/<ticker>`   | GET    | Triggers LSTM training and returns 7-day price forecasts.          |
| `/api/sentiment/<ticker>` | GET    | Returns news articles and an aggregated sentiment score (-1 to 1). |
| `/api/backtest/<ticker>`  | GET    | Returns profit/loss metrics based on the strategy.                 |

---

## 📂 Project Structure

```text
macd-stock-predictor/
├── app.py                 # Main Flask application & API routes
├── lstm_model.py          # Machine Learning model definition & training
├── sentiment_analyzer.py  # News fetching & NLP logic
├── requirements.txt       # Python dependencies
├── .env                   # API Keys (NOT committed to git)
├── static/
│   ├── index.html         # Frontend Dashboard
│   ├── css/
│   │   └── style.css      # Dark theme styling
│   └── js/
│       └── main.js        # Client-side logic & Chart rendering
└── README.md              # Project Documentation
```

---

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**. It is not financial advice.

- Stock predictions are based on historical patterns and cannot guarantee future results.
- Sentiment analysis is automated and may misinterpret complex financial news.
- Always do your own research before investing.

## 📄 License

MIT License - feel free to use and modify this project for your portfolio\!
