import bpy
import cv2 as cv
import mediapipe as mp
from .core_operations import *
from .empties_manager import create_empties_hierarchy, set_keyframes
from .smoothing import smooth_landmarks_over_time


class HMA_OT_TrackingOperator(bpy.types.Operator):
    """Toggle the motion capture window"""

    bl_idname = "hma.tracking_operator"
    bl_label = "Start tracking"

    _timer = None
    _cap = None
    _hands = None
    _current_frame = None

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "POSE"}

    def modal(self, context, event):
        if event.type == "TIMER":
            success, frame = self._cap.read()

            if not success:
                print("Ignoring empty camera frame.")
                return {"PASS_THROUGH"}

            # Flip the image horizontally and convert the BGR image to RGB
            frame = cv.cvtColor(cv.flip(frame, 1), cv.COLOR_BGR2RGB)

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference
            frame.flags.writeable = False
            results = self._hands.process(frame)
            frame.flags.writeable = True

            # smoothing landmarks position
            if results.multi_hand_world_landmarks is not None:
                for hand_landmarks in results.multi_hand_world_landmarks:
                    hand_landmarks = smooth_landmarks_over_time(
                        hand_landmarks, context.scene.hta.smoothing_window_size
                    )

            hma_hands = copy_to_hma_custom_structure(results)
            calculate_positions(hma_hands)
            calculate_hands_orientation(hma_hands)
            calculate_rotations(hma_hands)

            # set position and rotation keyframes in empties
            set_keyframes(hma_hands, self._current_frame)
            self._current_frame += context.scene.hta.skip_frames + 1

            # Draw the hand annotations on the image
            frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS
                    )
            cv.imshow("Camera stream", frame)
            cv.waitKey(1)

        elif event.type in {"ESC"}:
            self.cancel(context)
            return {"CANCELLED"}

        elif cv.getWindowProperty("Camera stream", cv.WND_PROP_VISIBLE) < 1:
            self.cancel(context)
            return {"CANCELLED"}

        elif context.scene.hta.modal_is_active is False:
            self.cancel(context)
            return {"FINISHED"}

        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        user = context.scene.hta

        if user.modal_is_active is True:
            user.modal_is_active = False
            return {"FINISHED"}
        else:
            user.modal_is_active = True

        self._current_frame = 1

        # initialize OpenCV video capture
        self._cap = cv.VideoCapture(user.camera_device_slot, cv.CAP_DSHOW)

        if not self._cap.isOpened():
            self.report(
                {"ERROR"},
                "The selected index does not correspond to an existing device",
            )
            return {"CANCELLED"}

        self._cap.set(cv.CAP_PROP_FRAME_WIDTH, 720)
        self._cap.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

        cv.namedWindow("Camera stream")

        # add timer event to capture frames
        actual_fps = context.scene.render.fps / context.scene.render.fps_base
        frame_duration = 1 / actual_fps

        if user.skip_frames > 0:
            frame_duration *= user.skip_frames

        self._timer = context.window_manager.event_timer_add(
            frame_duration, window=context.window
        )

        # create a Mediapipe Hands object
        self._hands = mp.solutions.hands.Hands(
            model_complexity=1,
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._hands.__enter__()

        # spawn empties representing landmarks
        create_empties_hierarchy()

        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        self._cap.release()
        cv.destroyAllWindows()
        context.scene.hta.modal_is_active = False
        self._hands.__exit__(None, None, None)


def register():
    bpy.utils.register_class(HMA_OT_TrackingOperator)


def unregister():
    bpy.utils.unregister_class(HMA_OT_TrackingOperator)
