import argparse
import json
import os
from pathlib import Path
from textwrap import dedent

DEFAULTS = {
    "floor_height": 3.2,
    "wall_thickness": 0.2,
    "corridor_width": 2.6,
    "door_width": 1.0,
    "double_door_width": 1.8,
    "bay_opening_width": 4.0,
    "bay_opening_height": 4.5,
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--plan-doc", required=True)
    p.add_argument("--mlo-meta", required=False)
    p.add_argument("--place", default="")
    p.add_argument("--floors", type=int, default=1)
    p.add_argument("--full-mlo", action="store_true")
    p.add_argument("--no-props", action="store_true")
    p.add_argument("--no-portals", action="store_true")
    return p.parse_args()


def build_station51(floors: int):
    bays = []
    for i in range(4):
        bays.append({"name": f"bay_{i+1}", "size": [18.0, 14.0], "floor": 0})
    rooms = [
        {"name": "apparatus_room", "size": [20.0, 25.0], "floor": 0},
        {"name": "gear_lockers", "size": [8.0, 8.0], "floor": 0},
        {"name": "watch", "size": [6.0, 6.0], "floor": 0},
        {"name": "kitchen", "size": [10.0, 8.0], "floor": 0},
        {"name": "dayroom", "size": [12.0, 10.0], "floor": 0},
        {"name": "bathroom_0", "size": [5.0, 5.0], "floor": 0},
        {"name": "storage_0", "size": [6.0, 6.0], "floor": 0},
        {"name": "mechanical", "size": [6.0, 6.0], "floor": 0},
    ]
    if floors > 1:
        rooms.extend([
            {"name": "admin_office", "size": [7.0, 6.0], "floor": 1},
            {"name": "chief_office", "size": [7.0, 6.0], "floor": 1},
            {"name": "bunks", "size": [14.0, 10.0], "floor": 1},
            {"name": "bathroom_1", "size": [6.0, 5.0], "floor": 1},
            {"name": "gym", "size": [8.0, 8.0], "floor": 1},
            {"name": "training", "size": [10.0, 8.0], "floor": 1},
            {"name": "storage_1", "size": [6.0, 6.0], "floor": 1},
        ])
    corridors = []
    for floor in range(floors):
        corridors.append({"name": f"corridor_f{floor}", "width": DEFAULTS["corridor_width"], "length": 24.0, "floor": floor})
    stairs = [{"name": "stair_core", "from": 0, "to": min(1, floors-1), "size": [4.0, 6.0]}] if floors > 1 else []
    doors = []
    for room in rooms:
        doors.append({"from": room["name"], "to": f"corridor_f{room['floor']}", "width": DEFAULTS["door_width"], "floor": room["floor"]})
    for bay in bays:
        doors.append({"from": bay["name"], "to": "apparatus_room", "width": DEFAULTS["double_door_width"], "floor": bay["floor"]})
    windows = []
    for room in rooms:
        if room["name"] in {"admin_office", "chief_office", "dayroom", "watch"}:
            windows.append({"room": room["name"], "width": 1.5, "height": 1.2, "floor": room["floor"]})
    bay_openings = []
    for bay in bays:
        bay_openings.append({
            "name": bay["name"],
            "width": DEFAULTS["bay_opening_width"],
            "height": DEFAULTS["bay_opening_height"],
            "floor": bay["floor"],
        })
    return {
        "defaults": DEFAULTS,
        "floors": floors,
        "bays": bays,
        "rooms": rooms,
        "corridors": corridors,
        "stairs": stairs,
        "doors": doors,
        "windows": windows,
        "bay_openings": bay_openings,
        "meta": {
            "interior_name": "station51",
            "place": "",
            "portal_rules": "room-corridor and bays to apparatus",
            "entity_sets": ["station51_main", "station51_floor0", "station51_floor1"],
        },
    }


def build_generic(prompt: str, floors: int):
    return build_station51(floors)


def write_plan(plan_path: Path, data: dict):
    lines = ["# PLAN", "", f"Floors: {data['floors']}", ""]
    for room in data["rooms"]:
        lines.append(f"- {room['name']} (floor {room['floor']}): {room['size'][0]}m x {room['size'][1]}m")
    for bay in data.get("bays", []):
        lines.append(f"- Bay {bay['name']} (floor {bay['floor']}): {bay['size'][0]}m x {bay['size'][1]}m")
    lines.append("")
    lines.append("Connectivity via corridors and doors. Bays link to apparatus room.")
    plan_path.write_text("\n".join(lines), encoding="utf-8")


def write_mlo_meta(meta_path: Path, data: dict):
    meta = {
        "interior": data.get("meta", {}).get("interior_name", "interior"),
        "entity_sets": data.get("meta", {}).get("entity_sets", []),
        "portal_rules": data.get("meta", {}).get("portal_rules", ""),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def main():
    args = parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_lower = args.prompt.lower()
    if "fire" in prompt_lower and "station" in prompt_lower:
        data = build_station51(args.floors)
    else:
        data = build_generic(args.prompt, args.floors)
    data["meta"]["place"] = args.place
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    write_plan(Path(args.plan_doc), data)
    if args.mlo_meta:
        write_mlo_meta(Path(args.mlo_meta), data)


if __name__ == "__main__":
    main()
