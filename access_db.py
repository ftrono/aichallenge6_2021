from utils import mongo_connect, mongo_disconnect
from classes import Combo, Series
import matplotlib.pyplot as plt
db,client = mongo_connect()
POSTS=db.test2


#QUERY FUNCTION BY MASTER, TAGLIA, IDCOMP:
def query_bycombo(master, taglia, idcomp):
    '''
    Get Combo object from MongoDB containing a list of Series objects with matching args.
    :params  (str) master:, (int) taglia:, (int) idcomp:
    :return (combo) Combo sequence of Series objects:
    '''
    #Objects:
    master = str(master)
    taglia = str(taglia)
    idcomp = str(idcomp)
    combo = Combo(master, taglia, idcomp)
    
    #query:
    cases = POSTS.find({'master': master, 'taglia': taglia})
    #Search for timestamp in riduttore (list of dicts):
    for post in cases:
        riduttore = str(post['ID'])
        for d in post['steps']:
            if d['id'] == idcomp:
                #Store series for altezza and for forza:
                combo.add_series(riduttore, d['timestamp'], d['altezza'], d['forza'])

    return combo


#QUERY FUNCTION BY PRESSATA TIMESTAMP:
def query_bytimestamp(riduttore, timestamp):
    '''
    Get series object from MongoDB with height (list) and force (list) series of values.
    :params  (str) riduttore:, (int) timestamp:
    :return (series) Series object:
    '''
    #Objects:
    riduttore = str(riduttore)
    timestamp = int(timestamp)
    series = Series(riduttore, timestamp)
    #query:
    post = POSTS.find_one({'ID': riduttore})
    #Search for timestamp in riduttore (list of dicts):
    for d in post['steps']:
        if d['timestamp'] == timestamp:
            #Store series for altezza and for forza:
            series.altezza = d['altezza']
            series.forza = d['forza']
            break

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
    serie = query_db("20200313112012", 1584109742)
    print(serie.altezza)
    print(serie.forza)

    ripressate = find_duplicates("20200313112012")
    print(ripressate)


#trial()
# MOLTO IMPORTANTE ricordarsi di metterlo ogni volta che si apre una connessione
mongo_disconnect(client)
