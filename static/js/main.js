let priceChart = null;
let macdChart = null;
let predictionChart = null;

// DOM Elements
const tickerInput = document.getElementById("ticker");
const periodSelect = document.getElementById("period");
const intervalSelect = document.getElementById("interval");
const analyzeBtn = document.getElementById("analyzeBtn");
const loading = document.getElementById("loading");
const errorDiv = document.getElementById("error");

// Event listeners
if (analyzeBtn) analyzeBtn.addEventListener("click", analyzeStock);
if (tickerInput) {
  tickerInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") analyzeStock();
  });
}

async function analyzeStock() {
  const ticker = tickerInput.value.trim().toUpperCase();
  if (!ticker) {
    showError("Please enter a stock ticker");
    return;
  }

  showLoading(true);
  hideError();

  try {
    const [stockData, signals, backtest, predictions, sentiment] =
      await Promise.all([
        fetchStockData(ticker),
        fetchSignals(ticker),
        fetchBacktest(ticker),
        fetchPredictions(ticker),
        fetchSentiment(ticker),
      ]);

    // Update charts with checks
    updatePriceChart(stockData, signals);
    updateMACDChart(stockData);
    updatePredictionChart(predictions, stockData);
    updateSentimentDisplay(sentiment);

    // Update metrics
    updateMetrics(backtest);

    // Update signal lists
    updateSignalLists(signals);
  } catch (error) {
    console.error(error);
    showError(error.message);
  } finally {
    showLoading(false);
  }
}

// --- API FETCH FUNCTIONS ---
async function fetchStockData(ticker) {
  const p = periodSelect.value;
  const i = intervalSelect.value;
  const res = await fetch(`/api/stock/${ticker}?period=${p}&interval=${i}`);
  if (!res.ok) throw new Error("Failed to fetch stock data");
  return res.json();
}

async function fetchSignals(ticker) {
  const res = await fetch(
    `/api/signals/${ticker}?period=${periodSelect.value}&interval=${intervalSelect.value}`
  );
  if (!res.ok) throw new Error("Failed to fetch signals");
  return res.json();
}

async function fetchBacktest(ticker) {
  const res = await fetch(
    `/api/backtest/${ticker}?period=${periodSelect.value}&interval=${intervalSelect.value}`
  );
  if (!res.ok) throw new Error("Failed to fetch backtest");
  return res.json();
}

async function fetchPredictions(ticker) {
  const res = await fetch(`/api/predict/${ticker}`);
  if (!res.ok) throw new Error("Failed to fetch predictions");
  return res.json();
}

async function fetchSentiment(ticker) {
  const res = await fetch(`/api/sentiment/${ticker}`);
  if (!res.ok) throw new Error("Failed to fetch sentiment");
  return res.json();
}

// --- UPDATE UI FUNCTIONS ---

function updatePriceChart(data, signals) {
  const ctx = document.getElementById("priceChart");
  if (!ctx) return;

  if (priceChart) priceChart.destroy();

  const buyPoints = signals.buy_signals.map((s) => ({ x: s.date, y: s.price }));
  const sellPoints = signals.sell_signals.map((s) => ({
    x: s.date,
    y: s.price,
  }));

  priceChart = new Chart(ctx.getContext("2d"), {
    type: "line",
    data: {
      labels: data.dates,
      datasets: [
        {
          label: "Price",
          data: data.close,
          borderColor: "#6366f1",
          fill: true,
          backgroundColor: "rgba(99, 102, 241, 0.1)",
          tension: 0.4,
          pointRadius: 0,
        },
        {
          label: "Buy",
          data: buyPoints,
          backgroundColor: "#10b981",
          pointStyle: "triangle",
          pointRadius: 8,
          showLine: false,
        },
        {
          label: "Sell",
          data: sellPoints,
          backgroundColor: "#ef4444",
          pointStyle: "triangle",
          rotation: 180,
          pointRadius: 8,
          showLine: false,
        },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });
}

function updateMACDChart(data) {
  const ctx = document.getElementById("macdChart");
  if (!ctx) return;

  if (macdChart) macdChart.destroy();

  macdChart = new Chart(ctx.getContext("2d"), {
    type: "line",
    data: {
      labels: data.dates,
      datasets: [
        {
          label: "MACD",
          data: data.macd,
          borderColor: "#6366f1",
          tension: 0.4,
          pointRadius: 0,
        },
        {
          label: "Signal",
          data: data.signal_line,
          borderColor: "#f59e0b",
          tension: 0.4,
          pointRadius: 0,
        },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });
}

function updatePredictionChart(predictions, stockData) {
  const ctx = document.getElementById("predictionChart");
  const container = document.getElementById("predictionSection");

  // Check if error exists AND container exists before setting innerHTML
  if (predictions.error && container) {
    container.innerHTML = `<div class="chart-header"><h2>📊 Predictions</h2></div><p style="text-align:center; padding:2rem; color:var(--text-secondary)">${predictions.error}</p>`;
    return;
  }

  if (!ctx) return;
  if (predictionChart) predictionChart.destroy();

  const last30 = stockData.dates.slice(-30);
  const last30Prices = stockData.close.slice(-30);

  const allDates = [...last30, ...(predictions.prediction_dates || [])];
  const actual = [
    ...last30Prices,
    ...Array(predictions.predictions?.length || 0).fill(null),
  ];
  const predicted = [
    ...Array(last30.length).fill(null),
    ...(predictions.predictions || []).map((p) =>
      Array.isArray(p) ? p[0] : p
    ),
  ];

  predictionChart = new Chart(ctx.getContext("2d"), {
    type: "line",
    data: {
      labels: allDates,
      datasets: [
        {
          label: "Actual",
          data: actual,
          borderColor: "#6366f1",
          tension: 0.4,
        },
        {
          label: "Predicted",
          data: predicted,
          borderColor: "#10b981",
          borderDash: [5, 5],
          tension: 0.4,
        },
      ],
    },
    options: { responsive: true, maintainAspectRatio: false },
  });
}

function updateSentimentDisplay(sentiment) {
  const container = document.getElementById("sentimentSection");
  if (!container) return; // Prevent Null Crash

  if (sentiment.error) {
    container.innerHTML = `<div class="sentiment-header"><h2>💭 Sentiment</h2></div><p style="text-align:center; padding:2rem">${sentiment.error}</p>`;
    return;
  }

  const color =
    sentiment.overall_sentiment > 0.1
      ? "#10b981"
      : sentiment.overall_sentiment < -0.1
      ? "#ef4444"
      : "#f59e0b";

  container.innerHTML = `
        <div class="sentiment-header"><h2>💭 Market Sentiment</h2></div>
        <div class="sentiment-content">
            <div class="sentiment-gauge">
                <div class="sentiment-score" style="color: ${color}">${(
    sentiment.overall_sentiment || 0
  ).toFixed(2)}</div>
                <div class="sentiment-label" style="color: ${color}">${
    sentiment.sentiment_label || "Neutral"
  }</div>
            </div>
            ${
              sentiment.reasoning
                ? `<div style="text-align:center; margin-top:1rem; color:var(--text-secondary)">${sentiment.reasoning}</div>`
                : ""
            }
        </div>
    `;
}

function updateMetrics(backtest) {
  // Helper function to safely set text content
  const set = (id, val, color) => {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = val;
      if (color) el.style.color = color;
    }
  };

  set(
    "totalProfit",
    `$${backtest.total_profit}`,
    backtest.total_profit >= 0 ? "#10b981" : "#ef4444"
  );
  set("roi", `${backtest.roi}%`, backtest.roi >= 0 ? "#10b981" : "#ef4444");
  set("portfolioValue", `$${backtest.final_value}`);
  set(
    "winRate",
    `${backtest.win_rate}%`,
    backtest.win_rate >= 50 ? "#10b981" : "#ef4444"
  );
}

function updateSignalLists(signals) {
  const buyEl = document.getElementById("buySignals");
  const sellEl = document.getElementById("sellSignals");

  if (buyEl) {
    buyEl.innerHTML = signals.buy_signals
      .map(
        (s) =>
          `<div class="signal-item buy">
                <div class="signal-date">${s.date}</div>
                <div class="signal-price">₹${s.price.toFixed(2)}</div>
            </div>`
      )
      .join("");
  }

  if (sellEl) {
    sellEl.innerHTML = signals.sell_signals
      .map(
        (s) =>
          `<div class="signal-item sell">
                <div class="signal-date">${s.date}</div>
                <div class="signal-price">₹${s.price.toFixed(2)}</div>
            </div>`
      )
      .join("");
  }
}

function showLoading(show) {
  if (loading) loading.classList.toggle("active", show);
}

function showError(message) {
  if (errorDiv) {
    errorDiv.textContent = message;
    errorDiv.classList.add("active");
    setTimeout(() => errorDiv.classList.remove("active"), 5000);
  }
}

function hideError() {
  if (errorDiv) errorDiv.classList.remove("active");
}

// Agent Chat Function
async function askAgent() {
  const input = document.getElementById("agentInput");
  const responseDiv = document.getElementById("agentResponse");

  if (!input || !responseDiv || !input.value) return;

  const question = input.value;
  responseDiv.innerHTML = "Thinking...";

  try {
    const res = await fetch("/api/agent/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: question }),
    });
    const data = await res.json();
    responseDiv.innerHTML = data.error
      ? `<span style="color:red">${data.error}</span>`
      : `<span style="color:#10b981">${data.answer}</span>`;
  } catch (e) {
    responseDiv.innerHTML = "Network Error";
  }
}

window.addEventListener("load", () => {
  analyzeStock();
});
