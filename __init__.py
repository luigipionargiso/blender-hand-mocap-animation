from .src.panels import panels_registration
from .src import hta_properties


bl_info = {
    "name": "Hand tracking animate",
    "author": "Luigi Pio Nargiso",
    "description": "",
    "blender": (3, 0, 0),
    "version": (0, 0, 1),
    "location": "3D View > Tool",
    "warning": "",
    "category": "Animation",
}

classes = [hta_properties, panels_registration]


def register():
    for cls in classes:
        if cls is None:
            continue
        cls.register()


def unregister():
    for cls in reversed(classes):
        if cls is None:
            continue
        cls.unregister()
