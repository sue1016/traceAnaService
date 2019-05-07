from django.shortcuts import render
from django.conf.urls.static import static
from django.http import HttpResponse
from visuService.dataUtil.dataHandler import *
def index(request):
    return HttpResponse("Hello, world. You're at the index.")

def getAllDataNeeded(request):
    dh = dataHandler()
    #dh.getVisuData()
    #dh.getAssoData()
    dh.getAnoResult()
    return HttpResponse("added")




