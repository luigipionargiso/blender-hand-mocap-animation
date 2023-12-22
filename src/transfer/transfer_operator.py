import bpy
from .transfer_utilities import *


class HMA_OT_TransferOperator(bpy.types.Operator):
    """Set the bone constraints"""

    bl_idname = "hma.transfer_operator"
    bl_label = "Transfer animation"

    @classmethod
    def poll(cls, context):
        user = context.scene.hma
        return user.drivers_collection is not None and user.selected_rig is not None

    def execute(self, context):
        try:
            set_bone_constraints()
        except Exception as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        
        return {"FINISHED"}


def register():
    bpy.utils.register_class(HMA_OT_TransferOperator)


def unregister():
    bpy.utils.unregister_class(HMA_OT_TransferOperator)
