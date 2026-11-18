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
    "This assistant provides educational information only and is not a medical "
    "diagnosis. Always consult a licensed healthcare professional."
)

app = FastAPI(title="AI Health ChatBot", version="1.0.0")


class ChatRequest(BaseModel):
    message: Optional[str] = None
    symptoms: Optional[List[str]] = None
    primary: Optional[str] = None


def _clean_symptoms(values):
    cleaned = []
    for value in values or []:
        name = str(value).strip()
        if name and name not in cleaned:
            cleaned.append(name)
    return cleaned


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
    return FileResponse(INDEX_FILE, media_type="text/html")


@app.get("/api/health")
def health():
    return {"status": "ok", "engine": "decision-tree+numpy-nn"}


@app.get("/api/symptoms")
def symptoms():
    names = []
    for name in bot.feature_names:
        label = str(name).strip()
        if label and label not in names:
            names.append(label)
    return {"count": len(names), "symptoms": names}


@app.post("/api/chat")
def chat(payload: ChatRequest):
    symptoms = _clean_symptoms(payload.symptoms)
    message = (payload.message or "").strip()

    if symptoms:
        primary = (payload.primary or "").strip()
        if primary and primary not in symptoms:
            symptoms.insert(0, primary)
        disease = bot.get_pridected_value(symptoms)
        details = bot.get_diesese_practions(disease)
        return {
            "type": "diagnosis",
            "disease": disease.strip(),
            "details": details,
            "symptoms": symptoms,
            "disclaimer": DISCLAIMER,
        }

    if not message:
        raise HTTPException(status_code=400, detail="Provide a message or a symptom list.")

    result = bot.getresponse(message)

    if isinstance(result, tuple):
        reply, options, primary = result
        return {
            "type": "options",
            "reply": reply,
            "options": _clean_symptoms(options),
            "primary": primary,
            "disclaimer": DISCLAIMER,
        }

    if isinstance(result, list) and result:
        reply = result[0]
        return {
            "type": "options" if "-->" in reply else "text",
            "reply": reply,
            "options": _parse_options(reply),
            "primary": None,
            "disclaimer": DISCLAIMER,
        }

    return {"type": "text", "reply": "Sorry, I could not process that request.", "disclaimer": DISCLAIMER}


@app.post("/api/predict")
def predict(payload: ChatRequest):
    symptoms = _clean_symptoms(payload.symptoms)
    if not symptoms:
        raise HTTPException(status_code=400, detail="Provide at least one symptom.")
    return chat(ChatRequest(symptoms=symptoms, primary=payload.primary))
