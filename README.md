# VGC Team Analyzer (Japanese article summariser)

Paste a Japanese Pokémon VGC team report (note.com, Hatena Blog, liberty-note.com, or any public blog) and get it back in English:

- the team as a **Showdown-importable paste** (item, ability, Tera type, nature, EVs, moves), with a copy button
- EV spreads, plus the author's reasoning for them ("survives X", "outspeeds Y") translated with full stat names
- team strategy, strengths/weaknesses, synergies and a full English translation of the article
- downloadable translation and paste `.txt` files

It is a single Streamlit app. Analysis is done by Google Gemini using **the user's own API key**, which they paste into the sidebar. The key is kept in their Streamlit session only and never stored on the server.

## Run locally

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt   # Windows; use .venv/bin/python on macOS/Linux
.venv/Scripts/python -m streamlit run app.py
```

Open http://localhost:8501, paste a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) into the sidebar, then paste an article URL or its text.

## Configuration

| Setting | Where | Default | Purpose |
|---|---|---|---|
| Gemini API key | Sidebar (per user) | none | Required. Each user brings their own. |
| `GEMINI_MODEL` | env var or `.streamlit/secrets.toml` | `gemini-2.5-flash` | Model used for text and image analysis. Change it here when Google retires a model. |

## Deploy (Streamlit Community Cloud)

Point a new app at this repo with `app.py` as the entry file. Cloud installs `requirements.txt` and uses Python 3.11 (`runtime.txt`). No secrets are needed. Optionally set `GEMINI_MODEL` in the app's secrets.

## How it works

`app.py` (routing, analysis flow, result cache) → `src/core/scraper.py` (fetch and extract the article; note.com is read through its public JSON API) → `src/core/analyzer.py` + `src/core/prompts.py` (Gemini call returning JSON) → `src/core/pokemon_validator.py` (fixes known name mistranslations) → `src/ui/` (rendering, Showdown export).

- **Caching:** successful results are cached in memory per (model, URL or text), so analysing the same article again costs no Gemini call. The cache holds 100 entries and is lost when the app restarts.
- **URL safety:** only `http(s)` URLs that resolve to public IPs are fetched, and redirects into private or internal addresses are refused (SSRF guard in `src/utils/utils.py`). This also covers images found on the page.
- **Paywalled note.com articles:** only the free part is available. The app analyses whatever text is public.

## Tests and lint

```bash
.venv/Scripts/python -m pytest -q
.venv/Scripts/ruff check .
```

Tests are offline. They cover the SSRF guard, the Showdown paste export, API-error handling, model config and the name-correction rules.

## Status of the old compliance docs

`COMPLIANCE_CHECKLIST.md` describes a v2.0 FastAPI backend with a domain allowlist, robots.txt checks, PII redaction, rate limiting and an age gate. That backend was removed in commit `e0edf6d`. See `docs/REVIEW-2026-10-10.md` for what exists today and what is recommended.
