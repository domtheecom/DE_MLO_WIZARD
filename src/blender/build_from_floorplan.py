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


if __name__ == "__main__":
    main()
