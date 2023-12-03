import bpy
import numpy as np
from ..landmarks_names import *


def create_empties_hierarchy():
    create_collections()
    create_empties()
    create_drivers_empties()
    tune_rotations()

    # force drivers dependencies update
    for obj in bpy.context.scene.objects:
        obj.hide_render = obj.hide_render


def create_collections():
    if "HAND_MOCAP_ANIMATION" not in bpy.data.collections:
        hma = bpy.data.collections.new("HAND_MOCAP_ANIMATION")
        bpy.context.scene.collection.children.link(hma)

    if "hma_EMPTIES.L" not in bpy.data.collections:
        hma_empties_L = bpy.data.collections.new("hma_EMPTIES.L")
        hma.children.link(hma_empties_L)

    if "hma_EMPTIES.R" not in bpy.data.collections:
        hma_empties_R = bpy.data.collections.new("hma_EMPTIES.R")
        hma.children.link(hma_empties_R)

    if "hma_DRIVERS.L" not in bpy.data.collections:
        hma_drivers_L = bpy.data.collections.new("hma_DRIVERS.L")
        hma.children.link(hma_drivers_L)

    if "hma_DRIVERS.R" not in bpy.data.collections:
        hma_drivers_R = bpy.data.collections.new("hma_DRIVERS.R")
        hma.children.link(hma_drivers_R)


def create_empties():
    for handedness in ["L", "R"]:
        for lmk_name in landmarks_names:
            name = lmk_name + "." + handedness

            if lmk_name == "wrist":
                empty_radius = 0.5
            else:
                empty_radius = 0.05

            if name not in bpy.data.objects:
                bpy.ops.object.empty_add(type="ARROWS", radius=empty_radius)

                empty = bpy.context.object
                empty.name = name

                if "wrist" in name and handedness == "L":
                    empty.scale = [1.0, 1.0, -1.0]

                # add to the right collection
                bpy.data.collections["hma_EMPTIES." + handedness].objects.link(empty)
                # remove from the scene collection
                bpy.context.collection.objects.unlink(empty)

                add_custom_properties(empty)


def add_custom_properties(obj):
    if "wrist" in obj.name:
        return
    elif "tip" in obj.name:
        return
    elif "thumb_mcp" in obj.name or "thumb_ip" in obj.name:
        obj["Scale X"] = 1.0
        obj["Offset X"] = 0.0
    elif "thumb_cmc" in obj.name or "mcp" in obj.name:
        obj["Scale X"] = 1.0
        obj["Offset X"] = 0.0
        obj["Scale Z"] = 1.0
        obj["Offset Z"] = 0.0
    else:
        obj["Scale Z"] = 1.0
        obj["Offset Z"] = 0.0


def create_drivers_empties():
    for handedness in ["L", "R"]:
        for lmk_name in landmarks_names:
            name = lmk_name + "." + handedness + ".D"

            if name not in bpy.data.objects:
                bpy.ops.object.empty_add(type="SPHERE", radius=0.1)

                empty = bpy.context.object
                empty.name = name

                # add to the appropriate collection
                bpy.data.collections["hma_DRIVERS." + handedness].objects.link(empty)
                # remove from the scene collection
                bpy.context.collection.objects.unlink(empty)

                add_drivers(empty)


def add_drivers(obj):
    if "wrist" in obj.name:
        return
    elif "tip" in obj.name:
        return
    elif "thumb_mcp" in obj.name or "thumb_ip" in obj.name:
        add_driver_to_rotation(obj, "X")
    elif "thumb_cmc" in obj.name or "mcp" in obj.name:
        add_driver_to_rotation(obj, "X")
        add_driver_to_rotation(obj, "Z")
    else:
        add_driver_to_rotation(obj, "Z")


def add_driver_to_rotation(obj, axis):
    if axis == "X":
        driver = obj.driver_add("rotation_euler", 0).driver
    else:
        driver = obj.driver_add("rotation_euler", 2).driver

    driver.type = "SCRIPTED"
    driver.expression = f"(scale_{axis} * value) + radians(offset_{axis})"

    target_obj = bpy.data.objects[obj.name[:-2]]

    value = driver.variables.new()
    value.name = "value"
    value.targets[0].id = target_obj
    value.targets[0].data_path = f"rotation_euler.{axis}".lower()

    scale = driver.variables.new()
    scale.name = f"scale_{axis}"
    scale.targets[0].id = target_obj
    scale.targets[0].data_path = f'["Scale {axis}"]'

    offset = driver.variables.new()
    offset.name = f"offset_{axis}"
    offset.targets[0].id = target_obj
    offset.targets[0].data_path = f'["Offset {axis}"]'


def tune_rotations():
    objs = bpy.data.objects
    for handedness in ["L", "R"]:
        for finger in ["index_finger", "middle_finger", "ring_finger", "pinky"]:
            objs[finger + "_mcp." + handedness]["Offset Z"] = -20.0
            objs[finger + "_mcp." + handedness]["Scale X"] = 1.5
            objs[finger + "_mcp." + handedness]["Offset X"] = 5.0

    objs["thumb_cmc.L"]["Scale Z"] = 2.0
    objs["thumb_cmc.L"]["Offset Z"] = -20.0
    objs["thumb_cmc.R"]["Scale Z"] = 2.0
    objs["thumb_cmc.R"]["Offset Z"] = 20.0


def set_keyframes(hma_hands, frame_number):
    for hand in hma_hands:
        for landmark in hand.landmarks:
            empty_name = landmark.name + "." + hand.handedness
            obj = bpy.data.objects[empty_name]

            # multiply position by 10 for visualization
            obj.location = (landmark.position * 10).tolist()
            obj.rotation_euler = landmark.rotation_euler.tolist()

            obj.keyframe_insert(data_path="location", frame=frame_number)
            obj.keyframe_insert(data_path="rotation_euler", frame=frame_number)


def demo_rotate_bones():
    bones = {
        "thumb.01": "thumb_cmc",
        "thumb.02": "thumb_mcp",
        "thumb.03": "thumb_ip",
        "f_index.01": "index_finger_mcp",
        "f_index.02": "index_finger_pip",
        "f_index.03": "index_finger_dip",
        "f_middle.01": "middle_finger_mcp",
        "f_middle.02": "middle_finger_pip",
        "f_middle.03": "middle_finger_dip",
        "f_ring.01": "ring_finger_mcp",
        "f_ring.02": "ring_finger_pip",
        "f_ring.03": "ring_finger_dip",
        "f_pinky.01": "pinky_mcp",
        "f_pinky.02": "pinky_pip",
        "f_pinky.03": "pinky_dip",
    }
    rig = bpy.data.objects["metarig"]
    for handedness in ["L", "R"]:
        for bone_name, lmk_name in bones.items():
            empty_name = lmk_name + "." + handedness + ".D"

            hma_rot = bpy.data.objects[empty_name].rotation_euler

            if "thumb" in bone_name:
                rig.pose.bones[bone_name + "." + handedness].rotation_euler = hma_rot
            else:
                rig.pose.bones[bone_name + "." + handedness].rotation_euler = [
                    hma_rot[2],
                    hma_rot[1],
                    hma_rot[0],
                ]
