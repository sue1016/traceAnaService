from visuService.dataUtil.readinfo import readinfo


def generateFeatureDic(l,dataHandler):

    info = readinfo(dataHandler.infoJSONpath)
    cameraNum = len(info['camera'])
    featureDic = []
    #how many cameras in all
    #print(len(l))
    for eachPerson in l:
        personFeature = [0]*cameraNum
        '''
        one person's feature vector is like 
        [300,200,100,5000,2000,200]
        means 
        camera1 in all 300
        camera2 in all 200
        and ...
        ''' 
        for eachRecord in eachPerson:
            if eachRecord[0] == 'p':
                continue
            cameraNo = int(eachRecord[0][1:])
           # print(cameraNo)
            duration = eachRecord[3] - eachRecord[2]
           # print(duration)
            personFeature[cameraNo-1] = personFeature[cameraNo-1] + duration
        featureDic.append(personFeature)
    #print(featureDic)
    return featureDic

def parsefile(name):
    """
		input file every line like:p2 (c2,s1,200,320) (c3,s1,420,500)
		output list :[['c2', 's1', 200, 320], ['c3', 's1', 420, 500]]
    the func will return something like 
    [['p1', ['c1', 's1', 15, 55], ['c2', 's1', 80, 2000], ['c5', 's1', 2300, 2400], ['c4', 's1', 2600, 3800], ['c6', 's1', 3200, 3500]], ['p2', ['c1', 's1', 200, 250], ['c2', 's1', 500, 1634], ['c5', 's1', 1800, 1850], ['c4', 's1', 2000, 4200], ['c6', 's1', 4800, 4900]], ['p3', ['c1', 's1', 500, 60.............
    """
    file = open(name)
    #print('file state',file.closed)
    alllines = file.readlines()
    l = []
    for eachline in alllines:
        eachlinelist = eachline.split()
        eachlinelist_ = [parsetracevector(x) for x in eachlinelist if x[0]!='p']
        eachlinelist_.insert(0,eachlinelist[0])
        l.append(eachlinelist_)
        #print('current line:'+str(eachlinelist))
    file.close()
    #print(l)
    return(l)


def parsetracevector(string):
    """
        input string :'(c1,s1,200,320)'
    """
    string = string.strip('(')
    string = string.strip(')')
    string = string.split(',')
    string[2] = int(string[2])
    string[3] = int(string[3])
    return string

def getTimeRelatedInterestedData(dataHandler):
    timeRelatedDataDic = []
    data = parsefile(dataHandler.traceTXTpath)
    interestThreshold = 1500
    count = 0
    for eachperson in data:
        count = count + 1
        timeRelatedData = []
        for eachrecord in eachperson:
            if eachrecord[0] == 'p':
                 continue  
            duration = eachrecord[3] - eachrecord[2]
            if duration > interestThreshold:
                timeRelatedData.append(eachrecord[0])
        timeRelatedDataDic.append(timeRelatedData)
        #print("intereted track of p"+ str(count) ,end = ':')
        #print(timeRelatedData)
    #print(timeRelatedDataDic)
    #print(len(timeRelatedDataDic))
    return timeRelatedDataDic

#parsefile('static/visuService/txt/swdata.txt')
