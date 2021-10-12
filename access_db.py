from pymongo import MongoClient
import matplotlib.pyplot as plt
# mongo connection
client = MongoClient("mongodb://localhost:27017/")
db=client.novotic

query={"steps.id": "a0207"}
result=db.test1.find(query)

count=0
for res in result:
   if count==0:
       print(res) 
    count+=1