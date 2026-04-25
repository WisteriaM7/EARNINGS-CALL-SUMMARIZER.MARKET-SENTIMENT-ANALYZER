# 📈 FinScope Earnings Call Analyzer (Mistral + Ollama)

An AI-powered earnings call analysis tool for **FinScope Capital**. Paste or upload any earnings call transcript and get a structured 3-sentence summary, sentiment classification, and detailed financial insights — all running locally with no API keys required.

---

## 🧠 Tech Stack

| Layer     | Technology             |
|-----------|------------------------|
| LLM       | Mistral (via Ollama)   |
| Backend   | FastAPI + Uvicorn      |
| Frontend  | Streamlit              |
| Language  | Python 3.10+           |

---

## 📁 Project Structure

```
earnings-call-analyzer/
│
├── backend/
│   ├── __init__.py
│   └── main.py                # FastAPI: /analyze/ with 3 structured prompts
│
├── frontend/
│   └── app.py                 # Streamlit UI with tabs, sentiment banner, download
│
├── data/
│   └── tesla_q4_2024.txt      # Realistic Q4 2024 earnings call transcript sample
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/earnings-call-analyzer.git
cd earnings-call-analyzer
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama & Pull Mistral

```bash
ollama pull mistral
```

---

## 🚀 Running the App

**Terminal 1 — Start the Backend:**

```bash
uvicorn backend.main:app --reload
```

**Terminal 2 — Start the Frontend:**

```bash
streamlit run frontend/app.py
```

Open `http://localhost:8501`. Click **Load Tesla Q4 2024 Sample** in the sidebar to test immediately.

---

## 📌 API Endpoint

| Method | Endpoint    | Description                                  |
|--------|-------------|----------------------------------------------|
| GET    | `/`         | Health check                                 |
| POST   | `/analyze/` | Analyze transcript → summary, sentiment, insights |

### Example Response

```json
{
  "summary": "Tesla reported record Q4 deliveries of 495,000 vehicles...",
  "sentiment": "Positive",
  "insights": "Revenue & Growth: Revenue of $25.7B, up 15% YoY...",
  "word_count": 612,
  "char_count": 3841
}
```

---

## ✅ Features

- Paste text or upload a `.txt` transcript directly from the sidebar
- Color-coded sentiment banner (green / yellow / red)
- Tabbed layout — Summary & Sentiment on one tab, Insights on another
- Insights structured into 4 categories: Revenue & Growth, Forward Guidance, Risk Factors, Strategic Signals
- Full analysis report downloadable as `.txt`
- Document size guard — rejects transcripts over 60,000 characters
- Word and character count display
- CORS-enabled FastAPI backend with sentiment normalization

---

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| Backend not connecting | Run `uvicorn backend.main:app --reload` |
| Ollama not responding | Run `ollama serve` and check `ollama list` |
| Sentiment shows wrong label | Mistral response is normalized — check backend logs if unexpected |
| Analysis times out | Mistral runs 3 sequential calls; try a shorter transcript first |
| .txt file not loading | Ensure the file is plain text (UTF-8 encoded) |
