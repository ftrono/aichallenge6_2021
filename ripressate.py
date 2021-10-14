from utils import mongo_connect, mongo_disconnect
import matplotlib.pyplot as plt
db,client = mongo_connect()
POSTS=db.test1

def find_masters(POSTS):
    tags = POSTS.distinct("master")

    for tag in tags:
        print(tag)

    #return tags

def find_duplicates(post):

    #Vars:
    ripressate = {}
    dups = []
    prior = ''
    new = ''
    count = 1
    height = []
    force = []
    series = {}
    newread = []
    priorread = []
    totread = []
    i = 0
    last = len(post["steps"])

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
            
        #save to buffer:
        newread = [height, force]
        height = []
        force = []

        #Duplicate match:
        if new == prior:
            #append buffer from prior read:
            totread.append(priorread)
            count = count+1

        else:
            #Store buffer in tuple:
            if count > 1:
                #Store to tuple:
                tup = (prior, count)
                dups.append(tup)
                #save to dict of pressate by id:
                totread.append(priorread)
                series[prior] = totread
                #reset count:
                count = 1
                totread = []

        #If last component of the riduttore and buffer is not empty, store:
        if i == last and count > 1:
            #Store to tuple:
            tup = (prior, count)
            dups.append(tup)
            #save to dict of pressate by id:
            totread.append(priorread)
            series[prior] = totread
            #reset count:
            count = 1
            totread = []

        #Reset:
        prior = new
        priorread = newread
        newread = []
        i = i+1
        
        #Store tuple in overall dictionary id:tuple
        ripressate[str(post["_id"])] = dups
        #newread = []

    return ripressate, series


#MAIN:
i = 0
limit = 1

#tags = find_masters(POSTS)
#print(tags)

#Loop across POSTS:
for post in POSTS.find():

    ripressate, series = find_duplicates(post)
    i = i+1

    #Break clause:
    if i >= limit:
        break

print("DUPLICATES FOUND:")
for item in ripressate.items():
    print(item)
    break

print("\nSERIES:")

for item in series.items():
    print(item)
    break

# MOLTO IMPORTANTE ricordarsi di metterlo ogni volta che si apre una connessione
mongo_disconnect(client)

