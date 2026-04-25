from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import re

app = FastAPI(title="FinScope Earnings Call Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
VALID_SENTIMENTS = {"positive", "neutral", "negative"}

PROMPTS = {
    "summary": (
        "You are a financial analyst at an investment research firm. "
        "Summarize the following earnings call transcript in exactly 3 concise sentences. "
        "Cover: overall performance, key financial highlights, and management outlook.\n\n"
        "Transcript:\n{text}"
    ),
    "sentiment": (
        "You are a financial sentiment analyst. "
        "Based on the earnings call transcript below, classify the overall market sentiment. "
        "Respond with exactly one word: Positive, Neutral, or Negative. "
        "Do not add any explanation.\n\n"
        "Transcript:\n{text}"
    ),
    "insights": (
        "You are a senior equity research analyst. "
        "Extract the key financial insights from the following earnings call transcript. "
        "Organise your output under these headings:\n"
        "- Revenue & Growth: key revenue figures, growth rates, delivery numbers\n"
        "- Forward Guidance: management outlook, targets, and projections\n"
        "- Risk Factors: challenges, competitive threats, cost pressures mentioned\n"
        "- Strategic Signals: new initiatives, investments, or product developments\n\n"
        "Be specific and cite figures where available.\n\n"
        "Transcript:\n{text}"
    ),
}

SENTIMENT_LABELS = {"positive": "Positive", "neutral": "Neutral", "negative": "Negative"}


def query_model(prompt: str, timeout: int = 120) -> str:
    """Send a prompt to Ollama Mistral and return the response."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout=timeout
        )
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to Ollama. Make sure it is running on port 11434."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {str(e)}")


def normalize_sentiment(raw: str) -> str:
    """Extract clean sentiment label from model response."""
    lower = raw.lower()
    for label in VALID_SENTIMENTS:
        if label in lower:
            return SENTIMENT_LABELS[label]
    return "Neutral"


@app.get("/")
def root():
    return {"message": "FinScope Earnings Call Analyzer API is running!"}


@app.post("/analyze/")
def analyze_call(text: str = Form(...)):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Transcript text cannot be empty.")

    if len(text) > 60000:
        raise HTTPException(
            status_code=413,
            detail="Transcript too large. Please limit to 60,000 characters."
        )

    results = {}
    for key, prompt_template in PROMPTS.items():
        prompt = prompt_template.format(text=text)
        results[key] = query_model(prompt)

    # Normalize sentiment
    results["sentiment"] = normalize_sentiment(results.get("sentiment", ""))

    return {
        "summary": results["summary"],
        "sentiment": results["sentiment"],
        "insights": results["insights"],
        "word_count": len(text.split()),
        "char_count": len(text),
    }
