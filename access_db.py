from utils import mongo_connect, mongo_disconnect
from classes import Combo, Series
import matplotlib.pyplot as plt
db,client = mongo_connect()
POSTS=db.test2


#QUERY FUNCTION BY MASTER, TAGLIA, IDCOMP:
def query_bycombo(master, taglia, idcomp):
    '''
    Get Combo object from MongoDB containing a list of all Series objects with matching args.
    :params  (str) master:, (str) taglia:, (str) idcomp:
    :return (combo) Combo sequence of Series objects:

    METHODS:
    :combo.series -> access list of Combo sequence of Series objects;
    :combo.series[index].altezza -> access list of altezza within 1 Series object in the Combo sequence;
    :combo.series[index].forza -> access list of forza within 1 Series object in the Combo sequence;
    :combo.get_series(timestamp)-> get Series object with the indicated timestamp;
    :can then use combo.get_series(timestamp).altezza and/or combo.get_series(timestamp).forza
    '''
    #Objects:
    master = str(master)
    taglia = str(taglia)
    idcomp = str(idcomp)
    combo = Combo(master, taglia, idcomp)
    
    #query:
    print("Querying DB...")
    cases = POSTS.find({'master': master, 'taglia': taglia})
    try:
        #Search for timestamp in riduttore (list of dicts):
        for post in cases:
            for d in post['steps']:
                if d['id'] == idcomp:
                    #Store series for altezza and for forza:
                    combo.add_series(d['timestamp'], d['altezza'], d['forza'])
    except:
        print("Query: no match found.")

    return combo


#QUERY FUNCTION BY RIDUTTORE AND PRESSATA TIMESTAMP:
def query_bytimestamp(riduttore, timestamp):
    '''
    Query for 1 Series object only from MongoDB, identified by a riduttore and timestamp.
    :params  (str) riduttore:, (int) timestamp:
    :return (series) Series object:

    METHODS:
    :series.altezza -> access list of altezza within the Series object;
    :series.forza -> access list of forza within the Series object.
    '''
    #Objects:
    riduttore = str(riduttore)
    timestamp = int(timestamp)
    series = Series(timestamp)
    #query:
    post = POSTS.find_one({'ID': riduttore})
    try:
        #Search for timestamp in riduttore (list of dicts):
        for d in post['steps']:
            if d['timestamp'] == timestamp:
                #Store series for altezza and for forza:
                series.altezza = d['altezza']
                series.forza = d['forza']
                break
    except:
        print("Query: no match found.")

    return series


#DUPLICATES COUNT:
def find_duplicates(riduttore):
    '''
    Get counts of duplicates within a riduttore, each with its related component ID.
    :param   (str) riduttore:
    :return: (component, count):
    '''
    #Vars:
    riduttore = str(riduttore)
    ripressate = {}
    dups = []
    prior = ''
    new = ''
    count = 1

    #query:
    post = POSTS.find_one({'ID': riduttore})
    try:
        #Check every pressata (dict) in riduttore (list of dicts):
        for pressata in post["steps"]:
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
        ripressate[str(post["_id"])] = dups
    
    except:
        print("Query: no match found.")

    return ripressate


#Find all distinct masters in DB:
def find_masters(POSTS):
    '''
    Get list of unique masters in the database.
    '''
    tags = POSTS.distinct("master")
    return tags


#MAIN:
def trial():
    '''
    Test functions in the module.
    '''
    combo = query_bycombo("2", "MP080", 'a0215')
    print(combo.series[0].altezza)
    print(combo.series[0].forza)
    print(combo.get_series(1584122174).forza) #return
    #print(combo.get_series(1584109742)) #no match found
    
    #serie = query_bytimestamp("20200313112012", 1584109742)
    #print(serie.altezza)
    #print(serie.forza)

    ripressate = find_duplicates("20200313112012")
    print(ripressate)


#trial()
# MOLTO IMPORTANTE ricordarsi di metterlo ogni volta che si apre una connessione
mongo_disconnect(client)
