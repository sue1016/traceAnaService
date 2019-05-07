import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from pandas.core.frame import DataFrame
import matplotlib.pyplot as plt
from visuService.dataUtil.readdata import parsefile
from visuService.dataUtil.readdata import generateFeatureDic
from visuService.dataUtil.readinfo import readinfo
def cluster(dataHandler):
    data = generateFeatureDic(parsefile(dataHandler.traceTXTpath),dataHandler)
   # print(data)
    data = DataFrame(data)
    info =  readinfo(dataHandler.infoJSONpath)
    cameraInfo = info['camera']
    names = [camera['name'] for camera in cameraInfo]
    data.columns = names
    #data.columns = ['c1','c2','c3','c4','c5','c6']
    #print(data)
    data_zs = 1.0 * (data - data.mean())/data.std()
   # print(data_zs)
    k = 1
    threshold = 2 
    iteration = 500
    model = KMeans(n_clusters=k, n_jobs = 4, max_iter = iteration)
    model.fit(data_zs) 

    r = data_zs
   # r = pd.concat([data_zs,pd.Series(model.labels_, index = data.index)], axis = 1)
   # r.colunms = ['c1','c2','c3','c4','c5','c6','type']
  #  print(r)
    norm = []
    norm_tmp = r-model.cluster_centers_[0]
    norm_tmp = norm_tmp.apply(np.linalg.norm,axis = 1)
    norm.append(norm_tmp/norm_tmp.median())
    #print(norm)
    norm = pd.concat(norm)    

   # plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    norm[norm <= threshold].plot(style = 'go')
    
    discrete_points = norm[norm > threshold]
    discrete_points.plot(style = 'ro')
    
    for i in range(len(discrete_points)):
        id = discrete_points.index[i]
        n = discrete_points.iloc[i]
        plt.annotate('(%s,%0.2f)'%(id,n),xy= (id,n),xytext = (id,n))
    plt.xlabel(u'编号')
    plt.ylabel(u'相对距离')
    #plt.show()
    plt.savefig(dataHandler.anoJPGpath)


