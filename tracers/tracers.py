import bpy
import csv
from mathutils import Vector

def execute(csv_file):
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
    dmat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (bpy.context.window_manager.dcolor[0], bpy.context.window_manager.dcolor[1], bpy.context.window_manager.dcolor[2], 1)          
    tmat = bpy.data.materials.new(name = str("T Mat"))
    tmat.use_nodes = True
    tmat.shadow_method = 'NONE'
    tmat.node_tree.nodes["Principled BSDF"].inputs['Base Color'].default_value = (bpy.context.window_manager.tcolor[0], bpy.context.window_manager.tcolor[1], bpy.context.window_manager.tcolor[2], 1)
          
        
      
    for i in range(len(spawns)):
         
        x, y, z = spawns[i]
        
        if dt:
            bpy.ops.mesh.primitive_cylinder_add(location=(x, y, z), depth=(bpy.context.window_manager.pointsize * 0.4), radius=(bpy.context.window_manager.pointsize * 0.4))
        else:
            bpy.ops.mesh.primitive_cube_add(location=(x, y, z), size=(bpy.context.window_manager.pointsize * 0.5))
        
        new = bpy.context.active_object

        new.scale[2] = new.scale[2] * 0.5

        list.append(new)
         
        new.name = str(("D" if dt else "T") + str(i + (bpy.context.window_manager.doff if dt else bpy.context.window_manager.toff)))
        
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

    if bpy.context.window_manager.file_path[-4:] == ".csv":
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

    elif bpy.context.window_manager.file_path[-4:] == ".txt":
        #find data blocks
        for line in lines:
            if line == "Ds\n":
                dstart = line_count + 1
            elif line == "Ts\n":
                dend = line_count - 2
                tstart = line_count + 1
            elif line == "Transmission\n":
                tend = line_count - 2
                transstart = line_count + 1
            line_count += 1
        transend = line_count
#/Path-Tracer/sample.txt

        i = 0
        lines = open(datafilename, "r")

        for line in lines:
            #strip \n
            line = line.strip()
            if dstart <= i <= dend:
                line = tuple(map(float, line.split('/')))
                dspawn.append(line)
            if tstart <= i <= tend:
                print(line)
                line = tuple(map(float, line.split('/')))
                tspawn.append(line)
            if transstart <= i <= transend:
                line = float(line)
                transmission.append(line)
            i += 1

        print('dspawn', dspawn)
        print('tspawn', tspawn)
        print('transmission', transmission)
        return dspawn, tspawn, transmission
    else:
        print("DATAFILE ERROR")

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