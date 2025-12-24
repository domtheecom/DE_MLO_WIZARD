import math

import bpy

from .utils import (
    append_log,
    apply_transforms,
    collection_get_or_create,
    get_or_create_material,
    merge_by_distance,
    recalc_normals,
    set_active_object,
    smart_uv,
)


MATERIALS = {
    "DE_Wall_Paint": (0.7, 0.7, 0.7, 1.0),
    "DE_Concrete": (0.5, 0.5, 0.5, 1.0),
    "DE_Glass": (0.2, 0.4, 0.6, 0.4),
    "DE_Metal": (0.3, 0.3, 0.3, 1.0),
}


def _create_materials():
    return {name: get_or_create_material(name, color) for name, color in MATERIALS.items()}


def _add_cube(name, size, location, collection):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0] / 2.0, size[1] / 2.0, size[2] / 2.0)
    collection.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)
    return obj


def _add_cylinder(name, radius, depth, location, collection):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    collection.objects.link(obj)
    bpy.context.scene.collection.objects.unlink(obj)
    return obj


def _apply_material(obj, mat):
    if not obj.data.materials:
        obj.data.materials.append(mat)
    else:
        obj.data.materials[0] = mat


def _boolean_difference(obj, cutters):
    for cutter in cutters:
        mod = obj.modifiers.new(name=f"bool_{cutter.name}", type='BOOLEAN')
        mod.object = cutter
        mod.operation = 'DIFFERENCE'
        mod.solver = 'EXACT'
        set_active_object(obj)
        bpy.ops.object.modifier_apply(modifier=mod.name)
        cutter.hide_viewport = True
        cutter.hide_render = True


def _add_door_opening(wall_obj, location, size, collection):
    cutter = _add_cube(
        name=f"{wall_obj.name}_door_cut",
        size=size,
        location=location,
        collection=collection,
    )
    _boolean_difference(wall_obj, [cutter])


def _build_rooms_grid(room_count):
    cols = max(1, math.ceil(math.sqrt(room_count)))
    rows = max(1, math.ceil(room_count / cols))
    return cols, rows


def generate_building(context, prompt_data, settings):
    append_log(context, "Generating building geometry...")
    collection = collection_get_or_create("DE_MLO")
    materials = _create_materials()

    floors = max(1, prompt_data.get("floors", 1))
    bays = max(0, prompt_data.get("bays", 0))
    rooms = prompt_data.get("rooms", [])

    room_count = max(1, len(rooms))
    cols, rows = _build_rooms_grid(room_count)

    bay_width = 6.0
    room_size = 5.0
    wall_thickness = 0.2
    floor_height = 3.2

    width = max(room_size * cols, bay_width * bays + 4.0)
    depth = room_size * rows + 4.0

    shell_objects = []

    for floor in range(floors):
        z_base = floor * floor_height
        slab = _add_cube(
            name=f"de_floor_{floor+1}",
            size=(width, depth, 0.2),
            location=(0, 0, z_base),
            collection=collection,
        )
        _apply_material(slab, materials["DE_Concrete"])
        shell_objects.append(slab)

        wall_height = floor_height
        wall_offset = z_base + wall_height / 2.0

        wall_front = _add_cube(
            name=f"de_wall_front_{floor+1}",
            size=(width, wall_thickness, wall_height),
            location=(0, depth / 2.0, wall_offset),
            collection=collection,
        )
        wall_back = _add_cube(
            name=f"de_wall_back_{floor+1}",
            size=(width, wall_thickness, wall_height),
            location=(0, -depth / 2.0, wall_offset),
            collection=collection,
        )
        wall_left = _add_cube(
            name=f"de_wall_left_{floor+1}",
            size=(wall_thickness, depth, wall_height),
            location=(-width / 2.0, 0, wall_offset),
            collection=collection,
        )
        wall_right = _add_cube(
            name=f"de_wall_right_{floor+1}",
            size=(wall_thickness, depth, wall_height),
            location=(width / 2.0, 0, wall_offset),
            collection=collection,
        )
        for wall in (wall_front, wall_back, wall_left, wall_right):
            _apply_material(wall, materials["DE_Wall_Paint"])
            shell_objects.append(wall)

        if bays > 0 and floor == 0:
            cutters = []
            spacing = width / (bays + 1)
            for bay_idx in range(bays):
                x_pos = -width / 2.0 + spacing * (bay_idx + 1)
                cutter = _add_cube(
                    name=f"de_bay_cut_{bay_idx+1}",
                    size=(bay_width * 0.9, wall_thickness * 2.0, floor_height * 0.85),
                    location=(x_pos, depth / 2.0, wall_offset * 0.95),
                    collection=collection,
                )
                cutters.append(cutter)
            _boolean_difference(wall_front, cutters)

        room_index = 0
        for row in range(rows):
            for col in range(cols):
                if room_index >= room_count:
                    continue
                x_pos = (-width / 2.0) + (col + 0.5) * (width / cols)
                y_pos = (-depth / 2.0) + (row + 0.5) * (depth / rows)
                if row < rows - 1:
                    wall = _add_cube(
                        name=f"de_partition_{floor+1}_{row}_{col}",
                        size=(width / cols - 0.4, wall_thickness, wall_height),
                        location=(x_pos, y_pos + (depth / rows) / 2.0, wall_offset),
                        collection=collection,
                    )
                    _apply_material(wall, materials["DE_Wall_Paint"])
                    _add_door_opening(
                        wall,
                        (x_pos, y_pos + (depth / rows) / 2.0, z_base + 1.1),
                        (1.2, wall_thickness * 2.0, 2.2),
                        collection,
                    )
                    shell_objects.append(wall)
                if col < cols - 1:
                    wall = _add_cube(
                        name=f"de_partition_v_{floor+1}_{row}_{col}",
                        size=(wall_thickness, depth / rows - 0.4, wall_height),
                        location=(x_pos + (width / cols) / 2.0, y_pos, wall_offset),
                        collection=collection,
                    )
                    _apply_material(wall, materials["DE_Wall_Paint"])
                    _add_door_opening(
                        wall,
                        (x_pos + (width / cols) / 2.0, y_pos, z_base + 1.1),
                        (wall_thickness * 2.0, 1.2, 2.2),
                        collection,
                    )
                    shell_objects.append(wall)
                room_index += 1

        if floor == floors - 1:
            roof = _add_cube(
                name="de_roof",
                size=(width, depth, 0.2),
                location=(0, 0, z_base + floor_height),
                collection=collection,
            )
            _apply_material(roof, materials["DE_Concrete"])
            shell_objects.append(roof)

    if floors > 1:
        stair_height = floor_height * (floors - 1)
        stairs = _add_cube(
            name="de_stairs",
            size=(2.0, 4.0, stair_height),
            location=(-width / 2.0 + 2.0, -depth / 2.0 + 2.0, stair_height / 2.0),
            collection=collection,
        )
        _apply_material(stairs, materials["DE_Concrete"])
        shell_objects.append(stairs)

    if "fire_pole" in rooms:
        pole = _add_cylinder(
            name="de_fire_pole",
            radius=0.15,
            depth=floor_height * floors,
            location=(width / 2.0 - 1.5, depth / 2.0 - 1.5, floor_height * floors / 2.0),
            collection=collection,
        )
        _apply_material(pole, materials["DE_Metal"])
        shell_objects.append(pole)

    if "watch_tower" in prompt_data.get("exterior", []):
        platform = _add_cube(
            name="de_watch_tower",
            size=(3.0, 3.0, 0.3),
            location=(width / 2.0 + 3.0, 0, floor_height + 2.0),
            collection=collection,
        )
        _apply_material(platform, materials["DE_Metal"])
        supports = _add_cube(
            name="de_watch_supports",
            size=(0.4, 3.0, floor_height + 2.0),
            location=(width / 2.0 + 3.0, 0, (floor_height + 2.0) / 2.0),
            collection=collection,
        )
        _apply_material(supports, materials["DE_Metal"])
        shell_objects.extend([platform, supports])

    if "apron" in prompt_data.get("exterior", []):
        apron = _add_cube(
            name="de_apron",
            size=(width * 1.2, 4.0, 0.1),
            location=(0, depth / 2.0 + 2.0, 0.0),
            collection=collection,
        )
        _apply_material(apron, materials["DE_Concrete"])
        shell_objects.append(apron)

    for obj in shell_objects:
        apply_transforms(obj)
        recalc_normals(obj)
        merge_by_distance(obj)
        smart_uv(obj)

    if shell_objects:
        main = shell_objects[0]
        for obj in shell_objects[1:]:
            set_active_object(main)
            obj.select_set(True)
            bpy.ops.object.join()
            main = bpy.context.active_object
        main.name = "de_mlo_shell"
        _apply_material(main, materials["DE_Wall_Paint"])
        main.location = (settings.base_x, settings.base_y, settings.base_z)
        main.rotation_euler[2] = math.radians(settings.heading)
        apply_transforms(main)
        recalc_normals(main)
        merge_by_distance(main)
        smart_uv(main)
        append_log(context, "Shell mesh created: de_mlo_shell")
        return {
            "collection": collection,
            "shell": main,
            "width": width,
            "depth": depth,
            "floors": floors,
            "floor_height": floor_height,
            "room_grid": (cols, rows),
        }

    append_log(context, "No shell objects created. Using defaults.")
    return {
        "collection": collection,
        "shell": None,
        "width": width,
        "depth": depth,
        "floors": floors,
        "floor_height": floor_height,
        "room_grid": (cols, rows),
    }


def generate_furnishings(context, prompt_data, layout_data):
    append_log(context, "Generating furnishings placeholders...")
    collection = collection_get_or_create("DE_MLO_Furnishings")
    rooms = prompt_data.get("rooms", [])
    width = layout_data.get("width", 10.0)
    depth = layout_data.get("depth", 10.0)
    cols, rows = layout_data.get("room_grid", (1, 1))
    floor_height = layout_data.get("floor_height", 3.2)
    shell = layout_data.get("shell")
    base_offset = shell.location if shell else (0.0, 0.0, 0.0)

    room_index = 0
    for row in range(rows):
        for col in range(cols):
            if room_index >= len(rooms):
                continue
            x_pos = (-width / 2.0) + (col + 0.5) * (width / cols)
            y_pos = (-depth / 2.0) + (row + 0.5) * (depth / rows)
            room_name = rooms[room_index]
            bpy.ops.mesh.primitive_cube_add(
                size=1.0,
                location=(x_pos + base_offset[0], y_pos + base_offset[1], floor_height / 4.0 + base_offset[2]),
            )
            obj = bpy.context.active_object
            obj.name = f"de_furn_{room_name}_{room_index}"
            obj.scale = (1.0, 0.6, 0.5)
            collection.objects.link(obj)
            bpy.context.scene.collection.objects.unlink(obj)
            room_index += 1
    append_log(context, "Furnishings generated.")


def generate_collision_proxy(context, layout_data):
    shell_obj = layout_data.get("shell")
    if shell_obj is None:
        append_log(context, "Collision proxy skipped: shell missing.")
        return None

    bpy.ops.object.select_all(action='DESELECT')
    shell_obj.select_set(True)
    bpy.context.view_layer.objects.active = shell_obj
    bpy.ops.object.duplicate()
    proxy = bpy.context.active_object
    proxy.name = "de_col_proxy"

    mod = proxy.modifiers.new(name="Decimate", type='DECIMATE')
    mod.ratio = 0.3
    bpy.ops.object.modifier_apply(modifier=mod.name)

    apply_transforms(proxy)
    recalc_normals(proxy)
    merge_by_distance(proxy)
    smart_uv(proxy)
    append_log(context, "Collision proxy created: de_col_proxy")
    return proxy
