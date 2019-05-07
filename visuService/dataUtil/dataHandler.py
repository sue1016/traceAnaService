import json
from django.core.files.storage import DefaultStorage
from visuService.dataUtil.visu import exportVisuData
from visuService.dataUtil.readinfo import readinfo
from visuService.dataUtil.assomining import getNormalizedBoolData,getTimeRelatedData,apriori_algo,exportCSV,mine,read_sequences,getAssoResult
import pprint as pp
from visuService.dataUtil.anoDetection import cluster
import argparse

class dataHandler():
    traceTXTpath = 'visuService/static/visuService/txt/swdata.txt'
    infoJSONpath = 'visuService/static/visuService/json/info.json'
    allJSONpath = 'visuService/static/visuService/json/all.json'
    visuJSONpath = 'visuService/static/visuService/json/visudata.json'
    assoCSVpath = 'visuService/static/visuService/csv/sequenceData.csv'
    anoJPGpath = 'visuService/static/visuService/jpg/anoDetection.jpg'
    defaultStorage = DefaultStorage()
    def __init__(self):
        self.support_threshold = 10
    def getVisuData(self):
        if self.defaultStorage.exists(self.traceTXTpath) and self.defaultStorage.exists(self.infoJSONpath):
            print("base data exist")
            exportVisuData(self)
        else:
            print("uable to do this for base data not exists")
    def getAssoData(self):
        paths = getAssoResult(self)
        return paths
    def getAnoResult(self):
        cluster(self)







