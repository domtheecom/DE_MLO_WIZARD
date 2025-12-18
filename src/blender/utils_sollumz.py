import bpy


def is_sollumz_loaded():
    return any(mod.__name__.lower().startswith("sollumz") for mod in bpy.utils.addon_utils.modules())


def find_op(names):
    for n in names:
        op = getattr(bpy.ops, n, None)
        if op:
            return op
    parts = n.split(".")
    if len(parts) == 2:
        group = getattr(bpy.ops, parts[0], None)
        if group and hasattr(group, parts[1]):
            return getattr(group, parts[1])
    return None


def ensure_material(obj):
    if obj.data.materials:
        return obj.data.materials[0]
    mat = bpy.data.materials.new(name="Sollumz_Default")
    obj.data.materials.append(mat)
    return mat


def select_geo():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.name.startswith(("WALL_", "FLOOR_", "CEIL_", "STAIR_", "CORRIDOR", "ROOM_")):
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

