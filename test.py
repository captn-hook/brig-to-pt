import bpy

#args are csv path, model path, and output folder
csvFile = './daikin.csv'
modelFile = './Daikin.glb'
outputFolder = './output/1/'

#load csv file
csv = open(csvFile, 'r')
csvLines = csv.readlines()

labelsX = []
labelsY = []
positionsX = []
positionsY = []

pointsXY = [[]]

camera_positions = []

for lineNum, line in enumerate(csvLines):
    line = csvLines[lineNum]
    #first line Should start with: Labels, 0, 1, 2, ... length  //labels is column 0 and '0' is column 1
    if line.startswith('Labels') and lineNum == 0:
        labelsX = line.split(',')[1:]
    #second line should have labelY[0], XYZ, posX[0], posX[1], posX[2], ... posX[length]
    elif line.startswith(labelsX[0]) and lineNum == 1:
        spl = line.split(',')
        labelsY.append(spl[0])
        #fill posX with line[2:]
        positionsX = spl[2:]
    #onwards should have labelY[linenum - 1], posY[lineNum - 1], pointXY[0], pointXY[1], pointXY[2], ... pointXY[l(ength - 1 )* (lineNum - 1)]
    elif not line.startswith('INSIGHTS') and not line.startswith('VIEWS'): #these are the note rows at the end of the csv
        spl = line.split(',')
        labelsY.append(spl[0])
        positionsY.append(spl[1])
        pointsXY.append(spl[2:])
    elif line.startswith('VIEWS'):
        spl = line.split(',')
        camera_positions.append(spl[1:])
