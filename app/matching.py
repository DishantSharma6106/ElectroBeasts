"""Spec-aware ranking engine.

The original backend ignored every spec except brand. This module turns the
user's desired specs into a weighted match score so results are actually
relevant. Numeric fields use a "meet-or-exceed" rule (you're hunting beasts, so
over-spec'd devices are not penalised).
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple

from .devices import DEVICES
from .models import Device, DeviceQuery, ScoredDevice, SearchResponse

# field on DeviceQuery -> (attribute on Device, weight)
NUMERIC_SPECS = {
    "ram": ("ram_gb", 1.0),
    "storage": ("storage_gb", 0.8),
    "refresh_rate": ("refresh_rate_hz", 0.8),
    "antutu": ("antutu", 1.2),
    "geekbench": ("geekbench", 1.0),
    "camera": ("camera_mp", 0.8),
    "brightness": ("brightness_nits", 0.6),
    "battery": ("battery_mah", 1.0),
}

TEXT_SPECS = {
    "brand": ("brand", 2.0),
    "processor": ("processor", 1.5),
    "gpu": ("gpu", 1.0),
}


def _to_number(value: str) -> Optional[float]:
    """Extract the first number from free text like '12GB' or '1,200 nits'."""
    if not value:
        return None
    cleaned = value.replace(",", "")
    match = re.search(r"\d+(?:\.\d+)?", cleaned)
    return float(match.group()) if match else None


def _score_device(device: Device, query: DeviceQuery) -> Tuple[Optional[float], List[str]]:
    total_weight = 0.0
    earned = 0.0
    matched: List[str] = []

    for field, (attr, weight) in TEXT_SPECS.items():
        wanted = getattr(query, field).strip().lower()
        if not wanted:
            continue
        total_weight += weight
        if wanted in getattr(device, attr).lower():
            earned += weight
            matched.append(field)

    for field, (attr, weight) in NUMERIC_SPECS.items():
        wanted = _to_number(getattr(query, field))
        if not wanted or wanted <= 0:
            continue
        total_weight += weight
        have = float(getattr(device, attr))
        ratio = have / wanted
        spec_score = 1.0 if ratio >= 1 else max(0.0, ratio)
        earned += weight * spec_score
        if spec_score >= 0.8:
            matched.append(field)

    if total_weight == 0:
        return None, matched
    return round(earned / total_weight * 100, 1), matched


def _describe(query: DeviceQuery) -> str:
    parts = []
    for field in list(TEXT_SPECS) + list(NUMERIC_SPECS):
        value = getattr(query, field).strip()
        if value:
            parts.append(f"{field.replace('_', ' ')}={value}")
    return ", ".join(parts) if parts else "no criteria"


def rank_devices(query: DeviceQuery) -> SearchResponse:
    scored = [(*_score_device(d, query), d) for d in DEVICES]
    # scored items are (score, matched, device)

    if all(score is None for score, _, _ in scored):
        # No criteria given: surface the most powerful beasts.
        ranked = sorted(DEVICES, key=lambda d: d.antutu, reverse=True)
        results = [
            ScoredDevice(device=d, match_score=100.0, matched_on=["top performance"])
            for d in ranked[: query.limit]
        ]
        return SearchResponse(count=len(results), query_used="Top beasts by raw performance", results=results)

    scored.sort(key=lambda item: (item[0] if item[0] is not None else -1.0), reverse=True)
    results = [
        ScoredDevice(device=device, match_score=score or 0.0, matched_on=matched)
        for score, matched, device in scored[: query.limit]
    ]
    return SearchResponse(count=len(results), query_used=_describe(query), results=results)
