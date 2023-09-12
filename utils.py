import bpy
from mathutils import Vector

# cuts the top off an object for a dollhouse view
def cut(z, importdOBJ):
    # make bounding cube
    bbox_corners = [
        importdOBJ.matrix_world @ Vector(corner) for corner in importdOBJ.bound_box
    ]
    verts = bbox_corners
    faces = [
        (0, 1, 2, 3),
        (4, 7, 6, 5),
        (0, 4, 5, 1),
        (1, 5, 6, 2),
        (2, 6, 7, 3),
        (4, 0, 3, 7),
    ]

    # assemble cube
    mesh = bpy.data.meshes.new("cubemesh")
    mesh.from_pydata(verts, [], faces)
    cube = bpy.data.objects.new("[PT]cutobj", mesh)

    cube.scale[0] = cube.scale[0] * 1.1
    cube.scale[1] = cube.scale[1] * 1.1
    cube.location[2] = cube.location[2] + z

    # boolean operation
    bpy.context.view_layer.objects.active = importdOBJ
    bpy.ops.object.modifier_add(type="BOOLEAN")
    importdOBJ.modifiers["Boolean"].operation = "DIFFERENCE"
    importdOBJ.modifiers["Boolean"].use_self = True
    importdOBJ.modifiers["Boolean"].object = cube

    # hide cube
    bpy.context.scene.collection.objects.link(cube)
    cube.parent = importdOBJ

    cube.hide_set(True)
    cube.hide_render = True

    return cube