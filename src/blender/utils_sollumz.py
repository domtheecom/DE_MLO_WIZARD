import addon_utils
import bpy


def is_sollumz_loaded():
    return any(mod.__name__.lower().startswith("sollumz") for mod in addon_utils.modules())


def find_op(names):
    for name in names:
        if "." in name:
            group, op_name = name.split(".", 1)
            group_obj = getattr(bpy.ops, group, None)
            if group_obj and hasattr(group_obj, op_name):
                return getattr(group_obj, op_name)
        else:
            op = getattr(bpy.ops, name, None)
            if op:
                return op
    return None


def ensure_material(obj):
    if not obj or not getattr(obj, "data", None):
        return None
    if obj.data.materials:
        return obj.data.materials[0]
    create_shader = find_op(["sollumz.createshadermaterial"])
    if create_shader:
        try:
            create_shader()
            if obj.data.materials:
                return obj.data.materials[0]
        except Exception:
            pass
    mat = bpy.data.materials.new(name="Sollumz_Default")
    obj.data.materials.append(mat)
    return mat


def select_geo():
    bpy.ops.object.select_all(action="DESELECT")
    geo_coll = bpy.data.collections.get("GEO")
    if geo_coll:
        targets = [obj for obj in geo_coll.objects if obj.type == "MESH"]
    else:
        targets = [obj for obj in bpy.data.objects if obj.type == "MESH" and obj.name.startswith(("WALL_", "FLOOR_", "CEIL_", "STAIR_", "CORRIDOR", "ROOM_"))]
    for obj in targets:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
