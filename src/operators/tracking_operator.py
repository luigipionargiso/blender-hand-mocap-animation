import bpy
import cv2 as cv
import mediapipe as mp
from .empties_manager import *


class HTA_OT_TrackingOperator(bpy.types.Operator):
    """Toggle the tracking window"""

    bl_idname = "hta.tracking_operator"
    bl_label = "Start tracking"

    _timer = None
    _cap = None

    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    _hands = None

    @classmethod
    def poll(cls, context):
        return context.mode in {"OBJECT", "POSE"}

    def modal(self, context, event):
        if event.type == "TIMER":
            success, frame = self._cap.read()
            # if success:
            #    cv.imshow("Camera stream", frame)
            if not success:
                print("Ignoring empty camera frame.")
                return {"PASS_THROUGH"}

            # Flip the image horizontally for a later selfie-view display, and convert
            # the BGR image to RGB.
            frame = cv.cvtColor(cv.flip(frame, 1), cv.COLOR_BGR2RGB)
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            frame.flags.writeable = False
            results = self._hands.process(frame)

            # Draw the hand annotations on the image.
            frame.flags.writeable = True
            frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
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

        actual_fps = context.scene.render.fps / context.scene.render.fps_base
        frame_duration = 1 / actual_fps
        if user.skip_frames > 0:
            frame_duration = user.skip_frames * frame_duration
        self._timer = context.window_manager.event_timer_add(
            frame_duration, window=context.window
        )

        # Create a hands object
        self._hands = self.mp_hands.Hands(
            min_detection_confidence=0.5, min_tracking_confidence=0.5
        )

        # Call the __enter__() method
        self._hands.__enter__()

        create_empty_in_collection()

        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        self._cap.release()
        cv.destroyAllWindows()
        context.scene.hta.modal_is_active = False
        self._hands.__exit__(None, None, None)


def register():
    bpy.utils.register_class(HTA_OT_TrackingOperator)


def unregister():
    bpy.utils.unregister_class(HTA_OT_TrackingOperator)