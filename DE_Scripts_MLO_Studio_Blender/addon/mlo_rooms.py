import bpy

from .utils import append_log, collection_get_or_create


def create_rooms_and_portals(context, prompt_data, layout_data):
    rooms = prompt_data.get("rooms", [])
    if not rooms:
        append_log(context, "No rooms specified for MLO metadata.")
        return []

    collection = collection_get_or_create("DE_MLO_ROOMS")
    cols, rows = layout_data.get("room_grid", (1, 1))
    width = layout_data.get("width", 10.0)
    depth = layout_data.get("depth", 10.0)
    floor_height = layout_data.get("floor_height", 3.2)
    shell = layout_data.get("shell")
    base_offset = shell.location if shell else (0.0, 0.0, 0.0)

    room_objects = []
    portals = []

    room_index = 0
    for row in range(rows):
        for col in range(cols):
            if room_index >= len(rooms):
                continue
            name = rooms[room_index]
            x_pos = (-width / 2.0) + (col + 0.5) * (width / cols)
            y_pos = (-depth / 2.0) + (row + 0.5) * (depth / rows)
            bpy.ops.object.empty_add(
                type='CUBE',
                location=(x_pos + base_offset[0], y_pos + base_offset[1], floor_height / 2.0 + base_offset[2]),
            )
            empty = bpy.context.active_object
            empty.name = f"room_{name}"
            empty.scale = (width / cols / 2.0, depth / rows / 2.0, floor_height / 2.0)
            empty["room_name"] = name
            empty["room_index"] = room_index
            collection.objects.link(empty)
            bpy.context.scene.collection.objects.unlink(empty)
            room_objects.append(empty)
            room_index += 1

    for idx, room in enumerate(room_objects):
        if idx + 1 < len(room_objects):
            other = room_objects[idx + 1]
            bpy.ops.mesh.primitive_plane_add(location=(
                (room.location.x + other.location.x) / 2.0,
                (room.location.y + other.location.y) / 2.0,
                floor_height / 2.0 + base_offset[2],
            ))
            portal = bpy.context.active_object
            portal.name = f"portal_{room.name}_{other.name}"
            portal.scale = (1.0, 1.0, 1.0)
            portal["room_a"] = room.name
            portal["room_b"] = other.name
            collection.objects.link(portal)
            bpy.context.scene.collection.objects.unlink(portal)
            portals.append(portal)

    append_log(context, f"Created {len(room_objects)} room markers and {len(portals)} portals.")

    if hasattr(bpy.ops, "sollumz"):
        append_log(context, "Sollumz operators detected; room helpers ready for export.")
    else:
        append_log(context, "Sollumz operators missing; room helpers created only as empties.")

    return room_objects
