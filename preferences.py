# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2013-2024 Campbell Barton
# SPDX-FileCopyrightText: 2016-2025 Mikhail Rachinskiy

import math

from bpy.props import (
    BoolProperty,
    CollectionProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    StringProperty,
)
from bpy.types import AddonPreferences, Operator, PropertyGroup, UIList

from . import __package__ as base_package
from . import report


def _preset_items(_self, context):
    items = [("", "None", "", 0)]

    if context is None:
        return items

    addon = context.preferences.addons.get(base_package)
    if addon is None:
        return items

    prefs = addon.preferences
    for i, preset in enumerate(prefs.export_presets):
        items.append((str(i), preset.name, preset.description, i + 1))

    return items


class ExportPreset(PropertyGroup):
    name: StringProperty(name="Name", default="Preset")
    description: StringProperty(name="Description", default="")
    export_format: EnumProperty(
        name="Format",
        items=(
            ("OBJ", "OBJ", ""),
            ("PLY", "PLY", ""),
            ("STL", "STL", ""),
            ("3MF", "3MF", ""),
        ),
        default="STL",
    )
    use_ascii_format: BoolProperty(name="ASCII")
    use_scene_scale: BoolProperty(name="Scene Scale")
    use_copy_textures: BoolProperty(name="Copy Textures")
    use_uv: BoolProperty(name="UVs")
    use_normals: BoolProperty(name="Normals")
    use_colors: BoolProperty(name="Colors")
    use_3mf_materials: BoolProperty(name="3MF Materials", default=True)
    use_3mf_units: BoolProperty(name="3MF Units", default=True)


class PRINT3D_UL_export_presets(UIList):
    def draw_item(self, _context, layout, _data, item, icon, _active_data, _active_propname, index):
        del icon

        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.label(text=item.name, translate=False)
            layout.label(text=item.export_format, translate=False)
        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text=str(index))


class PRINT3D_OT_preset_add(Operator):
    bl_idname = "print3d.preset_add"
    bl_label = "Add Export Preset"

    def execute(self, context):
        addon = context.preferences.addons.get(base_package)
        if addon is None:
            return {"CANCELLED"}

        prefs = addon.preferences
        scene_props = context.scene.print3d_toolbox

        preset = prefs.export_presets.add()
        preset.name = f"Preset {len(prefs.export_presets)}"
        self._copy_from_scene(scene_props, preset)
        prefs.export_preset_active = len(prefs.export_presets) - 1
        return {"FINISHED"}

    @staticmethod
    def _copy_from_scene(scene_props, preset):
        preset.export_format = scene_props.export_format
        preset.use_ascii_format = scene_props.use_ascii_format
        preset.use_scene_scale = scene_props.use_scene_scale
        preset.use_copy_textures = scene_props.use_copy_textures
        preset.use_uv = scene_props.use_uv
        preset.use_normals = scene_props.use_normals
        preset.use_colors = scene_props.use_colors
        preset.use_3mf_materials = scene_props.use_3mf_materials
        preset.use_3mf_units = scene_props.use_3mf_units


class PRINT3D_OT_preset_remove(Operator):
    bl_idname = "print3d.preset_remove"
    bl_label = "Remove Export Preset"

    @classmethod
    def poll(cls, context):
        addon = context.preferences.addons.get(base_package)
        return addon is not None and bool(addon.preferences.export_presets)

    def execute(self, context):
        addon = context.preferences.addons.get(base_package)
        prefs = addon.preferences

        if not prefs.export_presets:
            return {"CANCELLED"}

        prefs.export_presets.remove(prefs.export_preset_active)
        prefs.export_preset_active = min(prefs.export_preset_active, len(prefs.export_presets) - 1)
        return {"FINISHED"}


def _init_default_presets(prefs):
    if prefs.export_presets:
        return

    preset = prefs.export_presets.add()
    preset.name = "FFF PLA"
    preset.description = "General-purpose FFF profile with materials enabled"
    preset.export_format = "3MF"
    preset.use_scene_scale = True
    preset.use_copy_textures = True
    preset.use_uv = True
    preset.use_normals = True
    preset.use_colors = True
    preset.use_3mf_materials = True
    preset.use_3mf_units = True

    preset = prefs.export_presets.add()
    preset.name = "SLA Resin"
    preset.description = "Simple watertight STL preset for resin printers"
    preset.export_format = "STL"
    preset.use_scene_scale = True
    preset.use_normals = True
    preset.use_colors = False


class AddonPrefs(AddonPreferences):
    bl_idname = base_package

    export_presets: CollectionProperty(type=ExportPreset)
    export_preset_active: IntProperty()

    def draw(self, _context):
        layout = self.layout
        _init_default_presets(self)
        layout.label(text="Export Presets")

        row = layout.row()
        row.template_list(
            "PRINT3D_UL_export_presets",
            "",
            self,
            "export_presets",
            self,
            "export_preset_active",
            rows=3,
        )

        col = row.column(align=True)
        col.operator("print3d.preset_add", icon="ADD", text="")
        col.operator("print3d.preset_remove", icon="REMOVE", text="")

        if 0 <= self.export_preset_active < len(self.export_presets):
            preset = self.export_presets[self.export_preset_active]
            box = layout.box()
            box.prop(preset, "name")
            box.prop(preset, "description")
            box.prop(preset, "export_format")

            col = box.column(heading="General")
            sub = col.column()
            sub.active = preset.export_format != "OBJ"
            sub.prop(preset, "use_ascii_format")
            col.prop(preset, "use_scene_scale")

            col = box.column(heading="Geometry")
            col.active = preset.export_format != "STL"
            col.prop(preset, "use_uv")
            col.prop(preset, "use_normals")
            col.prop(preset, "use_colors")

            col = box.column(heading="Materials")
            col.prop(preset, "use_copy_textures")

            col = box.column(heading="3MF")
            col.active = preset.export_format == "3MF"
            col.prop(preset, "use_3mf_materials")
            col.prop(preset, "use_3mf_units")


class SceneProperties(PropertyGroup):

    # Analyze
    # -------------------------------------

    threshold_zero: FloatProperty(
        name="Limit",
        subtype="DISTANCE",
        default=0.0001,
        min=0.0,
        max=0.2,
        precision=5,
        step=0.01
    )
    angle_nonplanar: FloatProperty(
        name="Limit",
        subtype="ANGLE",
        default=math.radians(5.0),
        min=0.0,
        max=math.radians(180.0),
        step=100,
    )
    thickness_min: FloatProperty(
        name="Minimum Thickness",
        subtype="DISTANCE",
        default=0.001,  # 1mm
        min=0.0,
        max=10.0,
        precision=3,
        step=0.1
    )
    angle_sharp: FloatProperty(
        name="Angle",
        subtype="ANGLE",
        default=math.radians(160.0),
        min=0.0,
        max=math.radians(180.0),
        step=100,
    )
    angle_overhang: FloatProperty(
        name="Angle",
        subtype="ANGLE",
        default=math.radians(45.0),
        min=0.0,
        max=math.radians(90.0),
        step=100,
    )
    overhang_optimize_angle: FloatProperty(
        name="Target Angle",
        subtype="ANGLE",
        default=math.radians(45.0),
        min=0.0,
        max=math.radians(90.0),
        step=100,
    )
    overhang_optimize_iterations: IntProperty(
        name="Iterations",
        default=48,
        min=1,
        soft_max=256,
    )

    # Export
    # -------------------------------------

    export_path: StringProperty(
        name="Export Directory",
        default="//",
        maxlen=1024,
        subtype="DIR_PATH",
    )
    export_format: EnumProperty(
        name="Format",
        description="File format",
        items=(
            ("OBJ", "OBJ", ""),
            ("PLY", "PLY", ""),
            ("STL", "STL", ""),
            ("3MF", "3MF", ""),
        ),
        default="STL",
    )
    export_preset: EnumProperty(
        name="Preset",
        description="Choose a preset to apply saved export settings",
        items=_preset_items,
        update=lambda self, context: self.apply_preset(context),
    )
    use_ascii_format: BoolProperty(
        name="ASCII",
        description="Export file in ASCII format",
    )
    use_scene_scale: BoolProperty(
        name="Scene Scale",
        description="Apply scene scale on export",
    )
    use_copy_textures: BoolProperty(
        name="Copy Textures",
        description="Copy textures on export to the output path",
    )
    use_uv: BoolProperty(name="UVs")
    use_normals: BoolProperty(
        name="Normals",
        description="Export specific vertex normals if available, export calculated normals otherwise"
    )
    use_colors: BoolProperty(
        name="Colors",
        description="Export vertex color attributes",
    )
    use_3mf_materials: BoolProperty(
        name="Materials",
        description="Include materials in the 3MF export",
        default=True,
    )
    use_3mf_units: BoolProperty(
        name="Units",
        description="Write scene unit information to the 3MF export",
        default=True,
    )

    def apply_preset(self, context) -> None:
        if not self.export_preset or context is None:
            return

        addon = context.preferences.addons.get(base_package)
        if addon is None:
            return

        prefs = addon.preferences
        index = int(self.export_preset)
        if index >= len(prefs.export_presets):
            return

        preset = prefs.export_presets[index]
        self.export_format = preset.export_format
        self.use_ascii_format = preset.use_ascii_format
        self.use_scene_scale = preset.use_scene_scale
        self.use_copy_textures = preset.use_copy_textures
        self.use_uv = preset.use_uv
        self.use_normals = preset.use_normals
        self.use_colors = preset.use_colors
        self.use_3mf_materials = preset.use_3mf_materials
        self.use_3mf_units = preset.use_3mf_units

    @staticmethod
    def get_report():
        return report.info()
