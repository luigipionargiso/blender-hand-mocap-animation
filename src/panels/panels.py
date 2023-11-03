import bpy


class HTA_Base_Panel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Hand Tracking Animation"


class HTA_PT_Main_Panel(HTA_Base_Panel, bpy.types.Panel):
    bl_idname = "UI_PT_main_panel"
    bl_label = "Hand Tracking Animation"

    def draw(self, context):
        pass


class HTA_PT_Tracking_Panel(HTA_Base_Panel, bpy.types.Panel):
    bl_parent_id = "UI_PT_main_panel"
    bl_label = "Tracking"

    def draw(self, context):
        layout = self.layout
        user = context.scene.hta

        layout.prop(user, "camera_device_slot")
        layout.prop(user, "skip_frames")

        if user.modal_is_active:
            layout.operator(
                "hta.tracking_operator", text="Stop recording", icon="RADIOBUT_ON"
            )
        else:
            layout.operator(
                "hta.tracking_operator", text="Start recording", icon="RADIOBUT_OFF"
            )


class HTA_PT_Transfer_Panel(HTA_Base_Panel, bpy.types.Panel):
    bl_parent_id = "UI_PT_main_panel"
    bl_label = "Transfer animation"

    def draw(self, context):
        layout = self.layout
        user = context.scene.hta

        # Armature object picker
        layout.prop_search(
            data=user,
            property="selected_rig",
            search_data=bpy.data,
            search_property="objects",
            icon="ARMATURE_DATA",
        )

        # Collection selector
        layout.prop_search(
            data=user,
            property="drivers_collection",
            search_data=bpy.data,
            search_property="collections",
        )


classes = [HTA_PT_Main_Panel, HTA_PT_Tracking_Panel, HTA_PT_Transfer_Panel]


def register():
    for cls in classes:
        if cls is None:
            continue
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        if cls is None:
            continue
        bpy.utils.unregister_class(cls)
