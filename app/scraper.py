"""Robust live scraper for nanoreview.net.

Enables the application to query and parse detailed device specifications 
directly from NanoReview pages.
"""
from __future__ import annotations

import logging
import re
from typing import Optional
import requests
from bs4 import BeautifulSoup
from .models import Device

logger = logging.getLogger("electrobeasts.scraper")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

def query_to_slug(brand: str, model: str) -> str:
    """Convert brand and model names into the standard NanoReview URL slug."""
    brand_clean = brand.strip().lower()
    model_clean = model.strip().lower()
    
    # If model already starts with the brand name, don't duplicate it
    if model_clean.startswith(brand_clean):
        combined = model_clean
    else:
        combined = f"{brand_clean} {model_clean}"
        
    # Standard cleanups
    combined = combined.replace("+", "-plus")
    combined = re.sub(r"[()\[\],'\"]", "", combined)
    
    # Handle iPhone brand prefix case
    if "iphone" in combined and "apple" not in combined:
        combined = "apple-" + combined
        
    # Replace spaces and underscores with hyphens
    slug = re.sub(r"[\s_]+", "-", combined)
    slug = re.sub(r"-+", "-", slug)
    return slug

def parse_int_from_text(text: Optional[str]) -> int:
    """Parse the first integer found in a string."""
    if not text:
        return 0
    # remove commas
    text_clean = text.replace(",", "")
    match = re.search(r"\d+", text_clean)
    return int(match.group()) if match else 0

def fetch_live_device(brand: str, model: str, timeout: float = 8.0) -> Optional[Device]:
    """Fetch and parse smartphone specifications from NanoReview."""
    slug = query_to_slug(brand, model)
    url = f"https://nanoreview.net/en/phone/{slug}"
    logger.info("Scraping device page: %s", url)
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
    except requests.RequestException as exc:
        logger.error("HTTP request failed for slug %r: %s", slug, exc)
        return None
        
    if resp.status_code != 200:
        logger.warning("Scraper received status code %d for slug %r", resp.status_code, slug)
        return None
        
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Extract the formal title
    # e.g., "Samsung Galaxy S24 Ultra: specs..." -> "Samsung Galaxy S24 Ultra"
    page_title = soup.title.get_text(strip=True) if soup.title else ""
    name = page_title.split(":")[0].strip() if ":" in page_title else (brand + " " + model).title()
    
    specs = {}
    
    # 1. Parse all specification tables
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if len(cells) == 2:
                specs[cells[0].strip()] = cells[1].strip()
                
    # 2. Parse benchmark score-bars (AnTuTu, Geekbench)
    for div in soup.find_all("div", class_="score-bar"):
        name_div = div.find("div", class_="score-bar-name")
        res_span = div.find("span", class_="score-bar-result-number")
        if name_div and res_span:
            specs[name_div.get_text(strip=True)] = res_span.get_text(strip=True)
            
    # 3. Parse first camera megapixels (Main Camera)
    camera_mp = 12  # fallback default
    for tr in soup.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if len(cells) == 2 and cells[0] in ["Image resolution", "Matrix", "Megapixels"]:
            m = re.search(r"(\d+)\s*(?:MP|megapixels)", cells[1], re.IGNORECASE)
            if m:
                camera_mp = int(m.group(1))
                break
                
    # Extract structured fields with safe defaults
    price_usd = parse_int_from_text(specs.get("Launch price (MSRP)"))
    processor = specs.get("Chipset", "Unknown CPU")
    gpu = specs.get("Graphics", "Unknown GPU")
    ram_gb = parse_int_from_text(specs.get("RAM size"))
    storage_gb = parse_int_from_text(specs.get("Storage size"))
    refresh_rate_hz = parse_int_from_text(specs.get("Refresh rate"))
    brightness_nits = parse_int_from_text(specs.get("Max rated brightness"))
    battery_mah = parse_int_from_text(specs.get("Capacity"))
    
    # Parse AnTuTu Score
    antutu = 0
    for k, v in specs.items():
        if "antutu" in k.lower():
            try:
                antutu = int(v.replace(",", ""))
                break
            except ValueError:
                pass
                
    # Parse Geekbench Multi-Core Score
    geekbench = 0
    for k, v in specs.items():
        if "geekbench" in k.lower() and "multi" in k.lower():
            try:
                geekbench = int(v)
                break
            except ValueError:
                pass
                
    # Parse device image URL
    image_url = ""
    for img in soup.find_all("img"):
        src = img.get("src", "")
        if "/common/images/phone/" in src:
            image_url = "https://nanoreview.net" + src
            break
            
    # Assemble device object
    device = Device(
        name=name,
        brand=brand.title(),
        price_usd=price_usd if price_usd > 0 else 500, # default price if missing
        processor=processor,
        gpu=gpu,
        ram_gb=ram_gb if ram_gb > 0 else 8,
        storage_gb=storage_gb if storage_gb > 0 else 128,
        refresh_rate_hz=refresh_rate_hz if refresh_rate_hz > 0 else 60,
        antutu=antutu if antutu > 0 else 500000,
        geekbench=geekbench if geekbench > 0 else 3000,
        camera_mp=camera_mp,
        brightness_nits=brightness_nits if brightness_nits > 0 else 800,
        battery_mah=battery_mah if battery_mah > 0 else 4000,
        image_url=image_url
    )
    return device
