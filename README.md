# 📈 Agentic AI Stock Predictor

A sophisticated **Autonomous Agentic System** for stock market analysis. This application moves beyond traditional scripts by employing a **Cognitive AI Agent** that dynamically plans, reasons, and executes tasks using a suite of specialized tools.

## 🤖 The Agentic Architecture

Unlike traditional "Orchestrator" systems that follow a hardcoded script, this project uses a **ReAct (Reasoning + Acting) Loop** powered by **LangChain** and **Google Gemini**.

**How it works:**

1.  **User Query:** You ask a natural language question (e.g., _"Should I buy Apple? Check sentiment and technicals"_).
2.  **Cognitive Reasoning:** The "Brain" (Gemini 2.0 Flash) analyzes the request and creates a plan.
3.  **Dynamic Tool Selection:** The AI autonomously decides which tools to use and in what order. It might fetch data, then read news, then run a prediction—or skip steps if they aren't needed.
4.  **Synthesis:** The Agent combines quantitative data (charts/prices) with qualitative data (news) to give a human-like recommendation.

### The Toolkit (Specialized Agents)

The AI has access to these autonomous tools:

- **🕵️‍♂️ Market Data Tool ("The Librarian")**
  - **Role:** Autonomous data acquisition.
  - **Capabilities:** Smart caching of stock data via `yfinance`. Prevents API rate limits and handles data cleaning.
- **📈 Technical Analyst Tool ("The Chartist")**
  - **Role:** Pattern recognition.
  - **Capabilities:** Computes MACD, Signal Lines, and EMAs to generate independent Buy/Sell signals.
- **🔮 Prediction Tool ("The Futurist")**
  - **Role:** Quantitative forecasting.
  - **Capabilities:** Runs a Deep Learning **LSTM** model to generate 7-day price forecasts.
- **🧠 Sentiment Tool ("The Analyst")**
  - **Role:** Qualitative reasoning.
  - **Capabilities:** Powered by **Google Gemini**. Reads unstructured financial news and outputs a nuanced sentiment score with reasoning.
- **💼 Portfolio Tool ("The Trader")**
  - **Role:** Risk and strategy execution.
  - **Capabilities:** Simulates a trading account ($10k start) to calculate ROI, Win Rate, and Net Profit.

---

## 🚀 Features

- **💬 Conversational AI:** Chat directly with the agent. Ask complex, multi-step questions like _"Compare the sentiment of Tesla vs. Ford."_
- **🧠 True Autonomy:** The system handles errors and ambiguity (e.g., correcting typos in tickers) without crashing.
- **Real-Time Data:** Smart caching with `yfinance` to ensure speed.
- **Deep Learning:** LSTM Neural Network for time-series forecasting.
- **Modern UI:** Responsive, dark-themed dashboard with interactive charts and a new AI Chat interface.

---

## 🛠️ Tech Stack

- **Agent Framework:** LangChain (Python)
- **LLM (The Brain):** Google Gemini 2.0 Flash / 1.5 Flash
- **Deep Learning:** TensorFlow / Keras (LSTM)
- **Backend:** Flask
- **Data:** Pandas, NumPy, YFinance
- **Frontend:** HTML5, CSS3 (Glassmorphism), JavaScript, Chart.js

---

## ⚙️ Installation Guide

### Prerequisites

- **Python 3.10** or **3.11** (Strict requirement for TensorFlow)
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
    http://localhost:5001
    ```
    _(Note: The application runs on port 5001 to avoid conflicts with AirPlay/Control Center on macOS)_

---

## 📂 Project Structure

```text
macd-stock-predictor/
├── agents.py              # The "Toolkit": LangChain tools and Agent logic
├── app.py                 # The "Brain": Agent Executor & Flask routes
├── lstm_model.py          # Deep Learning model logic
├── sentiment_analyzer.py  # LLM interaction logic
├── requirements.txt       # Dependencies (includes langchain, google-genai)
├── .env                   # API Keys (Excluded from Git)
├── static/
│   ├── index.html         # Dashboard UI with Chat Interface
│   ├── css/style.css      # Styling
│   └── js/main.js         # Frontend Logic & Defensive Checks
└── README.md              # Documentation
```

## ⚠️ Disclaimer

This tool is for educational and research purposes only. It demonstrates the application of Agentic AI in finance but is not financial advice.

-> Stock predictions are based on historical patterns and cannot guarantee future results.

-> LLM hallucinations are possible; always verify news sources.

-> Always do your own research before investing.
