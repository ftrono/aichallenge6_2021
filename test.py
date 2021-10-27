from utils import mongo_connect,mongo_disconnect
from numpy import mean
import matplotlib.pyplot as plt

def mean_sample_rate(samples,max):
    tmp=[]
    pos=1
    while pos<=max:
        tmp.append(samples[pos]-samples[pos-1])
        pos+=1
    return mean(tmp)


# DB initilization
db,client=mongo_connect()
collection= db.test2

result= collection.find().distinct("steps.id")
ids=[]
for id in result:
    ids.append(id)

#print(ids)

#initialize dictionary
sample_rates={}
for id in ids:
    sample_rates[id]=[]

result= collection.find({},{"steps.id":1,"steps.altezza":1,"steps.forza":1})

for riduttore in result:
    for pressata in riduttore["steps"]:
        for id in ids:
            if pressata["id"]==id:
                max_value = max(pressata["altezza"])
                max_index = pressata["altezza"].index(max_value)
                if max_index==0:
                    print(pressata["id"])

                sample_rates[id].append(mean_sample_rate(pressata["altezza"],max_index))

for elem in sample_rates.items():
    print(elem[0],mean(elem[1]))



# keep at end of query
mongo_disconnect(client)