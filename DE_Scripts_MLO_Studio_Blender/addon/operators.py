import os

import bpy

from .generator import generate_building
from .mlo_rooms import create_rooms_and_portals
from .prompt_parser import parse_prompt
from .exporter import export_fivem_resource
from .preview import render_preview
from .utils import append_log, ensure_absolute_dir, sanitize_resource_name


def _get_settings(context):
    return context.scene.de_mlo_settings


def _clear_previous_generated():
    for name in ("DE_MLO", "DE_MLO_Furnishings", "DE_MLO_ROOMS"):
        collection = bpy.data.collections.get(name)
        if collection:
            for obj in list(collection.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(collection)


def _build_all(context):
    settings = _get_settings(context)
    _clear_previous_generated()

    prompt_data = parse_prompt(settings.prompt_text, settings.building_preset)
    settings.cached_floors = prompt_data.get("floors", 1)
    settings.cached_bays = prompt_data.get("bays", 0)
    settings.cached_rooms = ", ".join(prompt_data.get("rooms", []))

    append_log(context, f"Parsed prompt: {prompt_data}")

    layout_data = generate_building(context, prompt_data, settings)

    room_markers = create_rooms_and_portals(context, prompt_data, layout_data)

    if settings.generate_furnishings:
        from .generator import generate_furnishings
        generate_furnishings(context, prompt_data, layout_data)

    collision_obj = None
    if settings.generate_collision_proxy:
        from .generator import generate_collision_proxy
        collision_obj = generate_collision_proxy(context, layout_data)

    if settings.generate_preview_image:
        output_dir = ensure_absolute_dir(settings.output_folder)
        if output_dir:
            resource_name = sanitize_resource_name(settings.resource_name)
            preview_dir = os.path.join(output_dir, resource_name, "preview")
            render_preview(context, preview_dir)
        else:
            append_log(context, "Preview skipped: Output folder missing.")

    return layout_data.get("shell"), collision_obj, bool(room_markers)


class DEMLO_OT_Build(bpy.types.Operator):
    bl_idname = "de_mlo.build"
    bl_label = "Build MLO"
    bl_description = "Generate MLO building from prompt"

    def execute(self, context):
        try:
            _build_all(context)
            append_log(context, "Build completed.")
        except Exception as exc:
            append_log(context, f"Build failed: {exc}")
        return {'FINISHED'}


class DEMLO_OT_Export(bpy.types.Operator):
    bl_idname = "de_mlo.export"
    bl_label = "Export FiveM Resource"
    bl_description = "Export current MLO to a FiveM resource folder"

    def execute(self, context):
        settings = _get_settings(context)
        shell_obj = bpy.data.objects.get("de_mlo_shell")
        collision_obj = bpy.data.objects.get("de_col_proxy")
        export_ok = export_fivem_resource(context, settings, shell_obj, collision_obj, export_rooms=True)
        if export_ok and settings.generate_preview_image:
            output_dir = ensure_absolute_dir(settings.output_folder)
            if output_dir:
                resource_name = sanitize_resource_name(settings.resource_name)
                preview_dir = os.path.join(output_dir, resource_name, "preview")
                render_preview(context, preview_dir)
        return {'FINISHED'}


class DEMLO_OT_BuildExport(bpy.types.Operator):
    bl_idname = "de_mlo.build_export"
    bl_label = "Build + Export"
    bl_description = "Build MLO and export to FiveM"

    def execute(self, context):
        try:
            shell_obj, collision_obj, export_rooms = _build_all(context)
            settings = _get_settings(context)
            export_fivem_resource(context, settings, shell_obj, collision_obj, export_rooms)
            append_log(context, "Build + Export completed.")
        except Exception as exc:
            append_log(context, f"Build + Export failed: {exc}")
        return {'FINISHED'}
