from utils import mongo_connect,mongo_disconnect
from classes import Target_vector
from numpy import diff
import logging

logging.basicConfig(level=logging.DEBUG)

# open connection with db
db,client=mongo_connect()
db.target_vectors.drop()
logging.debug("Dropped target vector collection")
# close connection with db
mongo_disconnect(client)

# open connection with db
db,client=mongo_connect()
collection=db.test2
logging.debug("Connected to mongo DB")

# getting distinc id by query db 
id_result= collection.find().distinct("steps.id")
ids=[]
for id in id_result:
    ids.append(id)
logging.debug("Got id list")

#getting distinct tgl by query db
tgl_result= collection.find().distinct("taglia")
taglie=[]
for taglia in tgl_result:
    taglie.append(taglia)
logging.debug("Got tgl list")

# close connection with db
mongo_disconnect(client)
logging.debug("DB Connection closed")

# dictionary inizialization
combinazioni={}
for id in ids:
    for tgl in taglie:
        combinazioni[id+"_"+tgl]=Target_vector(id,taglia)
logging.debug("Initialized DB")

# query db to get all pressate
db,client=mongo_connect()
collection=db.test2
result= collection.find({},{"taglia":1,"steps.id":1,"steps.altezza":1})
logging.debug("Query DB completed")
mongo_disconnect(client)

# iterate in result to populate dictionary
for riduttore in result:
    tgl=riduttore["taglia"]
    for pressata in riduttore["steps"]:
        if len(pressata["altezza"])>0:
            key=pressata["id"]+"_"+tgl
            combinazioni[key].compute_rate(pressata["altezza"])
logging.debug("Populated dictionary")

# computing values and storing to the db
cnt=0
db,client=mongo_connect()
collection=db.target_vectors
for id in ids:
    for tgl in taglie:
        key = id + "_" + tgl
        combinazioni[key].compute_values()
        collection.insert_one(combinazioni[key].to_json())
        logging.debug("Inserted "+cnt)
        cnt+=1
logging.debug("Completed insertion")
mongo_disconnect(client)
logging.debug("End")






