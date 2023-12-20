from .src import hma_properties
from .src.tracking_operator import tracking_operator
from .src.panels import panels


bl_info = {
    "name": "Hand Mocap Animation",
    "author": "Luigi Pio Nargiso",
    "description": "A simple addon that uses markerless hand tracking to animate fingers in rigs",
    "blender": (3, 0, 0),
    "version": (0, 0, 1),
    "location": "3D View > Tool",
    "warning": "",
    "category": "Animation",
}

modules = [hma_properties, tracking_operator, panels]


def register():
    for mod in modules:
        if mod is None:
            continue
        mod.register()


def unregister():
    for mod in reversed(modules):
        if mod is None:
            continue
        mod.unregister()
