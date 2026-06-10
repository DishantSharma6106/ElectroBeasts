"""Pydantic models for requests and responses."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class DeviceQuery(BaseModel):
    """Specs the user is hunting for. Every field is optional.

    Numeric fields are accepted as free text (e.g. "12GB", "120 Hz") and parsed
    leniently, so the frontend can stay simple.
    """

    brand: str = ""
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
    limit: int = Field(default=5, ge=1, le=20)


class Device(BaseModel):
    """A single device with structured, comparable specs."""

    name: str
    brand: str
    price_usd: int
    processor: str
    gpu: str
    ram_gb: int
    storage_gb: int
    refresh_rate_hz: int
    antutu: int
    geekbench: int
    camera_mp: int
    brightness_nits: int
    battery_mah: int
    image_url: str = ""


class ScoredDevice(BaseModel):
    """A device paired with how well it matches the query."""

    device: Device
    match_score: float = Field(ge=0, le=100)
    matched_on: List[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    count: int
    query_used: str
    results: List[ScoredDevice]


class CompareRequest(BaseModel):
    names: List[str] = Field(min_length=1, max_length=4)


class CompareResponse(BaseModel):
    devices: List[Device]
    not_found: List[str] = Field(default_factory=list)
