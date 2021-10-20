from utils import mongo_connect, mongo_disconnect
import matplotlib.pyplot as plt
db,client = mongo_connect()
POSTS=db.test2

#Find all distinct masters in DB:
def find_masters(POSTS):
    tags = POSTS.distinct("master")
    return tags


#For 1 pressata: create timeseries for height and force values:
#input: pressata
#output: 2 lists, one for height timeseries, the other for force timeseries.
def read_timeseries(pressata):
    '''
    Create timeseries for height (list) and force (list) values
    :param  pressata:
    :return height:, force:
    '''
    #Vars:
    height = []
    force = []
    cur = str(pressata["id"])

    #Store data series into lists:
    for ts in pressata['serie']:
        try:
            #Convert values to floats:
            s1 = float(str(ts['height']).replace(",","."))
            s2 = float(str(ts['force']).replace(",","."))
            #Store:
            height.append(s1)
            force.append(s2)
        except:
            print("Line skipped for ID: {}".format(cur))
        
    return height, force


#For 1 riduttore: create dictionary of pressate:
#input: 1 riduttore
#output: dictionary with pressate+count as keys and pair of timeseries as values.
def read_pressate(riduttore):
    '''
    Created dictionary of pressate
    :param      riduttore:
    :return:    pressate:
    '''
    pressate = {}
    prior = ''
    new = ''
    count = 0

    #Check every pressata in riduttore:
    for pressata in riduttore["steps"]:
        new = str(pressata["id"])
        #read timeseries:
        height, force = read_timeseries(pressata)

        #if ripressata, increment count:
        if new == prior:
            count = count+1
        else:
            #reset count:
            count = 0

        #save to dict:
        pressate[new+"-"+str(count)] = [height, force]

        #Reset:
        prior = new
        height = []
        force = []

    return pressate


#For 1 riduttore: obtain list of duplicates only (ripressate) with counts.
#input: 1 riduttore
#output: dictionary with id_riduttore as key and list of tuples (component, count) for duplicates only as values.
def find_duplicates(riduttore):
    '''
    Obtain list of duplicates only (ripressate) with counts
    :param   riduttore:
    :return: (component, count):
    '''
    #Vars:
    ripressate = {}
    dups = []
    prior = ''
    new = ''
    count = 1

    #Check every pressata in riduttore:
    for pressata in riduttore["steps"]:
        new = str(pressata["id"])        

        #Duplicate match:
        #If ripressata, increment count:
        if (new == prior):
            count = count+1

        else:
            #Check if accumulated duplicates counts exist:
            if count > 1:
                #Store to tuple:
                tup = (prior, count)
                dups.append(tup)
            #reset count:
            count = 1

        #Reset id:
        prior = new
    
    #Store list of duplicates in dictionary:
    ripressate[str(riduttore["_id"])] = dups

    return ripressate


#MAIN:
def main():
   i = 0
   limit = 1

   #Loop across POSTS:
   print("DUPLICATES FOUND:")
   for riduttore in POSTS.find():

      sample = riduttore
      ripressate = find_duplicates(sample)
      print(ripressate)
      i = i+1

      #Break clause:
      if i >= limit:
         break


   print("\nSERIES:")

   pressate = read_pressate(sample)
   print(pressate.keys())
   print(pressate)


main()
# MOLTO IMPORTANTE ricordarsi di metterlo ogni volta che si apre una connessione
mongo_disconnect(client)




'''
#Launch find_masters:
tags = find_masters(POSTS)
for tag in tags:
    print(tag)

#PRIOR CONTENT OF ACCESSDB.PY FILE:
query={"steps.id": "a0207"}
result=db.test1.find(query)

count=0
for res in result:
   if count==0:
      print(res) 
      count+=1


'''

