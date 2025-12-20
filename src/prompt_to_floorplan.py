<<<<<<< codex/build-mlo-ai-builder-repo-for-fivem-ihzia0
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
    p.add_argument("--props-manifest", required=False)
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


def props_for_room(room_name: str):
    base = {
        "kitchen": ["counter", "fridge", "table"],
        "dayroom": ["couch", "tv", "table"],
        "watch": ["desk", "chair", "monitor"],
        "gear_lockers": ["locker", "bench"],
        "bunks": ["bed", "locker"],
        "gym": ["bench_press", "rack"],
        "training": ["table", "chair", "projector"],
        "admin_office": ["desk", "chair", "computer"],
        "chief_office": ["desk", "chair", "bookcase"],
    }
    for key, props in base.items():
        if key in room_name:
            return props
    return []


def write_props_manifest(path: Path, data: dict):
    placeholders = []
    for room in data.get("rooms", []):
        for idx, hint in enumerate(props_for_room(room["name"]), start=1):
            placeholders.append({
                "name": f"PROP_{room['name']}_{idx}",
                "room": room["name"],
                "suggested_keywords": [hint],
            })
    manifest = {"placeholders": placeholders}
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


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
    if args.props_manifest and not args.no_props:
        write_props_manifest(Path(args.props_manifest), data)
=======
#!/usr/bin/env python3
"""Prompt to deterministic floorplan generator.

This script uses template-driven heuristics to transform a natural language prompt
into a structured JSON file describing a basic multi-floor blockout. No external
LLM calls are performed so it is fully offline and reproducible.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_WALL_THICKNESS = 0.2
DEFAULT_FLOOR_HEIGHT = 3.2


@dataclass
class Room:
    name: str
    width: float
    depth: float
    height: float
    floor: int
    type: str = "generic"


@dataclass
class Door:
    name: str
    width: float
    type: str
    floor: int


@dataclass
class Floorplan:
    metadata: Dict[str, str]
    rooms: List[Room]
    corridors: List[Dict[str, float]]
    doors: List[Door]
    stairs: List[Dict[str, float]]
    settings: Dict[str, float]


TEMPLATES = {
    "fire station": {
        "rooms": [
            ("Apparatus Bay", 14.0, 12.0, "bay"),
            ("Watch Office", 5.0, 4.0, "office"),
            ("Dormitory", 8.0, 6.0, "sleep"),
            ("Kitchen", 6.0, 5.0, "kitchen"),
            ("Dayroom", 7.0, 6.0, "lounge"),
            ("Gear Room", 6.0, 5.0, "storage"),
        ],
        "hallway_width": 3.0,
        "bay_door_width": 4.2,
    },
    "police station": {
        "rooms": [
            ("Lobby", 6.0, 5.0, "lobby"),
            ("Front Desk", 5.0, 4.0, "office"),
            ("Holding Cells", 8.0, 6.0, "cell"),
            ("Interview", 4.0, 4.0, "office"),
            ("Briefing Room", 7.0, 6.0, "meeting"),
            ("Evidence", 5.0, 4.0, "storage"),
        ],
        "hallway_width": 2.6,
        "bay_door_width": 0.0,
    },
    "hospital": {
        "rooms": [
            ("ER", 10.0, 8.0, "medical"),
            ("Waiting", 6.0, 5.0, "lobby"),
            ("Nurses", 5.0, 4.0, "office"),
            ("Exam", 4.0, 4.0, "medical"),
            ("Surgery", 7.0, 6.0, "medical"),
        ],
        "hallway_width": 2.8,
        "bay_door_width": 0.0,
    },
    "nightclub": {
        "rooms": [
            ("Main Floor", 12.0, 10.0, "lounge"),
            ("Bar", 8.0, 4.0, "bar"),
            ("DJ Booth", 3.0, 3.0, "stage"),
            ("Storage", 4.0, 4.0, "storage"),
            ("Office", 4.0, 4.0, "office"),
        ],
        "hallway_width": 2.4,
        "bay_door_width": 0.0,
    },
    "warehouse": {
        "rooms": [
            ("Warehouse Floor", 16.0, 12.0, "storage"),
            ("Office", 5.0, 4.0, "office"),
            ("Loading Dock", 8.0, 6.0, "dock"),
        ],
        "hallway_width": 2.5,
        "bay_door_width": 4.0,
    },
    "generic": {
        "rooms": [
            ("Lobby", 5.0, 4.0, "lobby"),
            ("Open Office", 10.0, 8.0, "office"),
            ("Conference", 6.0, 5.0, "meeting"),
        ],
        "hallway_width": 2.4,
        "bay_door_width": 0.0,
    },
}


BUILDING_KEYWORDS = {
    "fire": "fire station",
    "firehouse": "fire station",
    "station": "fire station",
    "police": "police station",
    "hospital": "hospital",
    "clinic": "hospital",
    "nightclub": "nightclub",
    "club": "nightclub",
    "warehouse": "warehouse",
}


def detect_template(prompt: str) -> str:
    lowered = prompt.lower()
    for keyword, template in BUILDING_KEYWORDS.items():
        if keyword in lowered:
            return template
    return "generic"


def build_rooms(template_key: str, floors: int) -> List[Room]:
    template = TEMPLATES.get(template_key, TEMPLATES["generic"])
    rooms: List[Room] = []
    for floor in range(floors):
        for name, width, depth, rtype in template["rooms"]:
            rooms.append(Room(name=name, width=width, depth=depth, height=DEFAULT_FLOOR_HEIGHT, floor=floor, type=rtype))
    return rooms


def default_corridors(floors: int, hallway_width: float) -> List[Dict[str, float]]:
    return [
        {
            "name": f"Corridor_{i+1}",
            "width": hallway_width,
            "length": 12.0,
            "floor": i,
        }
        for i in range(floors)
    ]


def default_stairs(floors: int, floor_height: float) -> List[Dict[str, float]]:
    return [
        {
            "name": f"Stair_{i}_{i+1}",
            "from_floor": i,
            "to_floor": i + 1,
            "rise": floor_height,
        }
        for i in range(max(floors - 1, 0))
    ]


def default_doors(template_key: str, floors: int, bay_width: float) -> List[Door]:
    doors: List[Door] = []
    for floor in range(floors):
        doors.append(Door(name=f"Entry_{floor}", width=1.0, type="single", floor=floor))
        doors.append(Door(name=f"Double_{floor}", width=1.8, type="double", floor=floor))
        if bay_width > 0:
            doors.append(Door(name=f"Bay_{floor}", width=bay_width, type="bay", floor=floor))
    return doors


def parse_prompt(prompt: str, floors: int, place: str) -> Floorplan:
    template_key = detect_template(prompt)
    template = TEMPLATES.get(template_key, TEMPLATES["generic"])
    rooms = build_rooms(template_key, floors)
    corridors = default_corridors(floors, template["hallway_width"])
    stairs = default_stairs(floors, DEFAULT_FLOOR_HEIGHT)
    doors = default_doors(template_key, floors, template["bay_door_width"])
    metadata = {
        "source_prompt": prompt,
        "inferred_template": template_key,
        "place": place,
        "floors": str(floors),
    }
    settings = {
        "wall_thickness": DEFAULT_WALL_THICKNESS,
        "floor_height": DEFAULT_FLOOR_HEIGHT,
        "hallway_width": template["hallway_width"],
    }
    return Floorplan(metadata=metadata, rooms=rooms, corridors=corridors, doors=doors, stairs=stairs, settings=settings)


def write_plan_markdown(plan: Floorplan, path: Path) -> None:
    lines = ["# Generated PLAN", "", f"Template: {plan.metadata['inferred_template']}", f"Floors: {plan.metadata['floors']}", ""]
    lines.append("## Rooms")
    for room in plan.rooms:
        lines.append(f"- Floor {room.floor}: {room.name} ({room.width}m x {room.depth}m, {room.type})")
    lines.append("")
    lines.append("## Doors")
    for door in plan.doors:
        lines.append(f"- Floor {door.floor}: {door.name} ({door.type}, width {door.width}m)")
    lines.append("")
    lines.append("## Corridors")
    for cor in plan.corridors:
        lines.append(f"- Floor {cor['floor']}: {cor['name']} (width {cor['width']}m, length {cor['length']}m)")
    lines.append("")
    lines.append("## Stairs")
    for stair in plan.stairs:
        lines.append(f"- {stair['name']} from floor {stair['from_floor']} to {stair['to_floor']} rise {stair['rise']}m")
    path.write_text("\n".join(lines), encoding="utf-8")


def serialize_plan(plan: Floorplan) -> Dict[str, object]:
    return {
        "metadata": plan.metadata,
        "rooms": [asdict(room) for room in plan.rooms],
        "corridors": plan.corridors,
        "doors": [asdict(door) for door in plan.doors],
        "stairs": plan.stairs,
        "settings": plan.settings,
    }


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Convert prompt to floorplan JSON")
    parser.add_argument("--prompt", required=True, help="Natural language building description")
    parser.add_argument("--out", required=True, help="Output JSON path")
    parser.add_argument("--place", default="", help="Placement hint")
    parser.add_argument("--floors", type=int, default=1, help="Number of floors")
    parser.add_argument("--plan-doc", default=None, help="Optional PLAN.md output")
    args = parser.parse_args(argv)

    plan = parse_prompt(args.prompt, args.floors, args.place)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(serialize_plan(plan), indent=2), encoding="utf-8")

    if args.plan_doc:
        write_plan_markdown(plan, Path(args.plan_doc))

    print(f"Wrote floorplan to {out_path}")
>>>>>>> main


if __name__ == "__main__":
    main()
