import datetime
import json
import os
import re

import bpy


LOG_PROPERTY = "de_mlo_log"


def init_logger_properties():
    if not hasattr(bpy.types.Scene, LOG_PROPERTY):
        bpy.types.Scene.de_mlo_log = bpy.props.StringProperty(
            name="DE MLO Log",
            default="",
            description="Log output",
            options={'MULTILINE'}
        )


def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def append_log(context, message):
    entry = f"[{timestamp()}] {message}"
    scene = context.scene
    current = getattr(scene, LOG_PROPERTY, "")
    updated = f"{current}\n{entry}".strip()
    setattr(scene, LOG_PROPERTY, updated)
    print(entry)


def sanitize_resource_name(name):
    if not name:
        return "de_mlo_build"
    cleaned = re.sub(r"[^a-zA-Z0-9_]+", "_", name.strip())
    return cleaned or "de_mlo_build"


def safe_mkdir(path):
    if not path:
        return
    os.makedirs(path, exist_ok=True)


def safe_write_text(path, content):
    safe_mkdir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as file_handle:
        file_handle.write(content)


def safe_write_json(path, data):
    safe_mkdir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, indent=2)


def ensure_absolute_dir(path):
    if not path:
        return ""
    normalized = os.path.normpath(os.path.expanduser(path))
    return os.path.abspath(normalized)


def show_message_box(message, title="DE Scripts MLO Studio", icon='INFO'):
    def draw(self, context):
        for line in message.split("\n"):
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def set_active_object(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def apply_transforms(obj):
    set_active_object(obj)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def merge_by_distance(obj, distance=0.0001):
    set_active_object(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.merge_by_distance(threshold=distance)
    bpy.ops.object.mode_set(mode='OBJECT')


def recalc_normals(obj):
    set_active_object(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')


def smart_uv(obj):
    set_active_object(obj)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=66.0)
    bpy.ops.object.mode_set(mode='OBJECT')


def get_or_create_material(name, color):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs[0].default_value = color
    return mat


def collection_get_or_create(name):
    collection = bpy.data.collections.get(name)
    if collection is None:
        collection = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(collection)
    return collection
