import json 

def readinfo(jsonfile):
    with open(jsonfile,'r') as f:    
        info = json.load(f)
        return info


