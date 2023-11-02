import bpy


class HTA_Properties(bpy.types.PropertyGroup):
    camera_device_slot: bpy.props.IntProperty(
        name="Camera device slot",
        description="Select the index of the capture device",
        default=0,
        min=0,
    )

    skip_frames: bpy.props.IntProperty(
        name="Skip frames",
        description="Number of frames to skip for each step",
        default=4,
        min=0,
        max=12,
    )

    def is_armature(self, object):
        if object.type == "ARMATURE":
            return True
        return False

    selected_rig: bpy.props.PointerProperty(
        name="Transfer to rig",
        type=bpy.types.Object,
        description="Select an armature for animation transfer",
        poll=is_armature,
    )

    def hta_collection_poll(self, col):
        return col.name.startswith("hta_")

    drivers_collection: bpy.props.PointerProperty(
        name="Drivers Collection",
        description="Select a collection of drivers",
        type=bpy.types.Collection,
    )


def register():
    bpy.utils.register_class(HTA_Properties)
    bpy.types.Scene.hta = bpy.props.PointerProperty(type=HTA_Properties)


def unregister():
    del bpy.types.Scene.hta
    bpy.utils.unregister_class(HTA_Properties)
