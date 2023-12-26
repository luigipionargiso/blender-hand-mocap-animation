# Hand Mocap Animation for Blender

A Blender addon to perform markerless tracking of hand fingers.
<br><br>
This addon was realized as project assignment for the *Image Processing and Computer Vision* course at the *Politecnico di Torino*.
<br>
It is inspired by cgtinker's [BlenderArMocap](https://github.com/cgtinker/BlendArMocap/).

## Features
- Hand markerless tracking from camera video stream using Google’s [Mediapipe](https://google.github.io/mediapipe/).
- Smoothing of the fingers positions over time using Scipy's *Savitzky–Golay filter*.
- Tranfer animation to [Rigify](https://docs.blender.org/manual/en/latest/addons/rigging/rigify/index.html)'s rigs using metarig default naming convention.

## Installation for Windows
You can install this addon as any other Blender addon by going to *Edit > Preferences > Add-ons > Install* and selecting the addon zip file.
<br>You can get the zip file by downloading this repository as a zip file.
<br><br>
However you need to install some external dependencies to make it work. Specifically the ones in the `requirements.txt` file:
````
opencv-contrib-python>=4.7
mediapipe>=0.9
numpy>=1.26
scipy>=1.11
````
You can install them manually by opening Blender and going to the *Scripting* tab or simply opening a Python console in Blender.
<br>In the console type and execute:
```console
import sys; sys.executable
```
It will print the Blender's Python location in you disk.
Finally open a Command Prompt terminal and execute:
```console
<blender-python-location> -m pip install <path-to-requirement.txt>
```

## Limitations
This addon was tested only in Blender 3.6 for Windows.