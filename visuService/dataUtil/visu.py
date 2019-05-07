import random
import json
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_toolkits.mplot3d import Axes3D
from visuService.dataUtil.preVisu import Draw
from visuService.dataUtil.readinfo import readinfo


def exportVisuData(dataHandler):
    info = readinfo(dataHandler.infoJSONpath)
    cameraInfo = info['camera']
    interval_time = info['interval_time']
    numofcamera = len(cameraInfo)
    posofcameras =  [[camera['x'],camera['y']] for camera in cameraInfo]
    nameofcameras = [camera['name'] for camera in cameraInfo]
    d = Draw(dataHandler.traceTXTpath,interval_time,numofcamera,posofcameras,nameofcameras)
    maxframe = d.getMaxFrameNo()
    with open(dataHandler.allJSONpath, 'w') as f:
        json.dump(d.getWholeTraceBook(maxframe), f)
        print('写入所有轨迹信息到json文件中完毕')
    with open(dataHandler.allJSONpath, 'r') as f:
        tracebook = json.load(f)
    dikaerji = d.getCameraJoinList()


    info = readinfo(dataHandler.infoJSONpath)
    cameraInfo = info['camera']
    cameraNum = len(cameraInfo)
    visudata = {}
    frameCounter = 0
    pathbook = {}
    dotbook = {}
    for frame in tracebook:
        frameCounter = frameCounter + 1
        pathDic = {}
        dotDic = {}

        for person in frame:
            isIn = person[0]
            fromCam = person[1]
            toCam = person[2]
            if isIn:
                fromNo  = fromCam[1:]
                toNo = toCam[1:]
                path = str((fromNo,toNo))
                dot = fromNo
                if dotDic.__contains__(dot):
                    dotDic[dot] = dotDic[dot] + 1
                else:
                    dotDic[dot] = 1
                if pathDic.__contains__(path):
                    pathDic[path] = pathDic[path] + 1
                else:
                    pathDic[path] = 1

        pathbook[frameCounter] = dotDic
        dotbook[frameCounter] = pathDic

    with open(dataHandler.visuJSONpath,'w') as f:
        json.dump(pathbook,f)
        json.dump(dotbook,f)
        print("写入画图信息到json文件完毕")


'''

x_list = [[3, 3, 2], [4, 3, 1], [1, 2, 3], [1, 1, 2], [2, 1, 2]]
fig = plt.figure()
ax = Axes3D(fig)
for x in x_list:
    ax.scatter(x[0], x[1], x[2], c='r')
plt.show()
'''

'''
def draw():
    #https://www.cnblogs.com/OliverQin/p/7965435.html
    tracebook = readTraceBook("all.json")
    frame = tracebook[0]
    for person in
    info = readinfo('info.json')
    cameraInfo = info['camera']
    positionX = [camera['x'] for camera in cameraInfo]
    positionY = [camera['y'] for camera in cameraInfo]
    mpl.rcParams['font.size'] = 10
    plt.title("map",fontsize=12)
    plt.xlabel("x",fontsize=12)
    plt.ylabel("y",fontsize=12)
    color = ['r','y','k','g','m']
    plt.scatter(positionX, positionY,c=color)
    plt.show()
'''

