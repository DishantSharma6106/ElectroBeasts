from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import os
import random

app = FastAPI()

# Serve the static HTML frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

class DeviceQuery(BaseModel):
    processor: str = ""
    gpu: str = ""
    ram: str = ""
    storage: str = ""
    refresh_rate: str = ""
    antutu: str = ""
    geekbench: str = ""
    camera: str = ""
    brightness: str = ""
    battery: str = ""
    brand: str = ""

NANO_REVIEW_BASE_URL = "https://nanoreview.net/en/search?q="

# Sample device database as fallback when web scraping is blocked
SAMPLE_DEVICES = [
    {
        "name": "Samsung Galaxy S24 Ultra",
        "price": "$1,299",
        "image_url": "https://fdn2.gsmarena.com/vv/bigpic/samsung-galaxy-s24-ultra-5g-sm-s928.jpg"
    },
    {
        "name": "iPhone 15 Pro Max",
        "price": "$1,199",
        "image_url": "https://fdn2.gsmarena.com/vv/bigpic/apple-iphone-15-pro-max.jpg"
    },
    {
        "name": "Google Pixel 8 Pro",
        "price": "$999",
        "image_url": "https://fdn2.gsmarena.com/vv/bigpic/google-pixel-8-pro.jpg"
    },
    {
        "name": "OnePlus 12",
        "price": "$799",
        "image_url": "https://fdn2.gsmarena.com/vv/bigpic/oneplus-12.jpg"
    },
    {
        "name": "Xiaomi 14 Pro",
        "price": "$899",
        "image_url": "https://fdn2.gsmarena.com/vv/bigpic/xiaomi-14-pro.jpg"
    },
    {
        "name": "ASUS ROG Phone 8 Pro",
        "price": "$1,199",
        "image_url": "https://fdn2.gsmarena.com/vv/bigpic/asus-rog-phone-8-pro.jpg"
    },
]

def fetch_device_info(query):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        search_url = NANO_REVIEW_BASE_URL + query.replace(" ", "+")
        response = requests.get(search_url, headers=headers, timeout=5)
        
        # Check if we got Cloudflare challenge page
        if response.status_code != 200 or 'cf-chl' in response.text or 'cloudflare' in response.text.lower():
            return get_sample_device(query)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        device_list = soup.find_all('div', class_='device-card')
        
        if not device_list:
            return get_sample_device(query)
        
        first_device = device_list[0]
        name = first_device.find('h3').text.strip() if first_device.find('h3') else "Unknown Device"
        price_tag = first_device.find('span', class_='price')
        price = price_tag.text.strip() if price_tag else "Not available"
        img_tag = first_device.find('img')
        image_url = img_tag['src'] if img_tag and img_tag.get('src') else ""
        
        return {
            "name": name,
            "price": price,
            "image_url": image_url
        }
    except Exception as e:
        print(f"Error fetching device info: {e}")
        return get_sample_device(query)

def get_sample_device(query):
    """Return a sample device based on query keywords"""
    query_lower = query.lower()
    
    # Try to match brand keywords
    if 'samsung' in query_lower:
        return SAMPLE_DEVICES[0]
    elif 'iphone' in query_lower or 'apple' in query_lower:
        return SAMPLE_DEVICES[1]
    elif 'pixel' in query_lower or 'google' in query_lower:
        return SAMPLE_DEVICES[2]
    elif 'oneplus' in query_lower:
        return SAMPLE_DEVICES[3]
    elif 'xiaomi' in query_lower:
        return SAMPLE_DEVICES[4]
    elif 'asus' in query_lower or 'rog' in query_lower:
        return SAMPLE_DEVICES[5]
    
    # Return a random device if no match
    return random.choice(SAMPLE_DEVICES)

@app.post("/api/search-devices")
async def search_devices(data: DeviceQuery):
    # Build a smart query - prioritize brand and processor for better search results
    query_parts = []
    
    # Add brand first if provided (helps narrow down search)
    if data.brand:
        query_parts.append(data.brand)
    
    # Add processor second (important identifier)
    if data.processor:
        query_parts.append(data.processor)
    
    # Add RAM as it's a common differentiator
    if data.ram:
        query_parts.append(data.ram)
    
    # Add storage
    if data.storage:
        query_parts.append(data.storage)
    
    query = " ".join(query_parts) if query_parts else "smartphone"
    device_info = fetch_device_info(query)
    if device_info:
        return {"device": device_info}
    return {"error": "No matching device found"}
