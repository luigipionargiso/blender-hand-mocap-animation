import bpy
import numpy as np
from ..landmarks_names import *


def create_empties_hierarchy():
    create_collections()
    create_empties()
    create_drivers_empties()

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

                add_map_range_values_as_custom_properties(empty)


def add_map_range_values_as_custom_properties(obj):
    if "wrist" in obj.name:
        return
    elif "tip" in obj.name:
        return
    elif "thumb_mcp" in obj.name:
        obj["from_min_z"] = np.deg2rad(-10.0)
        obj["from_max_z"] = np.deg2rad(10.0)
        obj["to_min_z"] = np.deg2rad(-40.0)
        obj["to_max_z"] = np.deg2rad(40.0)
    elif "thumb_ip" in obj.name:
        obj["from_min_z"] = np.deg2rad(-10.0)
        obj["from_max_z"] = np.deg2rad(20.0)
        obj["to_min_z"] = np.deg2rad(-30.0)
        obj["to_max_z"] = np.deg2rad(90.0)
    elif "mcp" in obj.name:
        obj["from_min_z"] = np.deg2rad(-4.0)
        obj["from_max_z"] = np.deg2rad(110.0)
        obj["to_min_z"] = np.deg2rad(-40.0)
        obj["to_max_z"] = np.deg2rad(90.0)
        obj["from_min_x"] = np.deg2rad(-5.0)
        obj["from_max_x"] = np.deg2rad(5.0)
        obj["to_min_x"] = np.deg2rad(-20.0)
        obj["to_max_x"] = np.deg2rad(20.0)
    elif "cmc" in obj.name:
        obj["from_min_z"] = np.deg2rad(-20.0)
        obj["from_max_z"] = 0.0
        obj["to_min_z"] = np.deg2rad(-45.0)
        obj["to_max_z"] = np.deg2rad(20.0)
        obj["from_min_x"] = np.deg2rad(2.0)
        obj["from_max_x"] = np.deg2rad(16.0)
        obj["to_min_x"] = np.deg2rad(-30.0)
        obj["to_max_x"] = np.deg2rad(30.0)
    else:
        obj["from_min_z"] = np.deg2rad(5.0)
        obj["from_max_z"] = np.deg2rad(130.0)
        obj["to_min_z"] = np.deg2rad(0.0)
        obj["to_max_z"] = np.deg2rad(90.0)


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
    elif "thumb_mcp" in obj.name:
        pass
    elif "mcp" in obj.name or "cmc" in obj.name:
        add_driver_to_rotation(obj, "x")

    add_driver_to_rotation(obj, "z")


def add_driver_to_rotation(obj, axis):
    if axis == "x":
        driver = obj.driver_add("rotation_euler", 0).driver
    else:
        driver = obj.driver_add("rotation_euler", 2).driver

    driver.type = "SCRIPTED"
    driver.expression = (
        f"(( (value-2*pi ) if value > pi else value )-from_min_{axis})"
        f"*(to_max_{axis}-to_min_{axis})"
        f"/(from_max_{axis}-from_min_{axis})+to_min_{axis}"
    )

    target_obj = bpy.data.objects[obj.name[:-2]]

    value = driver.variables.new()
    value.name = "value"
    value.targets[0].id = target_obj
    value.targets[0].data_path = f"rotation_euler.{axis}"

    from_min = driver.variables.new()
    from_min.name = f"from_min_{axis}"
    from_min.targets[0].id = target_obj
    from_min.targets[0].data_path = f'["from_min_{axis}"]'

    from_max = driver.variables.new()
    from_max.name = f"from_max_{axis}"
    from_max.targets[0].id = target_obj
    from_max.targets[0].data_path = f'["from_max_{axis}"]'

    to_min = driver.variables.new()
    to_min.name = f"to_min_{axis}"
    to_min.targets[0].id = target_obj
    to_min.targets[0].data_path = f'["to_min_{axis}"]'

    to_max = driver.variables.new()
    to_max.name = f"to_max_{axis}"
    to_max.targets[0].id = target_obj
    to_max.targets[0].data_path = f'["to_max_{axis}"]'


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

            rotation = bpy.data.objects[empty_name].rotation_euler.copy()

            rig.pose.bones[bone_name + "." + handedness].rotation_euler = [
                rotation[2],
                rotation[1],
                rotation[0],
            ]
