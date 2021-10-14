import pymongo
import matplotlib.pyplot as plt
# mongo connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client.novotic
posts = db.test1

#Vars:
ripressate = {}
dups = []
prior = ''
new = ''
count = 1
i = 0
limit = 1
height = []
force = []
series_height = {}
series_force = {}

#Loop across posts:
for post in posts.find():

    #Check every step in the post:
    for step in post["steps"]:
        new = str(step["id"])

        #Create data series:
        for ts in step['serie']:
            try:
                s1 = float(str(ts['height']).replace(",","."))
                s2 = float(str(ts['force']).replace(",","."))
                height.append(s1)
                force.append(s2)
            except:
                print("Line skipped for ID: {}".format(new))

        #Duplicate match:
        if new == prior:
            count = count+1

        else:
            #Store buffer in tuple:
            if count > 1:
                #save to dict:
                series_height[count] = height[:-1]
                series_force[count] = force[:-1]
                print(series_height[prior])
                print(series_force[prior])
                #Store to tuple:
                tup = (prior, count)
                dups.append(tup)
                count = 1

            #keep only last read:
            height = [height[-1]]
            force = [force[-1]]

        #Reset:
        prior = new
    
    #Store tuple in overall dictionary id:tuple
    ripressate[str(post["_id"])] = dups
    dups = []
    prior = ''
    i = i+1

    #Break clause:
    if i >= limit:
        break

for item in ripressate.items():
    print(item)


'''
query={"steps.id": "a0207"}
result=db.test1.find(query)

count=0
for res in result:
   if count==0:
      print(res) 
      count+=1
'''