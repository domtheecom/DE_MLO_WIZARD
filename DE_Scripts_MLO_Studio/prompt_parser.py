import re

DEFAULT_TYPE = "fire_station"


def _extract_int(pattern: str, text: str, default: int) -> int:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if match:
        try:
            value = int(match.group(1))
            return max(value, 0)
        except ValueError:
            return default
    return default


def parse_prompt(prompt: str) -> dict:
    prompt = prompt or ""
    prompt_lower = prompt.lower()

    mlo_type = DEFAULT_TYPE
    for candidate in ["fire station", "fire_station", "firestation", "station"]:
        if candidate in prompt_lower:
            mlo_type = DEFAULT_TYPE
            break

    floors = _extract_int(r"(\d+)\s*floor", prompt_lower, 1)
    if "two floor" in prompt_lower or "2 floor" in prompt_lower:
        floors = max(floors, 2)

    garage_bays = _extract_int(r"(\d+)\s*garage", prompt_lower, 0)
    garage_bays = max(garage_bays, _extract_int(r"(\d+)\s*bay", prompt_lower, 0))

    offices = _extract_int(r"(\d+)\s*office", prompt_lower, 0)
    dorms = _extract_int(r"(\d+)\s*dorm", prompt_lower, 0)

    return {
        "type": mlo_type,
        "floors": max(floors, 1),
        "garage_bays": max(garage_bays, 0),
        "offices": max(offices, 0),
        "dorms": max(dorms, 0),
        "resource_name": f"de_scripts_mlo_{mlo_type}",
    }


__all__ = ["parse_prompt"]
