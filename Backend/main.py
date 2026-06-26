"""
main.py
GlobalInfo Chatbot — FastAPI backend entry point.

Endpoints:
  GET  /                     Health check
  GET  /country/{name}       Raw country data
  POST /chat                 Conversational chatbot endpoint
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

from services.chatbot_service import process_message
from services.country_service import get_country_info

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="GlobalInfo Chatbot API",
    description="A conversational API that answers questions about countries worldwide.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    intent: str
    data: dict | None = None

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def root():
    """Health check — confirms the API is running."""
    return {"message": "🌍 GlobalInfo Chatbot API is running!", "version": "1.0.0"}


@app.get("/country/{country_name}", tags=["Countries"])
def get_country(country_name: str):
    """
    Fetch structured data for a specific country by name.
    Returns capital, population, currencies, languages, region, and more.
    """
    data = get_country_info(country_name)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail=f"Country '{country_name}' not found. Check spelling and try again.",
        )
    return data


@app.post("/chat", response_model=ChatResponse, tags=["Chatbot"])
def chat(request: ChatRequest):
    """
    Main chatbot endpoint. Send a natural language message and get a
    conversational response about a country.

    **Example messages:**
    - "Tell me about Japan"
    - "What is the capital of France?"
    - "Currency of Egypt"
    - "Languages spoken in Switzerland"
    - "Population of India"
    - "Borders of Germany"
    """
    message = request.message.strip()

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    if len(message) > 500:
        raise HTTPException(status_code=400, detail="Message is too long (max 500 characters).")

    result = process_message(message)
    return ChatResponse(
        response=result["response"],
        intent=result["intent"],
        data=result.get("data"),
    )