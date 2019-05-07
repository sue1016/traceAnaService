import pandas as pd
from visuService.dataUtil.readdata import parsefile
from visuService.dataUtil.readdata import generateFeatureDic
from visuService.dataUtil.readinfo import readinfo
import collections
from visuService.dataUtil.keydefaultdict import _KeyDefaultDict

Event = collections.namedtuple('Event','sid eid')
class Element(object):
    '''An element of the set of all possible subsequences, and a description of
    where that element occurs in the input sequences.
    '''
    def __init__(self,seq,*events):

        self.seq = seq
        self.events = set()

        for event in events:
            self.events.add(event)

    def __ior__(self,other_element):
        '''Implements the assignment operator |= by returning an Element whose
        events attribute is a union of the events of both input Elements.
        '''

        self.events |= other_element.events
        return self

    def __repr__(self):

        return self.__dict__.__repr__()

    def __eq__(self,other):

        return (self.seq == other.seq and self.events == other.events)


def subset_to_support(elements,support_threshold):
    '''Given an IdList, return an IdList containing only those atoms which
    meet the support threshold.
    '''

    subsetted = _KeyDefaultDict(Element)

    for element_name,element in elements.items():
        support = len(set([event.sid for event in element.events]))
        if support >= support_threshold:
            subsetted[element_name] = element

    return subsetted


def count_frequent_two_seq(elements,support_threshold):
    '''Given an IdList of atoms, return a dictionary of two-sequences as keys with
    the frequency of each two-sequence as the value.
    '''

    # Given an dictionary of Elements, convert it to a horizontal ID list in order to
    # count the frequency of each two-sequence of atoms.
    horizontal_db = {}

    for element_name,element in elements.items():

        for event in element.events:

            if event.sid not in horizontal_db:
                 horizontal_db[event.sid] = []

            horizontal_db[event.sid].append((element_name,event.eid))

    # create counts using horizontal_db
    counts = collections.defaultdict(int)

    for sid,seq in horizontal_db.items():

        for event_index_i,event_i in enumerate(seq):
            for event_index_j,event_j in enumerate(seq[event_index_i+1:]):

                if event_i[1] <= event_j[1]:
                    two_seq = event_i[0]+event_j[0]
                else:
                    two_seq = event_j[0]+event_i[0]

                counts[two_seq] += 1

    # this is followed by temporal joins between atoms in pairs, so
    # include only unique combinations
    return {tuple(sorted(two_seq)) for two_seq,count in counts.items() if count >= support_threshold}


def temporal_join(element_i,element_j):
    Event = collections.namedtuple('Event', 'sid eid')

    '''Given two elements, return a dictionary of new elements indexed by
    their corresponding item sequences.
    '''

    join_results = _KeyDefaultDict(Element)

    for event_index_i,event_i in enumerate(element_i.events):
        for event_index_j,event_j in enumerate(element_j.events):

            if event_i.sid == event_j.sid:

                sid = event_i.sid
                superseqs = tuple()
                superseqs_events = tuple()

                # these two atoms occur in the same sequence
                # if they occur at different times (different eids), then
                # their combination atom has the later eid by Corollary 1 (Zaki 2001)
                if event_i.eid > event_j.eid:
                    superseq = element_j.seq + tuple(element_i.seq[-1])
                    superseq_event = Event(sid=sid,eid=event_i.eid)
                    join_results[superseq] |= Element(superseq,superseq_event)

                elif event_i.eid < event_j.eid:
                    superseq = element_i.seq + tuple(element_j.seq[-1])
                    superseq_event = Event(sid=sid,eid=event_j.eid)
                    join_results[superseq] |= Element(superseq,superseq_event)

                elif element_i.seq[-1] != element_j.seq[-1]:

                    superseq_event = Event(sid=sid,eid=event_j.eid)

                    # for coincident atoms, join the last element of one atom to the other
                    # ensure that the itemset is sorted
                    superseq_i = element_i.seq[:-1] + tuple([
                        ''.join(sorted(set(element_i.seq[-1] + element_j.seq[-1])))
                        ])
                    join_results[superseq_i] |= Element(superseq_i,superseq_event)

                    superseq_j = element_j.seq[:-1] + tuple([
                        ''.join(sorted(set(element_i.seq[-1] + element_j.seq[-1])))
                        ])

                    # if both resulting atoms are identical, only add it once
                    if superseq_j != superseq_i:
                        join_results[superseq_j] |= Element(superseq_j,superseq_event)

    return join_results


def enumerate_frequent_seq(elements,support_threshold):
    '''Recursively traverse the sequence lattice, generating frequent n+1-length
    sequences from n-length sequences provided in the id_list parameter.'''

    frequent_elements = _KeyDefaultDict(Element)

    for element_index_i,seq_i in enumerate(elements.keys()):

        frequent_elements_inner = _KeyDefaultDict(Element)

        for element_index_j,seq_j in enumerate(list(elements.keys())[element_index_i+1:]):

            R = temporal_join(elements[seq_i],elements[seq_j])

            for seq,element in R.items():
                support = len(set([event.sid for event in element.events]))
                if support >= support_threshold:
                    frequent_elements_inner[seq] |= element


        for seq,element in frequent_elements_inner.items():
            frequent_elements[seq] |= element

        for seq,element in enumerate_frequent_seq(frequent_elements_inner,support_threshold).items():
            frequent_elements[seq] |= element

    return frequent_elements


def mine(sequences,support_threshold):
    '''SPADE (Zaki 2001) is performed in three distinct steps:
    1. Identify frequent single elements.
    2. Identify frequent two-element sequences.
    3. Identify all remaining sequences of three elements or more.
    '''

    # parse input sequences into individual item Elements
    elements = _KeyDefaultDict(Element)
    for sid,eid,itemset in sequences:
        for item in itemset:
            elements[tuple(item)] |= Element(tuple(item),Event(sid=sid,eid=eid))

       # print(sid,eid,itemset)
    # identify frequent single elements
    elements = subset_to_support(elements,support_threshold)

    # identify frequent two-element sequences using a horizontal database
    freq_elements_len_eq_2 = count_frequent_two_seq(elements,support_threshold)

    # generate ID lists for frequent two-element sequences discovered above
    elements_len_eq_2 = _KeyDefaultDict(Element)

    for two_seq in freq_elements_len_eq_2:

        R = temporal_join(elements[tuple(two_seq[0])],elements[tuple(two_seq[1])])

        for seq,element in R.items():
            support = len(set([event.sid for event in element.events]))
            if support >= support_threshold:
                elements_len_eq_2[seq] |= element

    # identify and generate ID lists for all remaining sequences
    freq = enumerate_frequent_seq(elements_len_eq_2,support_threshold)

    # collect all identified sequences of any length
    for seq,element in elements_len_eq_2.items():
        freq[seq] |= element

    for seq,element in elements.items():
        freq[seq] |= element

    # return frequent sequences
    return freq


def read_sequences(filename):
    '''Read sequences from a CSV.
    The CSV contains one line per sequence with columns defined as follows:
    - First column is a unique integer as sequence ID (sid)
    - Second column is a sequence-unique integer as event ID (eid)
    - Each remaining column contains an item as a character string with columns
      arranged in sequence order
    '''

    import csv

    sequences = []

    with open(filename) as f:
        seqreader = csv.reader(f)
        for seqline in seqreader:
            sequences.append(
                    tuple([ seqline[0],seqline[1],tuple(seqline[2:]) ])
                    )
    #print(sequences)
    return sequences
def exportCSV(datas,dataHandler):
    import csv
    scount = 1
    sequences = datas
    records = []
    for sequence in sequences:
        ecount = 1
        for event in sequence:
            sid = scount
            eid = ecount
            ecount = ecount + 1
            record = (sid,eid,event[1:])
            records.append(record)
        scount = scount + 1
    csvfile = open(dataHandler.assoCSVpath,'w')
    writer = csv.writer(csvfile)
    writer.writerow(['sid','eid','event'])
    writer.writerows(records)

    csvfile.close()

def getTimeRelatedData(dataHandler):
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

def getNormalizedBoolData(dataHandler):
    #读取特征
    data = generateFeatureDic(parsefile(dataHandler.traceTXTpath),dataHandler)
   # print(data)

    #将原特征转化为感兴趣的0、1特征
    interestDic = []

    interestThreshold = 1500
    #在某一摄像头下停留超过1500帧，认为感兴趣，置为1
    for eachperson in data:
        interestFeature = []
        for eachCamera in eachperson:
            #print(eachCamera)
            if eachCamera > interestThreshold:
                interestFeature.append(1)
               # print("interest")
            else:
                interestFeature.append(0)
              #  print("not interest")
        interestDic.append(interestFeature)
    #print("--------------")
    #print(interestDic)

    dataframe = pd.DataFrame(interestDic)
    info =  readinfo(dataHandler.infoJSONpath)
    cameraInfo = info['camera']
    names = [camera['name'] for camera in cameraInfo]
    dataframe.columns = names
    dataframe = (dataframe == 1)
    #print(dataframe)
    return dataframe

#自定义连接函数，用于实现L_{k-1}到C_k的连接
def connect_string(x,ms):
    x = list(map(lambda i:sorted(i.split(ms)),x))
    l = len(x[0])
    r = []
    for i in range(len(x)):
        for j in range(i,len(x)):
            if x[i][:l-1] == x[j][:l-1] and x[i][l-1] != x[j][l-1]:
                r.append(x[i][:l-1]+sorted([x[j][l-1],x[i][l-1]]))
    return r

def apriori_algo(dataframe):
    d = dataframe
    support = 0.06 #最小支持度
    confidence = 0.75 #最小置信度
    column = []
    ms = '--'  #连接符，用来区分不同元素，如A--B。需要保证原始表格中不含有该字符
    result = pd.DataFrame(index=['support','confidence'])

    support_series = 1.0*d.sum()/len(d)#支持度序列
    #print(support_series)
    #初步根据支持度筛选
    column = list(support_series[support_series > support].index)
    #print(column)

    k = 0
    while len(column) > 1:
        k = k + 1
        #print(u'\n正在进行地%d次搜索...',k)
        column = connect_string(column,ms)
        #print(column)
        sf = lambda i: d[i].prod(axis=1, numeric_only = True) #新一批支持度的计算函数
        #print(sf)
        d_2 = pd.DataFrame(list(map(sf,column)), index = [ms.join(i) for i in column]).T
        #print(d_2)

        support_series_2 = 1.0*d_2[[ms.join(i) for i in column]].sum()/len(d) #计算连接后的支持度
        #print(support_series_2)
        column = list(support_series_2[support_series_2 > support].index) #新一轮支持度筛选
        #print(column)
        support_series = support_series.append(support_series_2)
        #print(support_series)
        column2 = []


        for i in column: #遍历可能的推理，如{A,B,C}究竟是A+B-->C还是B+C-->A还是C+A-->B？
            i = i.split(ms)
            for j in range(len(i)):
                column2.append(i[:j]+i[j+1:]+i[j:j+1])

        cofidence_series = pd.Series(index=[ms.join(i) for i in column2]) #定义置信度序列

        for i in column2: #计算置信度序列
            cofidence_series[ms.join(i)] = support_series[ms.join(sorted(i))]/support_series[ms.join(i[:len(i)-1])]

        for i in cofidence_series[cofidence_series > confidence].index: #置信度筛选
            result[i] = 0.0
            result[i]['support'] = support_series[ms.join(sorted(i.split(ms)))]

    result = result.T.sort_values(['confidence','support'], ascending = False) #结果整理，输出
    #print(u'\n结果为：')
    #print(result)

    return result
def getAssoResult(dataHandler):
    apriori_algo(getNormalizedBoolData(dataHandler))
    exportCSV(getTimeRelatedData(dataHandler), dataHandler)
    sequences = read_sequences(dataHandler.assoCSVpath)
    frequent_sequences = mine(sequences, dataHandler.support_threshold)
    assoSeqs = list(frequent_sequences.keys())
    # print(assoSeqs)
    print("强关联路径:")
    info = readinfo(dataHandler.infoJSONpath)
    cameraInfo = info['camera']
    names = [camera['name'] for camera in cameraInfo]
    paths = []
    for seq in assoSeqs:
        path = []
        seq = list(seq)
        outseq = ""
        if len(seq) > 1:
            count = 0
            for dot in seq:
                if count != len(seq) - 1:
                    print(names[int(dot) - 1], end="--->")
                    path.append(names[int(dot) - 1])

                else:
                    print(names[int(dot) - 1])
                    path.append(names[int(dot) - 1])
                count = count + 1
            paths.append(path)
    print(paths)
    return paths


#print(getNormalizedBoolData())
#apriori_algo(getNormalizedBoolData())
#exportCSV(getTimeRelatedData())
'''
def main(argv):

    import pprint as pp
    import argparse

    parser = argparse.ArgumentParser(description=
            'Generate frequent subsequences meeting the minimum support threshold.'
            )

    parser.add_argument('--file',dest='input_sequence_file',
            help='A comma-delimited text file containing input sequences.',
            default="sequenceData.csv")
    parser.add_argument('--support',dest='support_threshold',type=int,
            help='The minimum number of occurrences of a frequent sequence.',
            default=10)

    args = parser.parse_args(argv)
    sequences = read_sequences(args.input_sequence_file)

    frequent_sequences = mine(sequences,args.support_threshold)
    #print(frequent_sequences)
    #pp.pprint(frequent_sequences.keys())
    assoSeqs = list(frequent_sequences.keys())
    print(assoSeqs)
    print("强关联路径:")

    info =  readinfo('info.json')
    cameraInfo = info['camera']
    names = [camera['name'] for camera in cameraInfo]
    for seq in assoSeqs:
        seq = list(seq)
        outseq = ""
        if len(seq) > 1:
            count = 0
            for dot in seq:
                if count != len(seq) - 1:
                    print(names[int(dot)-1],end = "--->")

                else:
                    print(names[int(dot)-1])
                count = count + 1

'''