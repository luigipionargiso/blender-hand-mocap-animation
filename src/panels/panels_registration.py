from . import default_panel, tracking_panel, transfer_panel

classes = [default_panel, tracking_panel, transfer_panel]


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
