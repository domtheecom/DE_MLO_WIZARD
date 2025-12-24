import math
import os

import bpy

from .utils import append_log, safe_mkdir


def render_preview(context, output_dir, width=1024, height=1024):
    scene = context.scene
    if not output_dir:
        append_log(context, "Preview output directory missing.")
        return False

    safe_mkdir(output_dir)
    output_path = os.path.join(output_dir, "preview.png")

    original_camera = scene.camera
    original_world = scene.world
    original_render_path = scene.render.filepath
    original_resolution = (scene.render.resolution_x, scene.render.resolution_y)
    original_engine = scene.render.engine

    world = bpy.data.worlds.new("DE_MLO_Preview_World")
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
    scene.world = world

    bpy.ops.object.camera_add(location=(0, 0, 50))
    camera = bpy.context.active_object
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 50
    camera.location = (0, 0, 50)
    camera.rotation_euler = (math.radians(90), 0, 0)
    scene.camera = camera

    scene.render.filepath = output_path
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.engine = 'BLENDER_EEVEE'

    bpy.ops.render.render(write_still=True)

    scene.camera = original_camera
    scene.world = original_world
    scene.render.filepath = original_render_path
    scene.render.resolution_x, scene.render.resolution_y = original_resolution
    scene.render.engine = original_engine

    if camera:
        bpy.data.objects.remove(camera, do_unlink=True)
    if world:
        bpy.data.worlds.remove(world)

    append_log(context, f"Preview rendered to {output_path}")
    return True
