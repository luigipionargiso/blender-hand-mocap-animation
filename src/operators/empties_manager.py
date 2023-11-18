import bpy
from ..landmarks_names import *


def create_empties_hierarchy():
    create_collections()
    create_empties()
    create_drivers_empties()


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

                bpy.data.collections["hma_EMPTIES." + handedness].objects.link(empty)

                bpy.context.collection.objects.unlink(empty)


def create_drivers_empties():
    for handedness in ["L", "R"]:
        for lmk_name in landmarks_names:
            name = lmk_name + "." + handedness + ".D"

            if name not in bpy.data.objects:
                bpy.ops.object.empty_add(type="SPHERE", radius=0.1)

                empty = bpy.context.object

                empty.name = name

                bpy.data.collections["hma_DRIVERS." + handedness].objects.link(empty)

                bpy.context.collection.objects.unlink(empty)


def set_keyframes(hma_hands, frame_number):
    for hand in hma_hands:
        for landmark in hand.landmarks:
            empty_name = landmark.name + "." + hand.handedness
            obj = bpy.data.objects[empty_name]
            obj.location = (landmark.position * 10).tolist()
            obj.rotation_euler = landmark.rotation_euler.tolist()
            obj.keyframe_insert(data_path="location", frame=frame_number)
            obj.keyframe_insert(data_path="rotation_euler", frame=frame_number)
