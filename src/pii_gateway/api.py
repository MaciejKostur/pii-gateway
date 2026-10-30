"""FastAPI: filtr PII + proxy zgodny z OpenAI /v1/chat/completions.

Uruchomienie:  uvicorn pii_gateway.api:app --reload
Zmienne srodowiskowe: LLM_BASE_URL (domyslnie https://api.openai.com/v1), LLM_API_KEY
Uwaga: w logach NIGDY nie zapisujemy tresci promptow.
"""
import os
import uuid
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .anonymizer import Mode, PIIBlockedError, anonymize
from .detector import Detector
from .vault import Vault

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["detector"] = Detector()
    state["vault"] = Vault()
    yield


app = FastAPI(title="PII Gateway", lifespan=lifespan)


class AnonymizeRequest(BaseModel):
    text: str
    mode: Mode = Mode.PSEUDONYMIZE
    session_id: str | None = None


class DeanonymizeRequest(BaseModel):
    text: str
    session_id: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/anonymize")
def anonymize_endpoint(req: AnonymizeRequest):
    session_id = req.session_id or uuid.uuid4().hex
    entities = state["detector"].detect(req.text)
    try:
        result = anonymize(req.text, entities, req.mode, state["vault"], session_id)
    except PIIBlockedError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"text": result, "session_id": session_id,
            "entities": sorted({e.type for e in entities})}


@app.post("/v1/deanonymize")
def deanonymize_endpoint(req: DeanonymizeRequest):
    return {"text": state["vault"].restore(req.session_id, req.text)}


@app.post("/v1/chat/completions")
async def chat_completions(payload: dict):
    if payload.get("stream"):
        raise HTTPException(status_code=501, detail="Streaming jeszcze nieobslugiwany")

    session_id = uuid.uuid4().hex
    detector, vault = state["detector"], state["vault"]
    try:
        for msg in payload.get("messages", []):
            if isinstance(msg.get("content"), str):
                msg["content"] = anonymize(
                    msg["content"], detector.detect(msg["content"]),
                    Mode.PSEUDONYMIZE, vault, session_id,
                )
    except PIIBlockedError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    base = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    headers = {"Authorization": f"Bearer {os.getenv('LLM_API_KEY', '')}"}
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{base}/chat/completions", json=payload, headers=headers)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Blad po stronie LLM")

    data = resp.json()
    for choice in data.get("choices", []):
        content = choice.get("message", {}).get("content")
        if isinstance(content, str):
            choice["message"]["content"] = vault.restore(session_id, content)
    vault.drop(session_id)
    return data
