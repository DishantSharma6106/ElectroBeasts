from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Mount static folder for favicon and other assets
app.mount("/static", StaticFiles(directory="static"), name="static")

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

@app.get("/")
async def root():
    return {"message": "Server is running"}

NANO_REVIEW_BASE_URL = "https://nanoreview.net/en/search?q="

def fetch_device_info(query):
    search_url = NANO_REVIEW_BASE_URL + query.replace(" ", "+")
    response = requests.get(search_url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    device_list = soup.find_all('div', class_='device-card')
    if not device_list:
        return None
    first_device = device_list[0]
    name = first_device.find('h3').text.strip()
    price_tag = first_device.find('span', class_='price')
    price = price_tag.text.strip() if price_tag else "Not available"
    img_tag = first_device.find('img')
    image_url = img_tag['src'] if img_tag else ""
    return {
        "name": name,
        "price": price,
        "image_url": image_url
    }

@app.post("/api/search-devices")
async def search_devices(data: DeviceQuery):
    query = f"{data.processor} {data.gpu} {data.ram} {data.storage} {data.refresh_rate} {data.antutu} {data.geekbench} {data.camera} {data.brightness} {data.battery} {data.brand}"
    device_info = fetch_device_info(query)
    if device_info:
        return {"device": device_info}
    return {"error": "No matching device found"}
