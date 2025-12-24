bl_info = {
    "name": "DE Scripts MLO Studio",
    "author": "DE Scripts",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > DE Scripts",
    "description": "Prompt-driven MLO building generator and FiveM exporter",
    "category": "3D View",
}

import bpy

from . import ui, operators
from .utils import init_logger_properties

classes = (
    ui.DEMLOSettings,
    ui.DEMLO_UL_Log,
    ui.DEMLO_PT_MainPanel,
    operators.DEMLO_OT_Build,
    operators.DEMLO_OT_Export,
    operators.DEMLO_OT_BuildExport,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.de_mlo_settings = bpy.props.PointerProperty(type=ui.DEMLOSettings)
    init_logger_properties()


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Scene, "de_mlo_settings"):
        del bpy.types.Scene.de_mlo_settings
    if hasattr(bpy.types.Scene, "de_mlo_log"):
        del bpy.types.Scene.de_mlo_log


if __name__ == "__main__":
    register()
