import re
from typing import Dict


def _extract_count(pattern: str, text: str, default: int) -> int:
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return default


def parse_prompt(prompt: str) -> Dict[str, int | str]:
    prompt_lower = prompt.lower()
    building_type = "fire station"
    if "hospital" in prompt_lower:
        building_type = "hospital"
    if "police" in prompt_lower:
        building_type = "police station"

    floors = _extract_count(r"(\d+)\s+floors?", prompt_lower, 2)
    dorms = _extract_count(r"(\d+)\s+dorms?", prompt_lower, 2)
    offices = _extract_count(r"(\d+)\s+offices?", prompt_lower, 3)
    garage_bays = _extract_count(r"(\d+)\s+garage\s+bays?", prompt_lower, 2)

    resource_name = re.sub(r"[^a-z0-9_-]+", "_", building_type.strip().lower())
    resource_name = f"promptmlo_{resource_name}"

    return {
        "building_type": building_type,
        "floors": max(floors, 1),
        "dorms": max(dorms, 0),
        "offices": max(offices, 0),
        "garage_bays": max(garage_bays, 0),
        "resource_name": resource_name,
    }
