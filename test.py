import bpy
import sys
import os
#grabs the folder from the command line
folder = sys.argv[5]

#looks for a csv and a glb file in the folder
for file in os.listdir(folder):
    if file.endswith(".csv"):
        csv_file = os.path.join(folder, file)
    if file.endswith(".glb"):
        glb_file = os.path.join(folder, file)

print(csv_file, glb_file)

for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)

# import glb
bpy.ops.import_scene.gltf(filepath=glb_file)

#save to <folder>/output.blend
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(folder, "output.blend"))
