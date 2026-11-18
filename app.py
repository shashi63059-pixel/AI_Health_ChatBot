import os
import sys
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import bot

INDEX_FILE = os.path.join(BASE_DIR, "index.html")

DISCLAIMER = (
    "Educational information only—not a medical diagnosis. "
    "A symptom overlap from this dataset cannot confirm a condition. "
    "For health concerns, speak with a licensed healthcare professional."
)
UNKNOWN_DETAILS = (
    "The available symptom data is not sufficient to suggest a reliable "
    "dataset match. This chatbot cannot diagnose illness. Please consult "
    "a qualified healthcare professional for an assessment."
)

app = FastAPI(title="AI Health ChatBot", version="1.1.0")


class ChatRequest(BaseModel):
    message: Optional[str] = None
    symptoms: Optional[List[str]] = None
    primary: Optional[str] = None


def _clean_symptoms(values):
    cleaned = []
    for value in values or []:
        name = str(value).strip().lower()
        if name and name not in cleaned:
            cleaned.append(name)
    return cleaned


def _known_symptoms():
    # Use the canonical feature names used by bot.py.
    return {str(name).strip().lower() for name in bot.feature_names if str(name).strip()}


def _parse_options(text):
    options = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("-->"):
            name = stripped[3:].strip()
            if name:
                options.append(name)
    return options


@app.get("/")
def index():
    if not os.path.isfile(INDEX_FILE):
        raise HTTPException(status_code=404, detail="index.html was not found.")
    return FileResponse(INDEX_FILE, media_type="text/html")


@app.get("/api/health")
def health():
    return {"status": "ok", "engine": "decision-tree+numpy-nn"}


@app.get("/api/symptoms")
def symptoms():
    names = sorted(_known_symptoms())
    return {"count": len(names), "symptoms": names}


def _make_prediction(symptoms, primary=None):
    selected = _clean_symptoms(symptoms)
    if primary:
        primary = str(primary).strip().lower()
        if primary not in _known_symptoms():
            raise HTTPException(status_code=422, detail="Unknown primary symptom.")
        if primary not in selected:
            selected.insert(0, primary)

    known = _known_symptoms()
    invalid = [name for name in selected if name not in known]
    if invalid:
        raise HTTPException(
            status_code=422,
            detail="Unrecognized symptom(s): " + ", ".join(invalid),
        )
    if not selected:
        raise HTTPException(status_code=400, detail="Select at least one symptom.")

    disease = str(bot.get_pridected_value(selected) or "Unknown").strip()
    if disease.lower() in {"unknown", "none", ""}:
        details = UNKNOWN_DETAILS
        disease = "No reliable match"
    else:
        # This is only a dataset-based suggestion, never a confirmed diagnosis.
        details = bot.get_diesese_practions(disease)

    return {
        "type": "diagnosis",
        "disease": disease,
        "details": details,
        "symptoms": selected,
        "disclaimer": DISCLAIMER,
    }


@app.post("/api/chat")
def chat(payload: ChatRequest):
    selected = _clean_symptoms(payload.symptoms)
    message = (payload.message or "").strip()

    if selected:
        return _make_prediction(selected, payload.primary)

    if not message:
        raise HTTPException(status_code=400, detail="Provide a message or a symptom list.")

    result = bot.getresponse(message)

    if isinstance(result, tuple):
        reply = str(result[0])
        options = _clean_symptoms(result[1] if len(result) > 1 else [])
        primary = str(result[2]).strip().lower() if len(result) > 2 and result[2] else None
        return {
            "type": "options" if options else "text",
            "reply": reply,
            "options": options,
            "primary": primary,
            "disclaimer": DISCLAIMER,
        }

    if isinstance(result, list) and result:
        reply = str(result[0])
        options = _parse_options(reply)
        return {
            "type": "options" if options else "text",
            "reply": reply,
            "options": options,
            "primary": None,
            "disclaimer": DISCLAIMER,
        }

    return {
        "type": "text",
        "reply": "Sorry, I could not process that request.",
        "disclaimer": DISCLAIMER,
    }


@app.post("/api/predict")
def predict(payload: ChatRequest):
    return _make_prediction(payload.symptoms or [], payload.primary)
