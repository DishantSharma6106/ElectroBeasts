# 🐉 ElectroBeasts

A spec-based phone finder. Enter the specs you care about (RAM, AnTuTu, battery,
camera, brightness, brand…) and ElectroBeasts ranks the matching “beasts” by a
weighted match score — then lets you compare them side by side.

Built with **FastAPI** + a lightweight vanilla-JS frontend. Offline-first: it
ships with a structured device catalogue, so it works without any scraping.

## Features

- 🎯 **Spec-aware ranking** — every spec you enter contributes a weighted score
  (meet-or-exceed rule), so results are genuinely relevant.
- 📊 **Multiple ranked results** with a visual match-score bar and matched-spec chips.
- ⚖️ **Compare** up to 4 devices in a side-by-side table (`/api/compare`).
- 📦 **Offline-first catalogue** of popular 2024-era flagships and mid-rangers.
- 🔎 **Optional live scraper** (`app/scraper.py`) — fully isolated and defensive;
  the app never depends on it.
- 🧱 **Clean, typed, modular** code (`models`, `devices`, `matching`, `scraper`, `main`).
- 🟢 **/health** endpoint and auto-generated docs at **/docs**.

## Project structure

```
ElectroBeasts/
├─ app/
│  ├─ __init__.py
│  ├─ main.py        # FastAPI app + routes
│  ├─ models.py      # Pydantic request/response models
│  ├─ devices.py     # Offline device catalogue
│  ├─ matching.py    # Weighted spec-ranking engine
│  └─ scraper.py     # Optional best-effort nanoreview scraper
├─ static/
│  └─ index.html     # Frontend
├─ backend.py        # Entrypoint (python backend.py)
├─ requirements.txt
├─ render.yaml       # Render deploy config
└─ README.md
```

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# or: python backend.py
```

Then open http://localhost:8000 (or the port you set via `$PORT`).

## API

| Method | Path                 | Description                              |
|--------|----------------------|------------------------------------------|
| GET    | `/`                  | Frontend                                 |
| GET    | `/health`            | Health check                             |
| GET    | `/api/devices`       | Full catalogue                           |
| POST   | `/api/search-devices`| Rank devices by the specs you provide    |
| POST   | `/api/compare`       | Compare up to 4 devices by name          |
| GET    | `/docs`              | Interactive OpenAPI docs                 |

### Example

```bash
curl -X POST localhost:8000/api/search-devices \
  -H 'Content-Type: application/json' \
  -d '{"brand":"Samsung","ram":"12","battery":"5000","limit":3}'
```

## Deploy (Render)

`render.yaml` is preconfigured. Push to GitHub, create a new Web Service from the
repo, and Render binds to `$PORT` automatically.

## What changed from v1

- Fixed a deploy-blocking bug: the server never actually started (`backend.py`
  defined routes but never launched uvicorn / ignored `$PORT`).
- Specs are now actually used for ranking (v1 only matched on brand).
- Removed unused dependencies (`flask`, `numpy`, `pandas`).
- Removed the duplicate `electrobeasts_index.html`.
- Added comparison, health check, typed models, logging, CORS and docs.
