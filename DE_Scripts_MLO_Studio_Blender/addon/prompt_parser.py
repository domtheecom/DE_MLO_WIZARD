import re


ROOM_KEYWORDS = {
    "chief office": "chief_office",
    "dispatch": "dispatch",
    "kitchen": "kitchen",
    "dining": "dining",
    "gym": "gym",
    "workout": "gym",
    "turnout": "turnout",
    "classroom": "classroom",
    "meeting": "classroom",
    "wash bay": "wash_bay",
    "dorms": "dorms",
    "dorm": "dorms",
    "captain quarters": "captain_quarters",
    "lt quarters": "lt_quarters",
    "lobby": "lobby",
    "fire pole": "fire_pole",
    "watch tower": "watch_tower",
    "apron": "apron",
    "training area": "training_area",
    "flag pole": "flag_pole",
}


PRESET_DEFAULTS = {
    "FIRE_STATION": ["lobby", "dispatch", "dorms", "kitchen", "wash_bay"],
    "POLICE_STATION": ["lobby", "dispatch", "classroom", "chief_office"],
    "HOSPITAL": ["lobby", "dorms", "training_area"],
    "OFFICE": ["lobby", "classroom", "chief_office"],
    "GENERIC": ["lobby"],
}


EXTERIOR_KEYWORDS = {
    "watch tower": "watch_tower",
    "apron": "apron",
    "flag pole": "flag_pole",
}


STYLE_KEYWORDS = ["modern", "industrial", "brick", "stucco", "metal", "concrete"]


def _find_number(text, keyword):
    match = re.search(r"(\d+)\s+" + re.escape(keyword), text)
    if match:
        return int(match.group(1))
    return None


def _extract_rooms(text):
    rooms = []
    for phrase, room_name in ROOM_KEYWORDS.items():
        if phrase in text:
            rooms.append(room_name)
    return sorted(set(rooms))


def _extract_exterior(text):
    exterior = []
    for phrase, name in EXTERIOR_KEYWORDS.items():
        if phrase in text:
            exterior.append(name)
    return sorted(set(exterior))


def _extract_style(text):
    styles = []
    for token in STYLE_KEYWORDS:
        if token in text:
            styles.append(token)
    return sorted(set(styles))


def parse_prompt(text, preset):
    data = {
        "building_type": preset,
        "floors": 1,
        "bays": 0,
        "rooms": [],
        "exterior": [],
        "style": [],
    }
    try:
        raw = text or ""
        lowered = raw.lower()
        floors = _find_number(lowered, "floors") or _find_number(lowered, "floor")
        bays = _find_number(lowered, "bays") or _find_number(lowered, "bay")
        if floors:
            data["floors"] = max(1, floors)
        if bays is not None:
            data["bays"] = max(0, bays)

        rooms = _extract_rooms(lowered)
        if rooms:
            data["rooms"] = rooms
        else:
            data["rooms"] = PRESET_DEFAULTS.get(preset, ["lobby"]).copy()

        data["exterior"] = _extract_exterior(lowered)
        data["style"] = _extract_style(lowered)
    except Exception:
        data["rooms"] = PRESET_DEFAULTS.get(preset, ["lobby"]).copy()
    return data
