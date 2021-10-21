from utils import mongo_connect,mongo_disconnect
from numpy import mean

def mean_sample_rate(samples):
    tmp=[]
    pos=1
    while pos<len(samples):
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

print(ids)

#initialize dictionary
sample_rates={}
for id in ids:
    sample_rates[id]=[]

result= collection.find({},{"steps.id":1,"steps.altezza":1,"steps.forza":1})

for pres in result:
    for pressata in pres["steps"]:
        for id in ids:
            if pressata["id"]==id:
                sample_rates[id].append(mean_sample_rate(pressata["altezza"]))

for elem in sample_rates.items():
    print(elem[0],mean(elem[1]))



# keep at end of query
mongo_disconnect(client)