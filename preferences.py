# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2013-2024 Campbell Barton
# SPDX-FileCopyrightText: 2016-2025 Mikhail Rachinskiy

import math

from bpy.props import (
    BoolProperty,
    BoolVectorProperty,
    EnumProperty,
    FloatProperty,
    StringProperty,
)
from bpy.types import PropertyGroup

from . import report


BED_PROFILES = {
    "ENDER3": (220.0, 220.0, 250.0, "Ender 3 (220x220x250mm)"),
    "PRUSA_MK4": (250.0, 210.0, 220.0, "Prusa MK4 (250x210x220mm)"),
    "BAMBULAB_P1P": (256.0, 256.0, 256.0, "Bambu Lab P1P (256x256x256mm)"),
    "CUSTOM": (220.0, 220.0, 220.0, "Custom"),
}


def bed_profile_items(self, _context):
    return [(key, name, "") for key, (_x, _y, _z, name) in BED_PROFILES.items()]


def bed_profile_dimensions(props) -> tuple[float, float, float]:
    if props.bed_profile == "CUSTOM":
        return props.bed_size_x, props.bed_size_y, props.bed_size_z

    x, y, z, _label = BED_PROFILES[props.bed_profile]
    return x, y, z


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
        ),
        default="STL",
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
        description="Export vertex color attributes"
    )

    # Build Volume
    # -------------------------------------

    bed_profile: EnumProperty(
        name="Profile",
        description="Select a preset build volume or use a custom size",
        items=bed_profile_items,
        default="ENDER3",
    )
    bed_size_x: FloatProperty(
        name="Width",
        subtype="DISTANCE",
        default=BED_PROFILES["CUSTOM"][0],
        min=0.0,
    )
    bed_size_y: FloatProperty(
        name="Depth",
        subtype="DISTANCE",
        default=BED_PROFILES["CUSTOM"][1],
        min=0.0,
    )
    bed_size_z: FloatProperty(
        name="Height",
        subtype="DISTANCE",
        default=BED_PROFILES["CUSTOM"][2],
        min=0.0,
    )
    bed_report: StringProperty(
        name="",
        description="Last build volume validation result",
        default="",
        options={"HIDDEN"},
    )
    bed_axis_overflow: BoolVectorProperty(
        size=3,
        default=(False, False, False),
        options={"HIDDEN"},
    )

    @staticmethod
    def get_report():
        return report.info()
