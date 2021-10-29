from utils import mongo_connect,mongo_disconnect
from numpy import NaN, mean,arange
import json

def mean_sample_rate(samples):
    tmp=[]
    pos=1
    if len(samples)>1: # check array lenght >1
        while pos<len(samples):
            if samples[pos]>0:
                tmp.append(abs(samples[pos]-samples[pos-1]))
            pos+=1
    else:
        tmp.append(0)
    return mean(tmp)

def generate_vector(max_h, rate):
    vector=[]
    value=0
    while value<=max_h:
        vector.append(round(value,2))
        value+=round(rate,2)
    return vector


def to_json(comp_id,taglia,max_h,rate):
    result={
        'comp_id' : comp_id,
        'taglia'  : taglia,
        'max_h'   : max_h,
        'rate'    : rate,
        'vector'  : generate_vector(max_h,rate)
    }
    return result

# DB initilization
db,client=mongo_connect()
collection= db.test2
db.target_vectors.drop()

result= collection.find().distinct("steps.id")
ids=[]
for id in result:
    ids.append(id)

result= collection.find().distinct("taglia")
tgl=[]
for taglia in result:
    tgl.append(taglia)

#print(ids)

#initialize dictionary
sample_rates={}
for id in ids:
    sample_rates[id]={}
    for taglia in tgl:
        sample_rates[id][taglia]={}
        sample_rates[id][taglia]["max_v"]=0
        sample_rates[id][taglia]["rate"]=[]

result= collection.find({},{"taglia":1,"steps.id":1,"steps.altezza":1,"steps.forza":1})

for riduttore in result:
    taglia_r=riduttore["taglia"]
    for pressata in riduttore["steps"]:
        max_altezza = max(pressata["altezza"])
        if max_altezza > sample_rates[id][taglia_r]["max_v"]:
            sample_rates[pressata["id"]][taglia_r]["max_v"]=max_altezza
        if len(pressata["altezza"])>0:
            #sample_rates[pressata["id"]][taglia_r]["rate"].append(mean_sample_rate(pressata["altezza"]))
            sample_rates[pressata["id"]][taglia_r]["rate"].append(min(pressata["altezza"]))

for id in ids:
    for taglia in tgl:
        #sample_rates[id][taglia]["rate"]=mean(sample_rates[id][taglia]["rate"])
        if len(sample_rates[id][taglia]["rate"])>0:
            sample_rates[id][taglia]["rate"]=min(sample_rates[id][taglia]["rate"])


for comp in sample_rates.keys():
        for tg in sample_rates[comp].keys():
            if sample_rates[comp][tg]["max_v"] != 0:
                res=to_json(comp,tg,sample_rates[comp][tg]["max_v"],sample_rates[comp][tg]["rate"])
                db.target_vectors.insert_one(res)

# keep at end of query
mongo_disconnect(client)