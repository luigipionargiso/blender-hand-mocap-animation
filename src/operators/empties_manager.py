import bpy
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
        pass
    elif "mcp" in obj.name or "cmc" in obj.name:
        obj["from_min_z"] = 0.0
        obj["from_max_z"] = 1.0
        obj["to_min_z"] = 0.0
        obj["to_max_z"] = 1.0

    obj["from_min_x"] = 0.0
    obj["from_max_x"] = 1.0
    obj["to_min_x"] = 0.0
    obj["to_max_x"] = 1.0


def create_drivers_empties():
    for handedness in ["L", "R"]:
        for lmk_name in landmarks_names:
            name = lmk_name + "." + handedness + ".D"

            if name not in bpy.data.objects:
                bpy.ops.object.empty_add(type="SPHERE", radius=0.1)

                empty = bpy.context.object
                empty.name = name

                # add to the right collection
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
        # add driver to z euler rotation
        add_driver_to_rotation(obj, "z")

    # add driver to x rotation euler
    add_driver_to_rotation(obj, "x")


def add_driver_to_rotation(obj, axis):
    if axis == "x":
        driver = obj.driver_add("rotation_euler", 0).driver
    else:
        driver = obj.driver_add("rotation_euler", 2).driver

    driver.type = "SCRIPTED"
    driver.expression = (
        f"(value-from_min_{axis})*(to_max_{axis}-to_min_{axis})"
        f"/(from_max_{axis}-from_min_{axis})+to_min_{axis}"
    )

    target_obj = bpy.data.objects[obj.name[:-2]]

    value = driver.variables.new()
    value.name = "value"
    value.type = "TRANSFORMS"
    value.targets[0].id = target_obj
    value.targets[0].transform_type = "ROT_X"

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
            obj.location = (landmark.position * 10).tolist()
            obj.rotation_euler = landmark.rotation_euler.tolist()
            obj.keyframe_insert(data_path="location", frame=frame_number)
            obj.keyframe_insert(data_path="rotation_euler", frame=frame_number)
