import numpy as np
from scipy.signal import savgol_filter

landmarks_history = []


def smooth_landmarks_over_time(landmarks, window_size=15, poly_order=3):
    global landmarks_history

    # Convert landmarks to numpy array and add to history
    landmarks_np = np.array([(lm.x, lm.y, lm.z) for lm in landmarks.landmark])
    landmarks_history.append(landmarks_np)

    if len(landmarks_history) >= window_size:
        # Concatenate the history into an multidimensional array
        # the first dimension is the frame,
        # the second dimension is the landmark, and the third dimension is the coordinate (x, y, z)
        history_np = np.stack(landmarks_history[-window_size:], axis=0)

        # Apply Savitzky-Golay filter to smooth the landmarks
        smoothed_landmarks = savgol_filter(history_np, window_size, poly_order, axis=0)

        # Update the landmarks with the smoothed values from the last frame
        for i, lm in enumerate(landmarks.landmark):
            lm.x = smoothed_landmarks[-1, i, 0]
            lm.y = smoothed_landmarks[-1, i, 1]
            lm.z = smoothed_landmarks[-1, i, 2]

        landmarks_history.pop(0)

    return landmarks
