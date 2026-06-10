"""ElectroBeasts FastAPI application."""
from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .devices import DEVICE_BY_NAME, DEVICES
from .matching import rank_devices
from .models import (
    CompareRequest,
    CompareResponse,
    Device,
    DeviceQuery,
    SearchResponse,
)
from .scraper import fetch_live_device

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("electrobeasts")

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="ElectroBeasts",
    version="2.0.0",
    description="Find the beast in electronics: rank phones by the specs you care about.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def root() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "devices": len(DEVICES)}


@app.get("/api/devices", response_model=list[Device])
async def list_devices() -> list[Device]:
    return DEVICES


@app.post("/api/search-devices", response_model=SearchResponse)
async def search_devices(query: DeviceQuery) -> SearchResponse:
    result = rank_devices(query)
    logger.info("search query_used=%r -> %d results", result.query_used, result.count)
    return result


@app.post("/api/compare", response_model=CompareResponse)
async def compare(request: CompareRequest) -> CompareResponse:
    found: list[Device] = []
    not_found: list[str] = []
    for name in request.names:
        device = DEVICE_BY_NAME.get(name.strip().lower())
        if device:
            found.append(device)
        else:
            not_found.append(name)
    if not found:
        raise HTTPException(status_code=404, detail="None of the requested devices were found")
    return CompareResponse(devices=found, not_found=not_found)


@app.post("/api/import-device", response_model=Device)
async def import_device(brand: str, model: str) -> Device:
    """Scrape a device from NanoReview and insert it into our local catalogue."""
    brand_clean = brand.strip()
    model_clean = model.strip()
    full_name = f"{brand_clean} {model_clean}".lower()
    
    # Check if device already exists in catalogue
    device = DEVICE_BY_NAME.get(full_name)
    if device:
        logger.info("Device %r already exists in catalogue", device.name)
        return device
        
    # Fetch live device
    scraped = fetch_live_device(brand_clean, model_clean)
    if not scraped:
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch or parse device '{brand_clean} {model_clean}' from NanoReview"
        )
        
    # Append to local catalogue list
    DEVICES.append(scraped)
    
    # Update lookup maps
    DEVICE_BY_NAME[scraped.name.lower()] = scraped
    DEVICE_BY_NAME[full_name] = scraped
    
    logger.info("Imported device %r successfully from NanoReview", scraped.name)
    return scraped

