Here is a simplified, professional README. Keep your files clean and your instructions even cleaner.

---

# 🚀 CommercePulse: Live E-Commerce Data API

A real-time data generator that simulates a "live" e-commerce event stream. It is designed to act as a source system for Data Engineering pipelines, providing a steady flow of "noisy" data (duplicates, late arrivals, and schema drift).

## ⚡ Quick Start (Setup Instructions)

### 1. Prepare your Repository

Ensure your GitHub repository has these 4 files:

* `main.py`: The FastAPI application.
* `requirements.txt`: List of dependencies (`fastapi`, `uvicorn`, `sqlalchemy`).
* `render.yaml`: The blueprint for Render deployment.
* `.github/workflows/daily_sync.yml`: The automated orchestrator.

### 2. Deploy to Render

1. Push your code to **GitHub**.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** > **Blueprint**.
4. Connect your GitHub repo and click **Deploy**.
5. **Copy your Service URL** (e.g., `https://my-api.onrender.com`).

### 3. Activate the Automated "Data Lake"

1. Open your **GitHub Repository** > **Settings**.
2. Navigate to **Actions** > **General**.
3. Set **Workflow permissions** to **"Read and write permissions"** (so the Action can save your data).
4. Go to the **Actions** tab, select **Daily Data Sync**, and click **Run workflow**.

---

## 📡 Usage

### Live Stream Endpoint

This endpoint simulates events happening **right now** in West Africa Time (WAT).

```bash
# Get events that "just happened"
curl "https://commerce-pulse-api.onrender.com/events"

```

### Batch Endpoint

Generate a full day of historical data.

```bash
# Get 500 events for a specific date
curl "https://commerce-pulse-api.onrender.com/events?events=2000"
```

---

## 🛠️ How it Works

* **The API (Render):** Generates events in-memory. If a request is made at 10:00 AM, it only shows events from 12:00 AM to 10:00 AM.
* **The Database (SQLite):** Remembers Order IDs so that "Refunds" or "Shipments" correctly link back to "Orders" created earlier.
* **The Orchestrator (GitHub Actions):** Wakes up the API every hour, pulls the data, and saves it to the `/data` folder in your repository.

## 📁 Project Structure

```text
├── .github/workflows/  # Orchestration (The "Clock")
├── data/               # Your "Data Lake" (JSONL files)
├── main.py             # The API Engine
├── render.yaml         # Deployment Config
└── requirements.txt    # Python Libraries

```

---
