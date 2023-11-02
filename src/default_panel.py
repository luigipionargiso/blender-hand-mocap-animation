import bpy


class DefaultPanel(bpy.types.Panel):
    bl_label = "Hand Tracking Animate"
    bl_idname = "hta_default_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hand Tracking Animate"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    def draw(self, context):
        pass


def register():
    bpy.utils.register_class(DefaultPanel)


def unregister():
    bpy.utils.unregister_class(DefaultPanel)
