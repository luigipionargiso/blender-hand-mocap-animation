import bpy
from .default_panel import DefaultPanel


class TrackingPanel(DefaultPanel, bpy.types.Panel):
    bl_label = "Tracking"
    bl_parent_id = "hta_default_panel"
    bl_idname = "hta_trackingpanel"

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene.hta, "camera_device_slot")
        layout.prop(context.scene.hta, "skip_frames")


def register():
    bpy.utils.register_class(TrackingPanel)


def unregister():
    bpy.utils.unregister_class(TrackingPanel)
