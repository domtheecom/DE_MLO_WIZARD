<<<<<<< codex/build-mlo-ai-builder-repo-for-fivem-ihzia0
import argparse
import json
import sys

import bpy
import math

DEFAULTS = {
    "floor_height": 3.2,
    "wall_thickness": 0.2,
    "corridor_width": 2.6,
    "door_width": 1.0,
    "double_door_width": 1.8,
    "bay_opening_width": 4.0,
    "bay_opening_height": 4.5,
}


def ensure_collection(name: str):
    if name in bpy.data.collections:
        coll = bpy.data.collections[name]
    else:
        coll = bpy.data.collections.new(name)
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    return coll


def safe_unlink(obj, coll):
    try:
        if coll and coll.objects.get(obj.name):
            coll.objects.unlink(obj)
    except Exception:
        pass


def clear_scene():
    keep = {"GEO", "COLLISION", "HELPERS", "MLO"}
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for name in keep:
        ensure_collection(name)


def create_box(name, size, location, collection):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    collection.objects.link(obj)
    for coll in list(obj.users_collection):
        if coll != collection:
            safe_unlink(obj, coll)
    return obj


def build_room(room, defaults, geo_coll):
    x, y = room["size"]
    thickness = defaults["wall_thickness"]
    height = defaults["floor_height"]
    base_z = room["floor"] * defaults["floor_height"]
    floor_obj = create_box(f"FLOOR_{room['name']}_{room['floor']}", (x, y, thickness), (0, 0, base_z - thickness / 2), geo_coll)
    ceiling_obj = create_box(f"CEIL_{room['name']}_{room['floor']}", (x, y, thickness), (0, 0, base_z + height + thickness / 2), geo_coll)
    walls = []
    walls.append(create_box(f"WALL_{room['name']}_N_{room['floor']}", (x, thickness, height), (0, y / 2, base_z + height / 2), geo_coll))
    walls.append(create_box(f"WALL_{room['name']}_S_{room['floor']}", (x, thickness, height), (0, -y / 2, base_z + height / 2), geo_coll))
    walls.append(create_box(f"WALL_{room['name']}_E_{room['floor']}", (thickness, y, height), (x / 2, 0, base_z + height / 2), geo_coll))
    walls.append(create_box(f"WALL_{room['name']}_W_{room['floor']}", (thickness, y, height), (-x / 2, 0, base_z + height / 2), geo_coll))
    return floor_obj, ceiling_obj, walls


def build_corridor(corr, defaults, geo_coll):
    length = corr.get("length", 10.0)
    width = corr.get("width", defaults["corridor_width"])
    height = defaults["floor_height"]
    base_z = corr["floor"] * defaults["floor_height"]
    floor_obj = create_box(f"CORRIDOR_FLOOR_{corr['name']}", (length, width, defaults["wall_thickness"]), (0, 0, base_z - defaults["wall_thickness"] / 2), geo_coll)
    ceiling_obj = create_box(f"CORRIDOR_CEIL_{corr['name']}", (length, width, defaults["wall_thickness"]), (0, 0, base_z + height + defaults["wall_thickness"] / 2), geo_coll)
    walls = []
    walls.append(create_box(f"CORRIDOR_WALL_N_{corr['name']}", (length, defaults["wall_thickness"], height), (0, width / 2, base_z + height / 2), geo_coll))
    walls.append(create_box(f"CORRIDOR_WALL_S_{corr['name']}", (length, defaults["wall_thickness"], height), (0, -width / 2, base_z + height / 2), geo_coll))
    walls.append(create_box(f"CORRIDOR_WALL_E_{corr['name']}", (defaults["wall_thickness"], width, height), (length / 2, 0, base_z + height / 2), geo_coll))
    walls.append(create_box(f"CORRIDOR_WALL_W_{corr['name']}", (defaults["wall_thickness"], width, height), (-length / 2, 0, base_z + height / 2), geo_coll))
    return floor_obj, ceiling_obj, walls


def build_stair(stair, defaults, geo_coll):
    base_z = stair.get("from", 0) * defaults["floor_height"]
    height = (stair.get("to", 0) - stair.get("from", 0)) * defaults["floor_height"]
    size = (stair["size"][0], stair["size"][1], height)
    return create_box(f"STAIR_{stair['name']}", size, (0, 0, base_z + height / 2), geo_coll)


def add_cutters(data, defaults, helpers_coll):
    cutters = []
    for door in data.get("doors", []):
        z = door["floor"] * defaults["floor_height"] + 1.0
        width = door.get("width", defaults["door_width"])
        cutter = create_box(f"DOOR_{door['from']}_{door['to']}_{door['floor']}", (width, defaults["wall_thickness"] * 1.5, 2.1), (0, 0, z), helpers_coll)
        cutter.display_type = 'WIRE'
        cutters.append(cutter)
    for win in data.get("windows", []):
        z = win["floor"] * defaults["floor_height"] + 1.5
        cutter = create_box(f"WIN_{win['room']}_{win['floor']}", (win.get("width", 1.5), defaults["wall_thickness"] * 1.2, win.get("height", 1.2)), (0, 0, z), helpers_coll)
        cutter.display_type = 'WIRE'
        cutters.append(cutter)
    for bay in data.get("bay_openings", []):
        z = bay["floor"] * defaults["floor_height"] + bay.get("height", defaults["bay_opening_height"]) / 2
        cutter = create_box(f"BAYOPEN_{bay['name']}_{bay['floor']}", (bay.get("width", defaults["bay_opening_width"]), defaults["wall_thickness"] * 2, bay.get("height", defaults["bay_opening_height"])), (0, 0, z), helpers_coll)
        cutter.display_type = 'WIRE'
        cutters.append(cutter)
    return cutters


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--floorplan", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--blend", required=True)
    parser.add_argument("--full-mlo", action="store_true")
    parser.add_argument("--no-props", action="store_true")
    parser.add_argument("--no-portals", action="store_true")
    if "--" in sys.argv:
        args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    else:
        args = parser.parse_args()

    with open(args.floorplan, "r", encoding="utf-8") as f:
        data = json.load(f)

    geo_coll = ensure_collection("GEO")
    helpers_coll = ensure_collection("HELPERS")
    ensure_collection("COLLISION")
    ensure_collection("MLO")

    clear_scene()

    defaults = {**DEFAULTS, **data.get("defaults", {})}

    for room in data.get("rooms", []):
        build_room(room, defaults, geo_coll)
    for corr in data.get("corridors", []):
        build_corridor(corr, defaults, geo_coll)
    for stair in data.get("stairs", []):
        build_stair(stair, defaults, geo_coll)

    add_cutters(data, defaults, helpers_coll)

    bpy.ops.wm.save_as_mainfile(filepath=args.blend)
=======
#!/usr/bin/env python3
"""Blender headless blockout builder.

Executed via `blender -b -P build_from_floorplan.py -- --floorplan floorplan.json --output outdir`.
Creates simple rectangular rooms, walls, ceilings, corridors, and stair placeholders.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import bpy

COLLECTIONS = {
    "GEO": None,
    "COLLISION": None,
    "HELPERS": None,
}


def ensure_collections() -> None:
    for name in COLLECTIONS:
        if name in bpy.data.collections:
            COLLECTIONS[name] = bpy.data.collections[name]
        else:
            COLLECTIONS[name] = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(COLLECTIONS[name])


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for collection in list(bpy.data.collections):
        if collection.users == 0 and collection.name not in COLLECTIONS:
            bpy.data.collections.remove(collection)


def create_box(width: float, depth: float, height: float, name: str, collection) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.scale = (width / 2, depth / 2, height / 2)
    obj.name = name
    collection.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)
    return obj


def add_room(room: Dict[str, object]) -> None:
    obj = create_box(room["width"], room["depth"], room["height"], f"ROOM_{room['name'].replace(' ', '_')}_{room['floor']}", COLLECTIONS["GEO"])
    obj.location = (0, 0, room["floor"] * room["height"])

    wall_thickness = room.get("wall_thickness", 0.2)
    wall_height = room["height"]
    for idx, (dx, dy, w, d) in enumerate([
        (room["width"] / 2 + wall_thickness / 2, 0, wall_thickness, room["depth"] + wall_thickness * 2),
        (-room["width"] / 2 - wall_thickness / 2, 0, wall_thickness, room["depth"] + wall_thickness * 2),
        (0, room["depth"] / 2 + wall_thickness / 2, room["width"], wall_thickness),
        (0, -room["depth"] / 2 - wall_thickness / 2, room["width"], wall_thickness),
    ]):
        wall = create_box(w, d, wall_height, f"WALL_{room['name'].replace(' ', '_')}_{room['floor']}_{idx}", COLLECTIONS["GEO"])
        wall.location = (dx, dy, room["floor"] * room["height"])

    ceiling = create_box(room["width"], room["depth"], 0.05, f"CEIL_{room['name'].replace(' ', '_')}_{room['floor']}", COLLECTIONS["GEO"])
    ceiling.location = (0, 0, room["floor"] * room["height"] + room["height"])


def add_corridor(corridor: Dict[str, object], height: float) -> None:
    length = corridor.get("length", 12.0)
    obj = create_box(corridor["width"], length, height, f"CORRIDOR_{corridor['name']}_{corridor['floor']}", COLLECTIONS["GEO"])
    obj.location = (0, 0, corridor["floor"] * height)


def add_stairs(stair: Dict[str, object], height: float) -> None:
    step_height = 0.2
    steps = int(height / step_height)
    for i in range(steps):
        step = create_box(1.2, 0.3, step_height, f"STAIR_{stair['name']}_{i}", COLLECTIONS["GEO"])
        step.location = (0, i * 0.28, stair["from_floor"] * height + i * step_height)


def add_helper_origin() -> None:
    bpy.ops.object.empty_add(type="PLAIN_AXES")
    empty = bpy.context.active_object
    empty.name = "HELPER_ORIGIN"
    COLLECTIONS["HELPERS"].objects.link(empty)
    bpy.context.scene.collection.objects.unlink(empty)


def save_blend(path: Path) -> None:
    bpy.ops.wm.save_as_mainfile(filepath=str(path))


def build_from_plan(plan_path: Path, output_dir: Path, blend_path: Path) -> None:
    plan = json.loads(plan_path.read_text())
    clear_scene()
    ensure_collections()

    for room in plan.get("rooms", []):
        room["wall_thickness"] = plan.get("settings", {}).get("wall_thickness", 0.2)
        add_room(room)

    hallway_height = plan.get("settings", {}).get("floor_height", 3.2)
    for corridor in plan.get("corridors", []):
        add_corridor(corridor, hallway_height)

    for stair in plan.get("stairs", []):
        add_stairs(stair, hallway_height)

    add_helper_origin()
    output_dir.mkdir(parents=True, exist_ok=True)
    save_blend(blend_path)
    print(f"Saved blockout blend at {blend_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--floorplan", required=True, help="Floorplan JSON path")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--blend", required=True, help="Blend file path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_from_plan(Path(args.floorplan), Path(args.output), Path(args.blend))
>>>>>>> main


if __name__ == "__main__":
    main()
