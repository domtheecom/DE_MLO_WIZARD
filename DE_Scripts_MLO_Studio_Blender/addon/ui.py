import bpy


class DEMLOSettings(bpy.types.PropertyGroup):
    prompt_text: bpy.props.StringProperty(
        name="Prompt",
        description="Describe the building to generate",
        default="",
        options={'MULTILINE'},
    )
    resource_name: bpy.props.StringProperty(
        name="Resource Name",
        default="de_mlo_build",
    )
    output_folder: bpy.props.StringProperty(
        name="Output Folder",
        subtype='DIR_PATH',
    )
    base_x: bpy.props.FloatProperty(name="Base X", default=0.0)
    base_y: bpy.props.FloatProperty(name="Base Y", default=0.0)
    base_z: bpy.props.FloatProperty(name="Base Z", default=0.0)
    heading: bpy.props.FloatProperty(name="Heading", default=0.0)
    building_preset: bpy.props.EnumProperty(
        name="Building Preset",
        items=[
            ("FIRE_STATION", "FIRE_STATION", "Fire station layout"),
            ("POLICE_STATION", "POLICE_STATION", "Police station layout"),
            ("HOSPITAL", "HOSPITAL", "Hospital layout"),
            ("OFFICE", "OFFICE", "Office layout"),
            ("GENERIC", "GENERIC", "Generic layout"),
        ],
        default="GENERIC",
    )
    detail_level: bpy.props.EnumProperty(
        name="Detail Level",
        items=[
            ("LOW", "LOW", "Low detail"),
            ("MEDIUM", "MEDIUM", "Medium detail"),
            ("HIGH", "HIGH", "High detail"),
        ],
        default="MEDIUM",
    )
    generate_furnishings: bpy.props.BoolProperty(
        name="Generate Furnishings",
        default=True,
    )
    generate_collision_proxy: bpy.props.BoolProperty(
        name="Generate Collision Proxy",
        default=True,
    )
    generate_preview_image: bpy.props.BoolProperty(
        name="Generate Preview Image",
        default=True,
    )
    export_furnishings_as_meshes: bpy.props.BoolProperty(
        name="Export Furnishings",
        default=False,
    )
    cached_floors: bpy.props.IntProperty(name="Floors", default=1)
    cached_bays: bpy.props.IntProperty(name="Bays", default=0)
    cached_rooms: bpy.props.StringProperty(name="Rooms", default="")


class DEMLO_UL_Log(bpy.types.UIList):
    bl_idname = "DEMLO_UL_Log"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.label(text=item.name)


class DEMLO_PT_MainPanel(bpy.types.Panel):
    bl_label = "DE Scripts MLO Studio"
    bl_idname = "DEMLO_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "DE Scripts"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.de_mlo_settings

        layout.label(text="DE Scripts MLO Studio")
        layout.label(text="[DE] MLO Generator")
        layout.separator()

        layout.prop(settings, "prompt_text", text="Prompt")
        layout.prop(settings, "resource_name")
        layout.prop(settings, "output_folder")

        col = layout.column(align=True)
        col.label(text="Base Coords")
        row = col.row(align=True)
        row.prop(settings, "base_x", text="X")
        row.prop(settings, "base_y", text="Y")
        row.prop(settings, "base_z", text="Z")

        layout.prop(settings, "heading")
        layout.prop(settings, "building_preset")
        layout.prop(settings, "detail_level")

        layout.prop(settings, "generate_furnishings")
        layout.prop(settings, "generate_collision_proxy")
        layout.prop(settings, "generate_preview_image")
        layout.prop(settings, "export_furnishings_as_meshes")

        row = layout.row()
        row.operator("de_mlo.build", text="Build MLO")
        row = layout.row()
        row.operator("de_mlo.export", text="Export FiveM Resource")
        row = layout.row()
        row.operator("de_mlo.build_export", text="Build + Export")

        layout.separator()
        layout.label(text="Log Output")
        layout.prop(context.scene, "de_mlo_log", text="")
