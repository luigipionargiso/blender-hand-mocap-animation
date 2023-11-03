import bpy
import cv2 as cv


class HTA_OT_TrackingOperator(bpy.types.Operator):
    """Toggle the tracking window"""
    bl_idname = "hta.tracking_operator"
    bl_label = "Start tracking"

    _timer = None
    _cap = None
    
    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}

    def modal(self, context, event):
        if event.type == "TIMER":
            if cv.getWindowProperty("Webcam", cv.WND_PROP_VISIBLE) < 1:
                self.cancel(context)
                return {"CANCELLED"}

            ret, frame = self._cap.read()
            if ret:
                cv.imshow("Webcam", frame)
            cv.waitKey(1)

        elif event.type in {"ESC"} or context.scene.hta.modal_is_active is False:
            self.cancel(context)
            return {"CANCELLED"}

        return {"PASS_THROUGH"}

    def invoke(self, context, event):
        if context.scene.hta.modal_is_active is True:
            context.scene.hta.modal_is_active = False
            return {"FINISHED"}
        else:
            context.scene.hta.modal_is_active = True

        scene = bpy.context.scene
        self._cap = cv.VideoCapture(scene.hta.camera_device_slot)
        if not self._cap.isOpened():
            self.report(
                {"ERROR"},
                "The selected index does not correspond to an existing device",
            )
            return {"CANCELLED"}
        cv.namedWindow("Webcam")

        actual_fps = scene.render.fps / scene.render.fps_base
        frame_duration = 1 / actual_fps
        if scene.hta.skip_frames > 0:
            frame_duration = scene.hta.skip_frames * frame_duration
        self._timer = context.window_manager.event_timer_add(
            frame_duration, window=context.window
        )

        context.window_manager.modal_handler_add(self)
        
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        self._cap.release()
        cv.destroyAllWindows()
        context.scene.hta.modal_is_active = False


def register():
    bpy.utils.register_class(HTA_OT_TrackingOperator)


def unregister():
    bpy.utils.unregister_class(HTA_OT_TrackingOperator)
