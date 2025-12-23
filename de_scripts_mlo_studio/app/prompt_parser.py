from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class ParsedPrompt:
    raw_prompt: str
    building_type: str = "general"
    floors: int = 1
    bays: int = 0
    key_rooms: List[str] = field(default_factory=list)
    exterior_features: List[str] = field(default_factory=list)
    style_keywords: List[str] = field(default_factory=list)


ROOM_KEYWORDS = {
    "dorm": ["dorm", "sleep", "bunks"],
    "office": ["office", "admin"],
    "dispatch": ["dispatch", "communications", "radio"],
    "kitchen": ["kitchen", "mess"],
    "gym": ["gym", "fitness"],
    "turnout": ["turnout", "gear", "locker"],
    "classroom": ["classroom", "training"],
    "bathroom": ["bathroom", "restroom", "washroom"],
    "garage": ["garage", "bay"],
}

EXTERIOR_KEYWORDS = {
    "flag_area": ["flag", "flagpole"],
    "watch_tower": ["watch tower", "tower"],
    "apron": ["apron", "drive", "parking"],
}

STYLE_KEYWORDS = [
    "modern",
    "industrial",
    "coastal",
    "classic",
    "minimal",
    "rustic",
    "art deco",
    "miami",
]

BUILDING_TYPES = {
    "fire_station": ["fire station", "firehouse", "fire rescue"],
    "hospital": ["hospital", "medical"],
    "office": ["office", "dispatch"],
    "police": ["police", "sheriff"],
}


def _match_keywords(prompt: str, mapping: dict[str, list[str]]) -> list[str]:
    matches = []
    for key, phrases in mapping.items():
        for phrase in phrases:
            if phrase in prompt:
                matches.append(key)
                break
    return matches


def parse_prompt(prompt: str) -> ParsedPrompt:
    safe_prompt = prompt.lower().strip()
    if not safe_prompt:
        return ParsedPrompt(raw_prompt=prompt, building_type="general")

    building_type = "general"
    for b_type, phrases in BUILDING_TYPES.items():
        if any(phrase in safe_prompt for phrase in phrases):
            building_type = b_type
            break

    floors_match = re.search(r"(\d+)\s*(floor|story|storey)", safe_prompt)
    floors = int(floors_match.group(1)) if floors_match else 1

    bays_match = re.search(r"(\d+)\s*(bay|bays)", safe_prompt)
    bays = int(bays_match.group(1)) if bays_match else 0

    key_rooms = _match_keywords(safe_prompt, ROOM_KEYWORDS)
    exterior = _match_keywords(safe_prompt, EXTERIOR_KEYWORDS)

    styles = [keyword for keyword in STYLE_KEYWORDS if keyword in safe_prompt]

    if not key_rooms:
        if building_type == "fire_station":
            key_rooms = ["garage", "dispatch", "kitchen", "bathroom", "turnout"]
        elif building_type == "hospital":
            key_rooms = ["office", "bathroom", "classroom"]
        else:
            key_rooms = ["office", "bathroom"]

    return ParsedPrompt(
        raw_prompt=prompt,
        building_type=building_type,
        floors=max(floors, 1),
        bays=max(bays, 0),
        key_rooms=key_rooms,
        exterior_features=exterior,
        style_keywords=styles,
    )
