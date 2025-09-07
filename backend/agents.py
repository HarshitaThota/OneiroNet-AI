
from typing import List, Dict

JUNGIan_SYSTEM = """You are the Jungian Agent. Interpret dreams using Carl Jung's concepts: 
archetypes, shadow, anima/animus, individuation, and personal vs collective unconscious.
Be gentle, non-deterministic, and invite reflection. Keep 150-220 words."""

VEDIC_SYSTEM = """You are the Vedic Agent. Interpret dreams using Swapna Shastra, dharma, omens,
gunas (sattva/rajas/tamas), and karmic symbolism. Avoid fatalism; emphasize auspicious remedies 
(e.g., mantra, charity). Keep 150-220 words."""

ASTRO_SYSTEM = """You are the Astrologer Agent. Tie dream themes to lunar phase energy and the user's zodiac Sun sign if provided.
Explain how the phase (New, Waxing, Full, Waning) may color emotional tone, recall, or symbolism.
Offer 2-3 reflective prompts. Keep 120-180 words."""

SURREAL_SYSTEM = """You are the Surrealist Agent. Offer a poetic, metaphor-forward, dreamlike riff that
embraces ambiguity and imagistic thinking. 6-8 short lines, no more than ~120 words total."""

FOLLOWUP_ASKER = """You are a compassionate interviewer. Ask 3 concise follow-up questions
that would most help produce a deeper interpretation. Prioritize emotions, recent life context,
and repeating symbols. Number them 1-3. Keep under 60 words."""


def build_agent_messages(lens: str, dream: str, answers: Dict, moon: Dict, user_meta: Dict) -> List[Dict]:
    """
    Constructs messages for each agent using available context.
    """
    shared_context = f"""
Dream text: {dream}

User Answers (optional): {answers or {}}

Moon:
 - Phase: {moon.get('phase_name','unknown')}
 - Illumination: {moon.get('illumination','?')}%
 - Influence: {moon.get('influence','')}

User Meta:
 - Sun Sign: {user_meta.get('sun_sign','unknown')}
 - Notable Stressors: {user_meta.get('stressors','unknown')}
    """.strip()

    if lens == "jungian":
        system = JUNGIan_SYSTEM
        user = f"Interpret via Jungian psychology. Context:\n{shared_context}"
    elif lens == "vedic":
        system = VEDIC_SYSTEM
        user = f"Interpret via Vedic dream lore. Context:\n{shared_context}"
    elif lens == "astrologer":
        system = ASTRO_SYSTEM
        user = f"Interpret with lunar phase + sun sign. Context:\n{shared_context}"
    elif lens == "surrealist":
        system = SURREAL_SYSTEM
        user = f"Create a short surrealist take inspired by:\n{dream}\nTone: gentle, imagistic."
    elif lens == "followup":
        system = FOLLOWUP_ASKER
        user = f"Given the dream:\n{dream}\nand any answers: {answers or {}}"
    else:
        raise ValueError("Unknown lens")

    return [
        {"role":"system","content":system},
        {"role":"user","content":user}
    ]
