import bpy


class ToolProperties(bpy.types.PropertyGroup):
    camera_device_slot: bpy.props.IntProperty(
        name="Camera device slot", default=0, min=0
    )
    skip_frames: bpy.props.IntProperty(name="Skip frames", default=4, min=0)


def register():
    bpy.utils.register_class(ToolProperties)
    bpy.types.Scene.handtracktool = bpy.props.PointerProperty(type=ToolProperties)


def unregister():
    del bpy.types.Scene.handtracktool
    bpy.utils.unregister_class(ToolProperties)
