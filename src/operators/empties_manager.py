import bpy
import copy

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

    if "hta_pos_sx" not in bpy.data.collections:
        hta_pos_sx = bpy.data.collections.new("hta_pos_sx")
        hta_empties.children.link(hta_pos_sx)
    else:
        hta_pos_sx = bpy.data.collections["hta_pos_sx"]

    if "hta_pos_dx" not in bpy.data.collections:
        hta_pos_dx = bpy.data.collections.new("hta_pos_dx")
        hta_empties.children.link(hta_pos_dx)
    else:
        hta_pos_dx = bpy.data.collections["hta_pos_dx"]

    # Create empties
    for handedness in ["sx", "dx"]:
        for name in names:
            name_pos = handedness + "_" + name + "_pos"

            if name_pos not in bpy.data.objects:
                bpy.ops.object.empty_add(type="ARROWS", radius=0.1)

                empty = bpy.context.object

                empty.name = name_pos

                if handedness == "sx":
                    hta_pos_sx.objects.link(empty)
                else:
                    hta_pos_dx.objects.link(empty)

                bpy.context.collection.objects.unlink(empty)


def subtract_wrist_coordinates(multi_hand_landmarks):
    multi_hand_copy = copy.deepcopy(multi_hand_landmarks)

    for hand_landmarks in multi_hand_copy:
        # Get the wrist coordinates
        wrist_coordinates = hand_landmarks.landmark[0]
        for landmark in hand_landmarks.landmark:
            landmark.x -= wrist_coordinates.x
            landmark.y -= wrist_coordinates.y
            landmark.z -= wrist_coordinates.z
            landmark.x *= 10
            landmark.y *= 10
            landmark.z *= 10

    return multi_hand_copy

def set_position_keyframes(multi_hand_landmarks):
    handedness_v = ["sx", "dx"]
    try:
        for i, hand_landmarks in enumerate(multi_hand_landmarks):
            handedness = handedness_v[i]
            for j, landmark in enumerate(hand_landmarks.landmark):
                obj = bpy.data.objects[handedness + "_" + names[j] + "_pos"]
                obj.location.x = landmark.x
                obj.location.y = landmark.y
                obj.location.z = landmark.z
                obj.keyframe_insert(data_path="location", frame=1)
    except KeyError:
        print(f"No object named in the current scene.")
