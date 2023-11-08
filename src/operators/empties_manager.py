import bpy
import numpy as np
import mathutils

names = [
    "wrist",
    "thumb_cmc",
    "thumb_mcp",
    "thumb_ip",
    "thumb_tip",
    "index_finger_mcp",
    "index_finger_pip",
    "index_finger_dip",
    "index_finger_tip",
    "middle_finger_mcp",
    "middle_finger_pip",
    "middle_finger_dip",
    "middle_finger_tip",
    "ring_finger_mcp",
    "ring_finger_pip",
    "ring_finger_dip",
    "ring_finger_tip",
    "pinky_mcp",
    "pinky_pip",
    "pinky_dip",
    "pinky_tip",
]


def create_empty_in_collection():
    if "hta_empties" not in bpy.data.collections:
        hta_empties = bpy.data.collections.new("hta_empties")
        bpy.context.scene.collection.children.link(hta_empties)
    else:
        hta_empties = bpy.data.collections["hta_empties"]

    if "hta_pos.L" not in bpy.data.collections:
        hta_pos_L = bpy.data.collections.new("hta_pos.L")
        hta_empties.children.link(hta_pos_L)
    else:
        hta_pos_L = bpy.data.collections["hta_pos.L"]

    if "hta_pos.R" not in bpy.data.collections:
        hta_pos_R = bpy.data.collections.new("hta_pos.R")
        hta_empties.children.link(hta_pos_R)
    else:
        hta_pos_R = bpy.data.collections["hta_pos.R"]

    # Create empties
    for handedness in ["L", "R"]:
        for name in names:
            name_pos = name + "." + handedness

            if name == "wrist":
                empty_radius = 0.5
            else:
                empty_radius = 0.05

            if name_pos not in bpy.data.objects:
                bpy.ops.object.empty_add(type="ARROWS", radius=empty_radius)

                empty = bpy.context.object

                empty.name = name_pos

                bpy.data.collections["hta_pos." + handedness].objects.link(empty)

                bpy.context.collection.objects.unlink(empty)


def copy_to_hta_custom_structure(mp_results):
    if mp_results is None or mp_results.multi_hand_world_landmarks is None:
        return []

    mp_multi_hand = mp_results.multi_hand_world_landmarks

    hta_hands = []

    for i, mp_hand_landmarks in enumerate(mp_multi_hand):
        if mp_results.multi_handedness[i].classification[0].label == "Left":
            handedness = "L"
        else:
            handedness = "R"

        hta_landmarks_list = []

        for j, mp_landmark in enumerate(mp_hand_landmarks.landmark):
            position = np.array(
                [mp_landmark.x, mp_landmark.y, mp_landmark.z],
                dtype=HTA_Landmark.numpy_dtype,
            )
            rotation = np.zeros(3)
            hta_landmark = HTA_Landmark(names[j], position, rotation)
            hta_landmarks_list.append(hta_landmark)

        hta_single_hand = HTA_Hand(handedness, None, hta_landmarks_list)
        hta_hands.append(hta_single_hand)

    return hta_hands


def calculate_positions(hta_hands):
    for hand in hta_hands:
        wrist_position = hand.landmarks[0].position

        for landmark in hand.landmarks:
            landmark.position = np.subtract(
                landmark.position,
                wrist_position,
                dtype=HTA_Landmark.numpy_dtype,
            )

    return hta_hands


def calculate_hands_orientation(hta_hands):
    for hand in hta_hands:
        ring_mcp_v = hand.landmarks[13].position
        ring_mcp_v = ring_mcp_v / np.linalg.norm(ring_mcp_v)

        middle_mcp_v = hand.landmarks[9].position
        middle_mcp_v = middle_mcp_v / np.linalg.norm(middle_mcp_v)

        forward = middle_mcp_v
        up = np.cross(forward, ring_mcp_v)
        right = np.cross(forward, up)

        matrix_data = [
            [up[0], forward[0], -right[0], 0.0],
            [up[1], forward[1], -right[1], 0.0],
            [up[2], forward[2], -right[2], 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]

        hand.orientation = matrix_data

        # set empty rotation for visualization

        obj = bpy.data.objects["wrist." + hand.handedness]
        obj.rotation_euler = mathutils.Matrix(matrix_data).to_euler()

        bpy.context.view_layer.update()


def set_position_keyframes(hta_hands_landmarks_list, frame_number):
    try:
        for hta_hand_landmarks in hta_hands_landmarks_list:
            for hta_landmark in hta_hand_landmarks.landmarks:
                empty_name = hta_landmark.name + "." + hta_hand_landmarks.handedness
                obj = bpy.data.objects[empty_name]
                obj.location.x = hta_landmark.position[0] * 10
                obj.location.y = hta_landmark.position[1] * 10
                obj.location.z = hta_landmark.position[2] * 10
                obj.keyframe_insert(data_path="location", frame=frame_number)
    except KeyError:
        print(f"No object named in the current scene.")


class HTA_Hand:
    def __init__(self, handedness, orientation, landmarks):
        self.handedness = handedness
        self.orientation = orientation
        self.landmarks = landmarks


class HTA_Landmark:
    numpy_dtype = np.float32

    def __init__(self, name, position, rotation):
        self.name = name
        self.position = position
        self.rotation = rotation
