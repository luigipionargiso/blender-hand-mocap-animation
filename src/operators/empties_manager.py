import bpy


def create_empty_in_collection():
    names = [
        "wrist",
        "thumb_cmc",
        "thumb_mcp",
        "thumb_ip",
        "thumb_tip",
        "index_finger_mcp",
        "index_finger_pip",
        "index_finger_dip",
        "index_finger_tip",
        "middle_finger_mcp",
        "middle_finger_pip",
        "middle_finger_dip",
        "middle_finger_tip",
        "ring_finger_mcp",
        "ring_finger_pip",
        "ring_finger_dip",
        "ring_finger_tip",
        "pinky_mcp",
        "pinky_pip",
        "pinky_dip",
        "pinky_tip",
    ]


        # Check if the 'hta_empties' collection exists
    if 'hta_empties' not in bpy.data.collections:
        # If not, create a new collection named 'hta_empties'
        hta_empties = bpy.data.collections.new('hta_empties')
        bpy.context.scene.collection.children.link(hta_empties)
    else:
        # If it exists, get the 'hta_empties' collection
        hta_empties = bpy.data.collections['hta_empties']

    # Check if the 'hta_pos' collection exists
    if 'hta_pos' not in bpy.data.collections:
        # If not, create a new collection named 'hta_pos'
        hta_pos = bpy.data.collections.new('hta_pos')
        # Link 'hta_pos' to 'hta_empties', making 'hta_pos' a child of 'hta_empties'
        hta_empties.children.link(hta_pos)
    else:
        # If it exists, get the 'hta_pos' collection
        hta_pos = bpy.data.collections['hta_pos']

    # Create empties
    for name in names:
        #name = name + "_pos"

        if name not in bpy.data.objects:
            bpy.ops.object.empty_add(type="ARROWS", radius=0.1)

            empty = bpy.context.object

            empty.name = name

            hta_pos.objects.link(empty)

            bpy.context.collection.objects.unlink(empty)
