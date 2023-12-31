import numpy as np
import mathutils
from ..hma_data import landmarks_names


def copy_to_hma_custom_structure(mp_results):
    if mp_results is None or mp_results.multi_hand_world_landmarks is None:
        return []

    mp_multi_hand = mp_results.multi_hand_world_landmarks

    hma_hands = []

    # iterate through hands
    for i, mp_hand_landmarks in enumerate(mp_multi_hand):
        # get handedness
        if mp_results.multi_handedness[i].classification[0].label == "Left":
            handedness = "L"
        else:
            handedness = "R"

        hma_hand_landmarks = []

        # iterate through hand landmarks
        for j, mp_landmark in enumerate(mp_hand_landmarks.landmark):
            position = np.array(
                [mp_landmark.x, mp_landmark.y, mp_landmark.z],
                dtype=HMA_Landmark.numpy_dtype,
            )
            rotation_euler = np.zeros(3)
            hma_landmark = HMA_Landmark(landmarks_names[j], position, rotation_euler)
            hma_hand_landmarks.append(hma_landmark)

        hma_hand = HMA_Hand(handedness, None, hma_hand_landmarks)
        hma_hands.append(hma_hand)

    return hma_hands


def calculate_positions(hma_hands):
    for hand in hma_hands:
        # move the origin of axis to the wrist
        wrist_position = hand.landmarks[0].position

        for landmark in hand.landmarks:
            landmark.position = np.subtract(
                landmark.position,
                wrist_position,
                dtype=HMA_Landmark.numpy_dtype,
            )


def calculate_hands_orientation(hma_hands):
    for hand in hma_hands:
        # middle finger mcp, ring finger mcp and wrist lie on the local yz plane
        ring_mcp = hand.landmarks[13].position
        ring_mcp_norm = ring_mcp / np.linalg.norm(ring_mcp)

        middle_mcp = hand.landmarks[9].position
        middle_mcp_norm = middle_mcp / np.linalg.norm(middle_mcp)

        # use the distance vector from the wrist to the middle finger as local y axis
        forward = middle_mcp_norm

        # the up (x) vector comes out of the palm
        up = np.cross(ring_mcp_norm, forward)

        # the right (z) vector points to the thumb
        right = np.cross(up, forward)

        # use a left-handed coordinate system for the left hand
        if hand.handedness == "L":
            up *= -1.0
            right *= -1.0

        # return a rotation matrix to change to local coordinate system
        hand.orientation = np.column_stack((up, forward, right))


def calculate_rotations(hma_hands):
    x_axis = np.array([1.0, 0.0, 0.0])
    y_axis = np.array([0.0, 1.0, 0.0])
    z_axis = np.array([0.0, 0.0, 1.0])

    for hand in hma_hands:
        for i, landmark in enumerate(hand.landmarks):
            # the wrist rotation matches the hand orientation
            if landmark.name == "wrist":
                matrix_data = hand.orientation.tolist()
                rotation_euler = mathutils.Matrix(matrix_data).to_euler()
                landmark.rotation_euler = np.array(rotation_euler)

            # calculate thumb phalanxes rotations
            elif "thumb" in landmark.name:
                calculate_thumb_rotations(landmark, i, hand)

            # calculate all the other phalanxes rotations
            elif "mcp" in landmark.name:
                prox_phalanx = hand.landmarks[i + 1].position - landmark.position

                # get the local coordinates
                prox_phalanx = np.matmul(prox_phalanx, hand.orientation)

                # calculate rotation around z axis
                proj_xy = np.array([prox_phalanx[0], prox_phalanx[1], 0.0])

                z_angle = np.arctan2(
                    np.dot(np.cross(proj_xy, y_axis), z_axis),
                    np.dot(proj_xy, y_axis),
                )

                # calculate rotation around x axis

                rotation_matrix = np.array(
                    [
                        [np.cos(-z_angle), -np.sin(-z_angle), 0],
                        [np.sin(-z_angle), np.cos(-z_angle), 0],
                        [0, 0, 1],
                    ]
                )

                # rotate the vector until it is on xy plane
                rotated_phalanx = np.matmul(prox_phalanx, rotation_matrix)

                x_angle = np.arctan2(
                    np.dot(np.cross(rotated_phalanx, y_axis), x_axis),
                    np.dot(rotated_phalanx, y_axis),
                )

                landmark.rotation_euler = np.array([x_angle, 0.0, z_angle])

            elif "pip" in landmark.name:
                # calculate the angle between the current and the previous phalanx
                middle_phalanx = hand.landmarks[i + 1].position - landmark.position
                prox_phalanx = landmark.position - hand.landmarks[i - 1].position

                middle_phalanx /= np.linalg.norm(middle_phalanx)
                prox_phalanx /= np.linalg.norm(prox_phalanx)

                cross = np.cross(middle_phalanx, prox_phalanx)
                z_angle = np.arcsin(np.linalg.norm(cross))
                right = hand.orientation[:, [2]]
                if np.dot(cross, right) < 0:
                    z_angle *= -1

                landmark.rotation_euler = np.array([0.0, 0.0, z_angle])

            elif "dip" in landmark.name:
                # calculate the angle between the current and the previous phalanx
                dist_phalanx = hand.landmarks[i + 1].position - landmark.position
                middle_phalanx = landmark.position - hand.landmarks[i - 1].position

                dist_phalanx /= np.linalg.norm(dist_phalanx)
                middle_phalanx /= np.linalg.norm(middle_phalanx)

                cross = np.cross(dist_phalanx, middle_phalanx)
                z_angle = np.arcsin(np.linalg.norm(cross))
                right = hand.orientation[:, [2]]
                if np.dot(cross, right) < 0:
                    z_angle *= -1

                landmark.rotation_euler = np.array([0, 0, z_angle])


def calculate_thumb_rotations(landmark, index, hand):
    x_axis = np.array([1.0, 0.0, 0.0])
    y_axis = np.array([0.0, 1.0, 0.0])
    z_axis = np.array([0.0, 0.0, 1.0])

    if "cmc" in landmark.name:
        metacarpal = hand.landmarks[index + 1].position - landmark.position

        # get the local coordinates
        metacarpal = np.matmul(metacarpal, hand.orientation)

        proj_xy = np.array([metacarpal[0], metacarpal[1], 0.0])
        proj_yz = np.array([0.0, metacarpal[1], metacarpal[2]])

        z_angle = np.arctan2(
            np.dot(np.cross(proj_xy, y_axis), z_axis),
            np.dot(proj_xy, y_axis),
        )
        x_angle = np.arctan2(
            np.dot(np.cross(proj_yz, y_axis), x_axis),
            np.dot(proj_yz, y_axis),
        )

        if hand.handedness == "L":
            x_angle *= -1.0
        elif hand.handedness == "R":
            z_angle *= -1.0

        landmark.rotation_euler = np.array([x_angle, 0.0, z_angle])

    elif "mcp" in landmark.name:
        # calculate the angle between the current and the previous phalanx
        prox_phalanx = hand.landmarks[index + 1].position - landmark.position
        metacarpal = landmark.position - hand.landmarks[index - 1].position

        prox_phalanx /= np.linalg.norm(prox_phalanx)
        metacarpal /= np.linalg.norm(metacarpal)

        cross = np.cross(prox_phalanx, metacarpal)
        x_angle = np.arcsin(np.linalg.norm(cross))
        up = hand.orientation[:, [0]]
        if np.dot(cross, up) > 0:
            x_angle *= -1

        if hand.handedness == "R":
            x_angle *= -1.0

        landmark.rotation_euler = np.array([x_angle, 0.0, 0.0])

    elif "_ip" in landmark.name:
        # calculate the angle between the current and the previous phalanx
        dist_phalanx = hand.landmarks[index + 1].position - landmark.position
        prox_phalanx = landmark.position - hand.landmarks[index - 1].position

        dist_phalanx /= np.linalg.norm(dist_phalanx)
        prox_phalanx /= np.linalg.norm(prox_phalanx)

        cross = np.cross(dist_phalanx, prox_phalanx)
        x_angle = np.arcsin(np.linalg.norm(cross))
        up = hand.orientation[:, [0]]
        if np.dot(cross, up) > 0:
            x_angle *= -1

        if hand.handedness == "R":
            x_angle *= -1.0

        landmark.rotation_euler = np.array([x_angle, 0.0, 0.0])


class HMA_Hand:
    def __init__(self, handedness, orientation, landmarks):
        self.handedness = handedness
        self.orientation = orientation
        self.landmarks = landmarks


class HMA_Landmark:
    numpy_dtype = np.float32

    def __init__(self, name, position, rotation):
        self.name = name
        self.position = position
        self.rotation_euler = rotation
