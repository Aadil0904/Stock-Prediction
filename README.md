# 📈 Agentic AI Stock Predictor

A sophisticated **Multi-Agent System** for stock market analysis. This application moves beyond traditional scripts by employing a team of five autonomous AI agents that collaborate to analyze data, forecast prices, read news, and simulate trading strategies.

## 🤖 The Agentic Architecture

Instead of a monolithic script, this project utilizes an **Orchestrator Pattern** where a central manager coordinates specialized agents:

1.  **🕵️‍♂️ Market Data Agent ("The Librarian")**
    - **Role:** Autonomous data acquisition.
    - **Capabilities:** Decides when to fetch fresh data vs. serving cached data to prevent API rate limits. Handles data cleaning and multi-index flattening.
2.  **📈 Technical Analyst Agent ("The Chartist")**
    - **Role:** Pattern recognition.
    - **Capabilities:** Computes technical indicators (MACD, Signal Line, EMA) and independently generates Buy/Sell signals based on crossovers.
3.  **🔮 Prediction Agent ("The Futurist")**
    - **Role:** Quantitative forecasting.
    - **Capabilities:** Manages a Deep Learning **LSTM** model. Handles training loops, data normalization, and generates 7-day price forecasts.
4.  **🧠 Sentiment Agent ("The Analyst")**
    - **Role:** Qualitative reasoning (Cognitive Agent).
    - **Capabilities:** Powered by **Google Gemini (LLM)**. It reads unstructured financial news, weighs conflicting headlines, and outputs a nuanced sentiment score with reasoning. Includes self-healing retry logic for API limits.
5.  **💼 Portfolio Manager Agent ("The Trader")**
    - **Role:** Risk and strategy execution.
    - **Capabilities:** Simulates a real-world trading account ($10k start). Calculates ROI, Portfolio Value, and Win Rate while accounting for transaction fees.

---

## 🚀 Features

- **Real-Time Data:** Smart caching with `yfinance` to ensure speed and reliability.
- **Deep Learning:** LSTM Neural Network for time-series forecasting.
- **Generative AI:** LLM-based sentiment analysis that understands financial context better than simple NLP.
- **Realistic Backtesting:** Simulation includes fees and compounding portfolio value.
- **Modern UI:** Responsive, dark-themed dashboard with interactive charts.

---

## 🛠️ Tech Stack

- **Architecture:** Multi-Agent System (Python)
- **LLM:** Google Gemini 2.0 Flash / Pro
- **Deep Learning:** TensorFlow / Keras (LSTM)
- **Backend:** Flask
- **Data:** Pandas, NumPy, YFinance
- **Frontend:** HTML5, CSS3 (Glassmorphism), JavaScript, Chart.js

---

## ⚙️ Installation Guide

### Prerequisites

- **Python 3.10** or **3.11** (Strict requirement for TensorFlow on some platforms)
- **Git**

### Option A: For Apple Silicon (M1/M2/M3 Macs) - _Recommended_

Due to hardware acceleration requirements, use `conda` (Miniforge).

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

**Security Note:** This project uses environment variables. Never commit your `.env` file.

1.  Get a free **NewsAPI Key** from [NewsAPI.org](https://newsapi.org/).
2.  Get a free **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).
3.  Create a file named `.env` in the root directory:
    ```env
    NEWS_API_KEY=your_news_api_key_here
    GEMINI_API_KEY=your_gemini_key_here
    ```

---

## 🏃‍♂️ Running the Application

1.  Ensure your environment is active.
2.  Start the Flask server:
    ```bash
    python app.py
    ```
3.  Open your browser and navigate to:
    ```
    http://localhost:5000
    ```

---

## 📂 Project Structure

```text
macd-stock-predictor/
├── agents.py              # The "Brains": Class definitions for all 5 Agents
├── app.py                 # The "Manager": Flask app orchestrating the agents
├── lstm_model.py          # Deep Learning model logic (used by PredictionAgent)
├── sentiment_analyzer.py  # LLM interaction logic (used by SentimentAgent)
├── requirements.txt       # Dependencies
├── .env                   # API Keys (Excluded from Git)
├── static/
│   ├── index.html         # Dashboard UI
│   ├── css/style.css      # Styling
│   └── js/main.js         # Frontend Logic
└── README.md              # Documentation
```

---

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**. It demonstrates the application of Agentic AI in finance but is not financial advice.

- Stock predictions are based on historical patterns and cannot guarantee future results.
- LLM hallucinations are possible; always verify news sources.
- Always do your own research before investing.
