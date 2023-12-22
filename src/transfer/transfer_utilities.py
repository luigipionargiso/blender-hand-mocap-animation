import bpy
from ..hma_data import bone_lmk_correspondence


def set_bone_constraints():
    armature = bpy.context.scene.hma.selected_rig
    collection = bpy.context.scene.hma.drivers_collection

    for handedness in ["L", "R"]:
        for bone_name, lmk_name in bone_lmk_correspondence.items():
            # Select the target empty
            empty_name = lmk_name + "." + handedness + ".D"

            target = None
            for obj in collection.all_objects:
                if empty_name in obj.name:
                    target = obj

            if target is None:
                raise Exception(
                    "{} does not exist in the selected collection".format(empty_name)
                )

            # Go to object mode
            bpy.ops.object.mode_set(mode="OBJECT")

            # Select the armature
            bpy.ops.object.select_all(action="DESELECT")
            armature.select_set(True)
            bpy.context.view_layer.objects.active = armature

            # Go to pose mode
            bpy.ops.object.mode_set(mode="POSE")

            # Select the bone
            bpy.ops.pose.select_all(action="DESELECT")
            try:
                bone = armature.pose.bones[bone_name + "." + handedness]
            except KeyError:
                raise Exception(
                    "{} does not belong to the selected armature".format(
                        bone_name + "." + handedness
                    )
                )
            bone.bone.select = True

            # Add constraint
            constraint = bone.constraints.new("COPY_ROTATION")
            constraint.target = target
            constraint.owner_space = "LOCAL"
