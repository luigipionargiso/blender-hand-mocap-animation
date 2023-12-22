"""
MIT License

Copyright (c) 2023 Luigi Pio Nargiso

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .src import hma_properties
from .src.tracking import tracking_operator
from .src.transfer import transfer_operator
from .src.panels import tool_panels


bl_info = {
    "name": "Hand Mocap Animation",
    "author": "Luigi Pio Nargiso",
    "description": "A simple addon that uses markerless hand tracking to animate fingers in rigs",
    "blender": (3, 0, 0),
    "version": (0, 1, 0),
    "location": "3D View > Tool",
    "doc_url": "https://github.com/luigipionargiso/blender-animate-hand/",
    "category": "Animation",
}

modules = [
    hma_properties,
    tracking_operator,
    transfer_operator,
    tool_panels,
]


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
