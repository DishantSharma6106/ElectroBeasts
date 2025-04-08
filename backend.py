from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

from flask import Flask, request, jsonify import requests from bs4 import BeautifulSoup

app = Flask(name)

NANO_REVIEW_BASE_URL = "https://nanoreview.net/en/search?q="

def fetch_device_info(query): search_url = NANO_REVIEW_BASE_URL + query.replace(" ", "+") response = requests.get(search_url) if response.status_code != 200: return None

soup = BeautifulSoup(response.text, 'html.parser')
device_list = soup.find_all('div', class_='device-card')
if not device_list:
    return None

first_device = device_list[0]
name = first_device.find('h3').text.strip()
price = first_device.find('span', class_='price').text.strip() if first_device.find('span', class_='price') else "Not available"
image_url = first_device.find('img')['src'] if first_device.find('img') else ""

return {
    "name": name,
    "price": price,
    "image_url": image_url
}

@app.route('/search_device', methods=['POST']) def search_device(): data = request.json query = f"{data.get('processor', '')} {data.get('gpu', '')} {data.get('ram', '')} {data.get('storage', '')} {data.get('refresh_rate', '')} {data.get('antutu', '')} {data.get('geekbench', '')} {data.get('camera', '')} {data.get('brightness', '')} {data.get('battery', '')} {data.get('brand', '')}"

device_info = fetch_device_info(query)
if device_info:
    return jsonify(device_info)
else:
    return jsonify({"error": "No matching device found"}), 404

if name == 'main': app.run(debug=True)
