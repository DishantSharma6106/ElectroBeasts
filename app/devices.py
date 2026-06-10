"""Offline device catalogue.

The original app depended entirely on scraping nanoreview.net, which is behind
Cloudflare and almost always failed, silently returning a random sample. This
local, structured catalogue makes search deterministic, fast and offline-first.
The (optional) live scraper can still enrich results when reachable.
"""
from __future__ import annotations

from typing import List

from .models import Device

_GSM = "https://fdn2.gsmarena.com/vv/bigpic/"

DEVICES: List[Device] = [
    Device(name="Samsung Galaxy S24 Ultra", brand="Samsung", price_usd=1299,
           processor="Snapdragon 8 Gen 3", gpu="Adreno 750", ram_gb=12, storage_gb=256,
           refresh_rate_hz=120, antutu=2000000, geekbench=7200, camera_mp=200,
           brightness_nits=2600, battery_mah=5000,
           image_url=_GSM + "samsung-galaxy-s24-ultra-5g-sm-s928.jpg"),
    Device(name="iPhone 15 Pro Max", brand="Apple", price_usd=1199,
           processor="Apple A17 Pro", gpu="Apple GPU (6-core)", ram_gb=8, storage_gb=256,
           refresh_rate_hz=120, antutu=1600000, geekbench=7300, camera_mp=48,
           brightness_nits=2000, battery_mah=4441,
           image_url=_GSM + "apple-iphone-15-pro-max.jpg"),
    Device(name="Google Pixel 8 Pro", brand="Google", price_usd=999,
           processor="Google Tensor G3", gpu="Immortalis-G715", ram_gb=12, storage_gb=128,
           refresh_rate_hz=120, antutu=1050000, geekbench=4600, camera_mp=50,
           brightness_nits=2400, battery_mah=5050,
           image_url=_GSM + "google-pixel-8-pro.jpg"),
    Device(name="OnePlus 12", brand="OnePlus", price_usd=799,
           processor="Snapdragon 8 Gen 3", gpu="Adreno 750", ram_gb=16, storage_gb=256,
           refresh_rate_hz=120, antutu=2100000, geekbench=7000, camera_mp=50,
           brightness_nits=4500, battery_mah=5400,
           image_url=_GSM + "oneplus-12.jpg"),
    Device(name="Xiaomi 14 Pro", brand="Xiaomi", price_usd=899,
           processor="Snapdragon 8 Gen 3", gpu="Adreno 750", ram_gb=12, storage_gb=256,
           refresh_rate_hz=120, antutu=2050000, geekbench=7100, camera_mp=50,
           brightness_nits=3000, battery_mah=4880,
           image_url=_GSM + "xiaomi-14-pro.jpg"),
    Device(name="ASUS ROG Phone 8 Pro", brand="ASUS", price_usd=1199,
           processor="Snapdragon 8 Gen 3", gpu="Adreno 750", ram_gb=24, storage_gb=1024,
           refresh_rate_hz=165, antutu=2150000, geekbench=7250, camera_mp=50,
           brightness_nits=2500, battery_mah=5500,
           image_url=_GSM + "asus-rog-phone-8-pro.jpg"),
    Device(name="Vivo X100 Pro", brand="Vivo", price_usd=999,
           processor="Dimensity 9300", gpu="Immortalis-G720", ram_gb=16, storage_gb=512,
           refresh_rate_hz=120, antutu=2200000, geekbench=7400, camera_mp=50,
           brightness_nits=3000, battery_mah=5400,
           image_url=_GSM + "vivo-x100-pro.jpg"),
    Device(name="Nothing Phone (2)", brand="Nothing", price_usd=599,
           processor="Snapdragon 8+ Gen 1", gpu="Adreno 730", ram_gb=12, storage_gb=256,
           refresh_rate_hz=120, antutu=1300000, geekbench=5200, camera_mp=50,
           brightness_nits=1600, battery_mah=4700,
           image_url=_GSM + "nothing-phone-2.jpg"),
    Device(name="iPhone 15", brand="Apple", price_usd=799,
           processor="Apple A16 Bionic", gpu="Apple GPU (5-core)", ram_gb=6, storage_gb=128,
           refresh_rate_hz=60, antutu=1300000, geekbench=6500, camera_mp=48,
           brightness_nits=2000, battery_mah=3349,
           image_url=_GSM + "apple-iphone-15.jpg"),
    Device(name="Samsung Galaxy A55", brand="Samsung", price_usd=449,
           processor="Exynos 1480", gpu="Xclipse 530", ram_gb=8, storage_gb=128,
           refresh_rate_hz=120, antutu=700000, geekbench=4200, camera_mp=50,
           brightness_nits=1000, battery_mah=5000,
           image_url=_GSM + "samsung-galaxy-a55.jpg"),
    Device(name="Redmi Note 13 Pro+", brand="Xiaomi", price_usd=399,
           processor="Dimensity 7200 Ultra", gpu="Mali-G610", ram_gb=12, storage_gb=256,
           refresh_rate_hz=120, antutu=750000, geekbench=3900, camera_mp=200,
           brightness_nits=1300, battery_mah=5000,
           image_url=_GSM + "xiaomi-redmi-note-13-pro-plus.jpg"),
    Device(name="Motorola Edge 50 Pro", brand="Motorola", price_usd=599,
           processor="Snapdragon 7 Gen 3", gpu="Adreno 720", ram_gb=12, storage_gb=256,
           refresh_rate_hz=144, antutu=850000, geekbench=4000, camera_mp=50,
           brightness_nits=2000, battery_mah=4500,
           image_url=_GSM + "motorola-edge-50-pro.jpg"),
]

DEVICE_BY_NAME = {d.name.lower(): d for d in DEVICES}
