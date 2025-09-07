
# Oneironet

Privacy-first, multi‑lens dream interpreter (no storage). Dockerized FastAPI + lightweight UI.

## Run (Docker)

```bash
cd oneironet
docker build -t oneironet .
# Ensure your key is exported in this shell
export OPENAI_API_KEY=sk-... 
docker run -e OPENAI_API_KEY -p 8000:8000 oneironet
# open http://localhost:8000
```

Or with Compose:

```bash
docker compose up --build
```

## Dev (without Docker)

```bash
pip install -r backend/requirements.txt
export OPENAI_API_KEY=sk-...
uvicorn backend.app:app --reload
```

## Notes
- No user data is stored; everything is session-only in the browser.
- Moon phase computed locally; no external APIs.
- Symbol dictionary is a small starter you can expand easily in `backend/app.py`.
- Multi-agent interpretations are simulated via separate system prompts.
