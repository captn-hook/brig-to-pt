import bpy
import bmesh
import sys
import os
import csv
import math
from mathutils import Vector

dcolor = (1, .25, .25)
tcolor = (.25, .25, 1)
nullcolor = (1, 1, 1)

pointsize = .25
tracerwidth = .25
headroom = 3

minopacity = 1

lift = 3

toff = 1
doff = 1

#groups
#max = 100
#groups = [0, 0.0005, 0.005, 0.02, .1, 0.5922612543706294, 1]
#colors = ["#1e62b2","#70a8fa","#c4deff","#fd8181","#fd8181","#f91010","#d10000"]

max = 25
groups = [0,0.00016000640025601025,0.003960158406336254,0.01996079843193728,0.03996159846393856,0.1999679987199488,1]
colors = ["#0000ff","#00a0ff","#02fbff","#4aff01","#fbfd00","#ff5a00","#ff0000"]

opacity = [0, .1, .2, .4, .6, .8, 1]
scale = [0, .1, .2, .4, .6, .8, 1]


for i in range(0, len(colors)):
    h = colors[i].lstrip('#')
    colors[i] = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    colors[i] = (colors[i][0] / 256, colors[i][1] / 256, colors[i][2] / 256)
    
    #opacity[i] = groups[i]
    #scale[i] = groups[i] * 3
    scale[i] = scale[i] * 3
print(colors)
    
br1 = groups[0] * max
br2 = groups[1] * max
br3 = groups[2] * max
br4 = groups[3] * max
br5 = groups[4] * max
br6 = groups[5] * max
br7 = groups[6] * max

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


def points(csv_file):
    resetSelection()

    dspawn, tspawn, transmission = datafile(csv_file)
    # create point collections
    pts = bpy.data.collections.new("[PT]Points")
    bpy.context.scene.collection.children.link(pts)

    dsc = bpy.data.collections.new("[PT]D's")
    pts.children.link(dsc)

    tsc = bpy.data.collections.new("[PT]T's")
    pts.children.link(tsc)

    spawn(dspawn, dsc, True)
    spawn(tspawn, tsc, False)

def resetSelection():
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.active_layer_collection = bpy.data.scenes[0].view_layers[0].layer_collection

def spawn(spawns, clc, dt):
    list = []

    dmat = bpy.data.materials.new(name = str("D Mat"))
    dmat.use_nodes = True
    dmat.shadow_method = 'NONE'
    dmat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (dcolor[0], dcolor[1], dcolor[2], 1)          
    tmat = bpy.data.materials.new(name = str("T Mat"))
    tmat.use_nodes = True
    tmat.shadow_method = 'NONE'
    tmat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (tcolor[0], tcolor[1], tcolor[2], 1)
          
        
      
    for i in range(len(spawns)):
         
        x, y, z = spawns[i]
        
        if dt:
            bpy.ops.mesh.primitive_cylinder_add(location=(x, y, z), depth=(pointsize * 0.4), radius=(pointsize * 0.4))
        else:
            bpy.ops.mesh.primitive_cube_add(location=(x, y, z), size=(pointsize * 0.5))
        
        new = bpy.context.active_object

        new.scale[2] = new.scale[2] * 0.5

        list.append(new)
         
        new.name = str(("D" if dt else "T") + str(i + (doff if dt else toff)))
        
        new.data.materials.append(dmat if dt else tmat)

        clc.objects.link(new)
        bpy.context.scene.collection.objects.unlink(new)

    return list

def datafile(datafilename):
    print("Data from", datafilename)
    line_count = 0
    lines = open(datafilename, "r")
    
    #assign data blocks
    dspawn = []
    tspawn = []
    transmission = []

    # TRNS,-80/14/-2,-107/27/-2,99/-27/-2
    # -78/-9/-2,1,2,3
    # 78/-17/2,4,5,6
    # -87/-14/-2,7,8,9

    twodarray = []
    length = 0

    with open(datafilename) as csv_file2:
        csv_reader2 = csv.reader(csv_file2, delimiter=',')
        for row in csv_reader2:
            twodarray.append(row)
            length += 1
            

    with open(datafilename) as csv_file:
        #get number of rows
        
        csv_reader = csv.reader(csv_file, delimiter=',')

        
        if twodarray[0][0] == "Labels":
            print("Labels", csv_reader)
            #first row and column are labels, second row and column are coordinates except for 1,1 which is coordinate system
            #second to last row is INSIGHTS, not needed
            #last row is views, spawn animated camera with keyframes at each view

            for row in csv_reader:
                print(line_count)
                if line_count == 0:
                    #skip
                    pass
                elif line_count == 1:
                    #get dspawn
                    print(row)
                    for i in range(2, len(row)):
                        print(row[i])
                        x, y, z = tuple(map(float, row[i].split('/')))
                        dspawn.append((x, y * -1, z))    
                #while not at last two rows
                elif line_count < length - 2:
                    #get tspawn
                    x, y, z = tuple(map(float, row[1].split('/')))
                    tspawn.append((x, y * -1, z))
                    #get transmission
                    for i in range(2, len(row)):
                        transmission.append(row[i])
                #do camera stuff
                elif line_count == length - 1:
                    camera_coords = []
                    for i in range(1, len(row)):
                        x, y, z = tuple(map(float, row[i].split('/')))
                        camera_coords.append((x, y * -1, z))
                    print("making camera")
                    #spawn camera
                    camera_data = bpy.data.cameras.new(name='Camera')
                    camera_object = bpy.data.objects.new('Camera', camera_data)
                    camera_object.rotation_mode = 'XYZ'
                    bpy.context.scene.collection.objects.link(camera_object)
                    #make main camera
                    bpy.context.scene.camera = camera_object
                    #set keyframes
                    for i in range(len(camera_coords)):
                        camera_object.location = camera_coords[i]
                        camera_object.keyframe_insert(data_path="location", frame=i)
                        #lookat dspawn
                        print("looking at", dspawn[i], "from", camera_coords[i])
                        look_at(camera_object, camera_coords[i], dspawn[i])
                        camera_object.keyframe_insert(data_path="rotation_euler", frame=i)
                        
                line_count += 1

            print(line_count, length)
            print(dspawn, tspawn, transmission)
            
            return dspawn, tspawn, transmission
                    
        else:
            for row in csv_reader:
                if line_count == 0:
                    #range 1 to len(row) to skip the first cell
                    for i in range(1, len(row)):

                        if "/" in row[i]:
                            x, y, z = tuple(map(float, row[i].split('/')))

                        else:
                            print(row[i] + " NOT A LOCATION")
                            x, y, z = (0.0, 0.0, 0.0)
                        #check if this * -1 is needed
                        dspawn.append((x,  y * -1, z))

                else:
                    #lines after 0 are coord,transmission,transmission,transmission,...
                    for i in range(0, len(row)):
                        if i == 0:

                            if "/" in row[i]:
                                x, y, z = tuple(map(float, row[i].split('/')))

                            else:
                                print(row[i] + " NOT A LOCATION")
                                x, y, z = (0.0, 0.0, 0.0)

                            tspawn.append((x, y * -1, z))
                            
                        else:
                            transmission.append(row[i])

                line_count += 1
            
            
            transmission = transmissionTranspose(transmission, len(dspawn))
            
            return dspawn, tspawn, transmission


def transmissionTranspose(trans, columns):

    transmission = []

    print(len(trans) / columns)
    for n in range(0, columns):
        for i in range(0, int(len(trans) / columns)):
            transmission.append(trans[columns * i + n])

    print(trans)
    print(transmission)
    return transmission

def look_at(obj_camera, loc, point):
    #https://blender.stackexchange.com/questions/5210/pointing-the-camera-in-a-particular-direction-programmatically
    loc_camera = Vector(loc) # obj_camera.matrix_world.to_translation()

    point = Vector(point) # target location
    print(point, loc_camera)
    
    direction = point - loc_camera
    # point the cameras '-Z' and use its 'Y' as up
    rot_quat = direction.to_track_quat('-Z', 'Y')

    # assume we're using euler rotation
    obj_camera.rotation_euler = rot_quat.to_euler()


def rescale(val, inmin, inmax, outmin, outmax):
    return outmin + (val - inmin) * ((outmax - outmin) / (inmax - inmin))

def zlift(lift, length):
    if length > 15:
        return lift
    else:
        return lift / 2
    
def midpoint(x1, y1, z1, x2, y2, z2):
    
    x = (x1 + x2) / 2
    y = (y1 + y2) / 2
    z = (z1 + z2) / 2
    
    return x, y, z

def rgb(value):
    #THIS IS WHAT DECIDES HOW DATA IS SHOWN
    groups = [br1, br2, br3, br4, br5, br6, br7] #this is funkiness from the way blender addons work, all these values were editable in the window
    clrs = [colors[0], colors[1], colors[2], colors[3], colors[4], colors[5], colors[6]]
    opps = [opacity[0], opacity[1], opacity[2], opacity[3], opacity[4], opacity[5], opacity[6]]
    scl = [scale[0], scale[1], scale[2], scale[3], scale[4], scale[5], scale[6]]

    for i in range(len(groups)):
        
        #if i + 1 == len(groups):
        #    r, g, b = colors[len(groups) - 1\]
        #    return r, g, b, scale[len(groups) - 1], opacity[len(groups) - 1], len(groups) - 1

        #groups[0] <= value <= groups[-1] and

        if groups[i] <= value <= groups[i + 1]:
            collector = i
                
            r1, g1, b1 = clrs[i]
            r2, g2, b2 = clrs[i + 1]
                
            r = rescale(value, groups[i], groups[i + 1], r1, r2)
            g = rescale(value, groups[i], groups[i + 1], g1, g2)
            b = rescale(value, groups[i], groups[i + 1], b1, b2)
                
            scl = rescale(value, groups[i], groups[i + 1], scl[i], scl[i + 1])
            opps = rescale(value, groups[i], groups[i + 1], opps[i], opps[i + 1])
                
            if opps * minopacity <= 1:
                opps = opps * minopacity
            else:
                opps = 1

            return r, g, b, scl, opps, collector

        elif value > groups[len(groups) - 1]:
            r, g, b = clrs[len(groups) - 1]
            return r, g, b, scl[len(groups) - 1], opacity[len(groups) - 1], i
    
    return nullcolor[0], nullcolor[1], nullcolor[2], tracerwidth, minopacity, 0
    

def tracers(file, crv, arw):
    #connect every d to its t, mainy body loop
    dspawn, tspawn, transmission = datafile(file)

    insig = []
    counter = 0
    for ds in range(len(dspawn)):
        
        dclc = bpy.data.collections.new("[PT]D" + str(ds + 1))
        arw.children.link(dclc)

        for ts in range(len(tspawn)):
            
            #map coords
            name = "D " + str(doff + ds) + " T " + str(toff + ts)
            
            curve = None

            #find existing curves
            if len(crv.all_objects) > 0:
                for i in crv.all_objects:    
                    if i.name.count(" ") == 3:
                        dname, d, tname, t = i.name.split(" ")
                        if t.count(".") > 0:
                            t, tail = t.split(".")
                        if int(d) == ds + doff and int(t) == ts + toff:
                            curve = i
            
            if curve:
                print("Found existing curve", curve.name)
            else:
                curve = createCurve(name, crv, dspawn[ds], tspawn[ts])

            r, g, b, scale, opacity, collector = rgb(float(transmission[counter]))

            print("DS, TS, R, G, B, S, O, T")
            print(ds, ts, r, g, b, scale, opacity, transmission[counter])

            scale = scale * tracerwidth

            #duplicate arrow to each
            bpy.ops.mesh.primitive_plane_add(size=scale, enter_editmode=False, location=(0, 0, 0), scale=(0.0, 0.0, 0.0))
            bpy.ops.object.modifier_add(type='ARRAY')
            bpy.ops.object.modifier_add(type='CURVE')

            arrow = bpy.context.active_object
            arrow.modifiers["Array"].fit_type = 'FIT_LENGTH'
            arrow.parent = curve
            arrow.name =str(collector) + name + " body"
            
            #set arrow to curve
            curveLength = sum(s.calc_length() for s in curve.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.splines)

            curveconst = headroom * scale

            arrow.modifiers["Array"].fit_length = curveLength - curveconst
            arrow.modifiers["Curve"].object = curve

            #arrowtips
            mesh = bpy.data.meshes.new("TriPlane")
            tips = bpy.data.objects.new("Plane", mesh)

            bpy.context.collection.objects.link(tips)

            bm = bmesh.new()
            bm.from_object(tips, bpy.context.view_layer.depsgraph)

            s = scale * 1.5
            bm.verts.new((s,s,0))
            bm.verts.new((s,-s,0))
            bm.verts.new((0,0,0))
           
            bmesh.ops.contextual_create(bm, geom=bm.verts)

            bm.to_mesh(mesh)
            
            bpy.context.view_layer.objects.active = tips

            bpy.ops.object.modifier_add(type='CURVE')

            #set tips to curve
            tips.parent = arrow
            tips.modifiers["Curve"].object = curve
            tips.name = name + " tip"
            
            #modify arrow location
            arrow.location[0] += curveconst
            tips.location[0] -= scale * 2
            
            #convert to mesh (apply modifiers), merge by distance, shade smooth


            dclc.objects.link(arrow)
            dclc.objects.link(tips)
            
            #material settings
            #color the arrows
            mat = bpy.data.materials.new(name = str(name))
        
            arrow.data.materials.append(mat)
            tips.data.materials.append(mat)

            #keyframe the arrows according to ds or ts
            #they should be visible on frame 0 and their frame d or t
            dsots = True
            if dsots: #keyframe according to ds
                arrow.hide_render = False
                tips.hide_render = False
                arrow.keyframe_insert(data_path="hide_render", frame=0)
                tips.keyframe_insert(data_path="hide_render", frame=0)
                #if should be visible on frame 1, dont change hide_render
                if ds == 0:
                    arrow.keyframe_insert(data_path="hide_render", frame=1)
                    tips.keyframe_insert(data_path="hide_render", frame=1)
                else:
                    #set to hide on frame 1
                    arrow.hide_render = True
                    tips.hide_render = True
                    arrow.keyframe_insert(data_path="hide_render", frame=1)
                    tips.keyframe_insert(data_path="hide_render", frame=1)

                #set to hide on frame d
                arrow.hide_render = True
                tips.hide_render = True
                arrow.keyframe_insert(data_path="hide_render", frame=ds)
                tips.keyframe_insert(data_path="hide_render", frame=ds)

                #set to show on frame d + 1
                arrow.hide_render = False
                tips.hide_render = False
                arrow.keyframe_insert(data_path="hide_render", frame=ds + 1)
                tips.keyframe_insert(data_path="hide_render", frame=ds + 1)

                #set to hide on frame d + 2
                arrow.hide_render = True
                tips.hide_render = True
                arrow.keyframe_insert(data_path="hide_render", frame=ds + 2)
                tips.keyframe_insert(data_path="hide_render", frame=ds + 2)


            mat.use_nodes = True
            mat.node_tree.nodes["Principled BSDF"].inputs['Alpha'].default_value = opacity
            mat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (r, g, b, opacity)
            mat.node_tree.nodes["Principled BSDF"].inputs['Specular'].default_value = 0.0
            

            #new = mat.node_tree.nodes.new('ShaderNodeRGB')

            #mat.node_tree.nodes.remove(mat.node_tree.nodes.get('Principled BSDF'))

            #mat.node_tree.links.new(new.outputs[0], mat.node_tree.nodes.get('Material Output').inputs[0])
            
            mat.blend_method = 'BLEND'
            mat.shadow_method = 'NONE'
            
            
            #mat.node_tree.nodes['RGB'].outputs[0].default_value = (r, g, b, opacity)
            
            #end of loop

            bpy.context.scene.collection.objects.unlink(arrow)
            bpy.context.scene.collection.objects.unlink(tips)

            counter = counter + 1


        #for every  obj in arw
        

def createCurve(name, crv, d, t):
    # create curve
    dx, dy, dz = d
    tx, ty, tz = t
                
    dist = math.sqrt((dx - tx)**2 + (dy - ty)**2)
           

    curveData = bpy.data.curves.new(name, type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 10
                
    line = curveData.splines.new('BEZIER')
                
    line.bezier_points.add(2)
                
    mx, my, mz = midpoint(dx, dy, dz, tx, ty, tz)
                
    mz = mz + zlift(lift, dist)
                
    m1x, m1y, m1z = midpoint(dx, dy, dz, mx, my, mz)
    m2x, m2y, m2z = midpoint(tx, ty, tz, mx, my, mz)
               
    #point d            
    line.bezier_points[0].co = (dx, dy, dz)
    line.bezier_points[0].handle_left = (dx, dy, dz)
    line.bezier_points[0].handle_right = (m1x, m1y, m1z)    
                    
    #midpoint
    line.bezier_points[1].co = (mx, my, mz)
    line.bezier_points[1].handle_left = ( m1x, m1y, mz)
    line.bezier_points[1].handle_right = (m2x, m2y, mz)
                
    #point
    line.bezier_points[2].co = (tx, ty, tz)
    line.bezier_points[2].handle_left = (m2x, m2y, m2z)
    line.bezier_points[2].handle_right = (tx, ty, tz)
            
    curve = bpy.data.objects.new(name, curveData)

    # attach to scene
    crv.objects.link(curve)

    return curve

def makeTracers(csv_file):
    print("Making tracer collections")
    #create tracer collections
    arw = bpy.data.collections.new("[PT]Tracers")
    bpy.context.scene.collection.children.link(arw)

    crv = bpy.data.collections.new("[PT]Curves")
    arw.children.link(crv)

    #https://blenderartists.org/t/disable-exlude-from-view-layer-in-collection/1324744
    def recurLayerCollection(layerColl, collName):
        found = None
        if (layerColl.name == collName):
            return layerColl
        for layer in layerColl.children:
            found = recurLayerCollection(layer, collName)
            if found:
                return found

    #layer_collection = bpy.context.view_layer.layer_collection
    #use view_layer 0 instead of context
    layer_collection = bpy.data.scenes[0].view_layers[0].layer_collection
    layerColl = recurLayerCollection(layer_collection, crv.name)
    bpy.context.view_layer.active_layer_collection = layerColl

    bpy.context.view_layer.active_layer_collection.exclude = True

    resetSelection()

    tracers(csv_file, crv, arw)

def getViews(csv_file):
    #views is just last row columns 1 to end, not 0
    views = []
    with open(csv_file) as csv_file2:
        csv_reader2 = csv.reader(csv_file2, delimiter=',')
        for row in csv_reader2:
            views = row[1:]
    return views

#opens the template file C:\Users\trist\brig-to-pt-1\blender\template.blend
bpy.ops.wm.open_mainfile(filepath="./blender/template.blend")

# grabs the folder from the command line
folder = sys.argv[5]

# looks for a csv and a glb file in the folder
for file in os.listdir(folder):
    if file.endswith(".csv"):
        csv_file = os.path.join(folder, file)
    if file.endswith(".glb"):
        glb_file = os.path.join(folder, file)

print(csv_file, glb_file)

for obj in bpy.data.objects:
    bpy.data.objects.remove(obj)

# import glb
model = bpy.ops.import_scene.gltf(filepath=glb_file)

# #check for any cameras in the scene AND remove
# for obj in bpy.data.objects:
#     if obj.type == 'CAMERA':
#         bpy.data.objects.remove(obj)

cut(2.75, bpy.data.objects[0])

views = getViews(csv_file)

points(csv_file)

makeTracers(csv_file)


# #create camera
# camera_data = bpy.data.cameras.new(name='Camera')
# camera_object = bpy.data.objects.new('Camera', camera_data)
# camera_object.rotation_mode = 'XYZ'
# bpy.context.scene.collection.objects.link(camera_object)
# #set camera to render camera
# bpy.context.scene.camera = camera_object

# #on frame 0 set camera to topdown view and set keyframe
# height = 5 #blender defaults to meters
# camera_object.location = (0, 0, height)

# #keyframe camera
# camera_object.keyframe_insert(data_path="location", frame=0)

# #for 1 to len(views) set camera to view and set keyframe
# for i in range(len(views)):
#     try:
#         print(views[i])
#         x, y, z, rx, ry, rz = tuple(map(float, views[i].split('/')))
#     except:
#         x, y, z, rx, ry, rz = (0, 0, height, 0, 0, 0)

#     camera_object.location = (x, y, z)
#     camera_object.keyframe_insert(data_path="location", frame=i + 1)

bpy.context.scene.frame_end = len(views) + 1
bpy.context.scene.frame_start = 0

#set render settings
bpy.context.scene.render.engine = 'BLENDER_EEVEE'

#spawn sun at angle and power
# angle = 8 #degrees from vertical
# power = 1.5 #strength of sun
# sun = bpy.data.lights.new(name="Sun", type='SUN')
# sun_obj = bpy.data.objects.new(name="Sun", object_data=sun)
# bpy.context.collection.objects.link(sun_obj)
# sun_obj.rotation_euler = (math.radians(angle), 0, 0)
# sun.energy = power

#set output to png and folder to <folder>/output
bpy.context.scene.render.image_settings.file_format = 'PNG'
bpy.context.scene.render.filepath = os.path.join(folder, "output/")

# save to <folder>/output.blend
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(folder, "output.blend"))