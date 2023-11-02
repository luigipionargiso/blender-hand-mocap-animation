import bpy
from .default_panel import DefaultPanel


class TranferPanel(DefaultPanel, bpy.types.Panel):
    bl_label = "Transfer animation"
    bl_parent_id = "hta_default_panel"
    bl_idname = "hta_transferpanel"

    def draw(self, context):
        layout = self.layout

        # Armature object picker
        layout.prop_search(
            data=context.scene.hta,
            property="selected_rig",
            search_data=bpy.data,
            search_property="objects",
            icon="ARMATURE_DATA",
        )

        # Collection selector
        layout.prop_search(
            data=context.scene.hta,
            property="drivers_collection",
            search_data=bpy.data,
            search_property="collections",
        )


def register():
    bpy.utils.register_class(TranferPanel)


def unregister():
    bpy.utils.unregister_class(TranferPanel)
