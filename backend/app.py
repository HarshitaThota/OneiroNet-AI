
import os
import math
from datetime import datetime, timezone
from typing import Dict, Any, List

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# OpenAI client will be initialized on-demand in call_openai function

from .agents import build_agent_messages

app = FastAPI(title="Oneironet")
templates = Jinja2Templates(directory="/app/backend/templates")
app.mount("/static", StaticFiles(directory="/app/backend/static"), name="static")


class InterpretReq(BaseModel):
    dream_text: str
    answers: Dict[str, Any] | None = None
    sun_sign: str | None = None
    dream_date: str | None = None  # YYYY-MM-DD


class RitualReq(BaseModel):
    dream_text: str
    dream_type: str  # nightmare, flying, prophetic, unknown


SYMBOL_DB = {
    "snake": {
        "jungian": "Transformation, instinct, the shadow; kundalini energy rising.",
        "vedic": "Can signify naga energies; auspicious if calm, caution if biting.",
        "astrology": "Serpentine themes in Scorpio/Pluto: rebirth, depth, taboo truths.",
        "cultural": "Dual symbol: healer (staff of Asclepius) and tempter (Eden)."
    },
    "water": {
        "jungian": "Unconscious/emotions; depth, cleansing, potential overwhelm.",
        "vedic": "Tirtha/purification; clarity if clear, confusion if muddy or stormy.",
        "astrology": "Water signs (Cancer/Scorpio/Pisces): sensitivity, intuition, memory.",
        "cultural": "Ritual ablutions, rivers as deities; flow and change."
    },
    "flying": {
        "jungian": "Liberation, transcendence of constraints, or desire for control.",
        "vedic": "Siddhi-like freedom; auspicious beginnings when serene.",
        "astrology": "Air sign flavor (Gemini/Libra/Aquarius): ideas, perspective, detachment.",
        "cultural": "Myths of flight symbolize ambition and spiritual ascent."
    }
}


def moon_phase_info(dt: datetime) -> dict:
    """
    Simple moon phase approximation (Conway variant). Returns phase name & illumination.
    """
    # Days since known new moon reference (2000-01-06 18:14 UTC)
    ref = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
    days = (dt.replace(tzinfo=timezone.utc) - ref).total_seconds() / 86400.0
    synodic = 29.53058867
    phase = days % synodic
    illum = (1 - math.cos(2 * math.pi * phase / synodic)) / 2  # 0..1

    if phase < 1.84566:
        name = "New Moon"
        influence = "Seeds, introspection, beginnings."
    elif phase < 5.53699:
        name = "Waxing Crescent"
        influence = "Intentions, gentle momentum."
    elif phase < 9.22831:
        name = "First Quarter"
        influence = "Action, decisions, friction becomes fuel."
    elif phase < 12.91963:
        name = "Waxing Gibbous"
        influence = "Refinement, adjustment, anticipation."
    elif phase < 16.61096:
        name = "Full Moon"
        influence = "Culmination, illumination, vivid recall."
    elif phase < 20.30228:
        name = "Waning Gibbous"
        influence = "Integration, gratitude, sharing."
    elif phase < 23.99361:
        name = "Last Quarter"
        influence = "Release, reevaluation, boundaries."
    elif phase < 27.68493:
        name = "Waning Crescent"
        influence = "Rest, closure, surrender."
    else:
        name = "New Moon"
        influence = "Seeds, introspection, beginnings."

    return {
        "phase_name": name,
        "illumination": round(illum * 100, 1),
        "influence": influence
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/moonphase")
async def get_moonphase(date: str | None = None):
    try:
        dt = datetime.fromisoformat(date) if date else datetime.utcnow()
        info = moon_phase_info(dt)
        return JSONResponse(info)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/symbols")
async def symbols(term: str):
    t = term.lower().strip()
    if t in SYMBOL_DB:
        return JSONResponse({"term": t, **SYMBOL_DB[t]})
    return JSONResponse({"term": t, "jungian": "", "vedic": "", "astrology": "", "cultural": ""})


@app.post("/api/ritual")
async def ritual(req: RitualReq):
    t = (req.dream_type or "unknown").lower()
    mapping = {
        "nightmare": {
            "breath": "Box breathing 2 minutes (inhale-hold-exhale-hold for 4).",
            "affirm": "I am safe; my body knows how to relax.",
            "prompt": "What fear is asking to be met with care today?"
        },
        "flying": {
            "breath": "3 gentle shoulder rolls + 60 seconds soft belly breaths.",
            "affirm": "I move lightly and choose my direction.",
            "prompt": "Where is life inviting me to take a higher view?"
        },
        "prophetic": {
            "breath": "Slow nasal breathing 10 cycles.",
            "affirm": "Clarity arrives as I listen.",
            "prompt": "What small action could honor this message today?"
        },
        "unknown": {
            "breath": "1 minute of slow, even breaths.",
            "affirm": "I greet today with curiosity.",
            "prompt": "Which feeling from the dream lingers now?"
        }
    }
    return JSONResponse(mapping.get(t, mapping["unknown"]))

from openai import OpenAI
client = OpenAI()  

def call_openai(messages: list[dict], model: str = "gpt-4o-mini") -> str:
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.8,
            max_tokens=400,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI error: {e}]"

@app.post("/api/interpret")
async def interpret(req: InterpretReq):
    dream = req.dream_text.strip()
    if not dream:
        return JSONResponse({"error":"Empty dream"}, status_code=400)

    # Moon context
    dt = datetime.fromisoformat(req.dream_date) if req.dream_date else datetime.utcnow()
    moon = moon_phase_info(dt)

    user_meta = {
        "sun_sign": (req.sun_sign or "").title() if req.sun_sign else "Unknown",
        "stressors": (req.answers or {}).get("stressors","")
    }

    lenses = ["followup","jungian","vedic","astrologer","surrealist"]
    outputs = {}

    for lens in lenses:
        msgs = build_agent_messages(lens, dream, req.answers or {}, moon, user_meta)
        text = call_openai(msgs)
        outputs[lens] = text

    return JSONResponse({
        "moon": moon,
        "agents": outputs
    })
