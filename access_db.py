from utils import mongo_connect, mongo_disconnect
from classes import Combo, Series
import matplotlib.pyplot as plt
import numpy as np
import warnings, statistics

db,client = mongo_connect()
POSTS=db.test2
TGTS=db.target_vectors

#QUERY FUNCTIONS:

#Find all distinct search items in DB:
def find_unique(searchitem):
    '''
    Get list of unique search items in the database.
    '''
    print("Querying DB...")
    tags = POSTS.distinct(searchitem)
    return tags

#QUERY FUNCTION BY COMBO TAGLIA & IDCOMP (mandatory)
#(also can add MASTER (optional) and/or N. STADI (optional)):
def query_bycombo(taglia, idcomp, master = None, stadi = None):
    '''
    Get Combo object from MongoDB containing a list of all Series objects with matching args.
    :params  (str) taglia:, (str) idcomp, (str optional) master:, (str optional) stadi:
    :return (combo) Combo sequence of Series objects:

    METHODS:
    :combo.series -> access list of Combo sequence of Series objects;
    :combo.series[index].max_altezza -> access value of max_altezza within 1 Series object in the Combo sequence;
    :combo.series[index].max_forza -> access value of max_forza within 1 Series object in the Combo sequence;
    :combo.series[index].altezza -> access list of altezza within 1 Series object in the Combo sequence;
    :combo.series[index].forza -> access list of forza within 1 Series object in the Combo sequence;
    :combo.series[index].riduttore -> access riduttore (timecode) to which the current pressata / Series belongs;
    :combo.get_series(timestamp)-> get Series object with the indicated timestamp;
    :combo.get_fromriduttore(riduttore)-> get list of Series objects belonging to the same riduttore timecode;
    :can then use combo.get_series(timestamp).altezza and/or .forza and/or .max_altezza and/or .max_forza
    '''
    #Objects:
    taglia = str(taglia)
    idcomp = str(idcomp)
    if master:
        master = str(master)
    if stadi:
        stadi = str(stadi)
    combo = Combo(taglia, idcomp, master, stadi)
    
    #query:
    if master and stadi:
        cases = POSTS.find({'master': master, 'taglia': taglia, 'stadi': stadi}, {'ID': 1, 'steps.id': 1, 'steps.timestamp': 1, 'steps.warning':1, 'steps.max_altezza': 1, 'steps.max_forza': 1, 'steps.altezza': 1, 'steps.forza': 1})
    elif master:
        cases = POSTS.find({'master': master, 'taglia': taglia}, {'ID': 1, 'steps.id': 1, 'steps.timestamp': 1, 'steps.warning':1, 'steps.max_altezza': 1, 'steps.max_forza': 1, 'steps.altezza': 1, 'steps.forza': 1})
    elif stadi:
        cases = POSTS.find({'taglia': taglia, 'stadi': stadi}, {'ID': 1, 'steps.id': 1, 'steps.timestamp': 1, 'steps.warning':1, 'steps.max_altezza': 1, 'steps.max_forza': 1, 'steps.altezza': 1, 'steps.forza': 1})
    else:
        cases = POSTS.find({'taglia': taglia}, {'ID': 1, 'steps.id': 1, 'steps.warning':1, 'steps.timestamp': 1, 'steps.max_altezza': 1, 'steps.max_forza': 1, 'steps.altezza': 1, 'steps.forza': 1})
    
    #data extraction:
    if cases != None:
        #Search for timestamp in riduttore (list of dicts):
        for post in cases:
            #steps is list of dicts:
            for d in post['steps']:
                if d['id'] == idcomp:
                    #Store series for altezza and for forza:
                    combo.add_series(d['timestamp'], post['ID'], d['warning'], d['max_altezza'], d['max_forza'], d['altezza'], d['forza'])
    else:
        warnings.warn("Query: no match found.")

    return combo

#QUERY FROM TARGET_VECTORS COLLECTION:
def query_tgtvectors(taglia, idcomp):
    '''
    Extract max_h and tgt_vector from "target_vectors" collection in MongoDB.
    :params  (str) taglia:, (str) idcomp:
    :return (float) max_h:, (float) s_rate:, (list) tgt_vector:
    '''
    #Objects:
    taglia = str(taglia)
    idcomp = str(idcomp)
    max_h = 0
    s_rate = 0
    tgt_vec = []
    #query:
    obj = TGTS.find_one({'comp_id': idcomp, 'taglia': taglia}, {'max_h': 1, 'rate': 1, 'vector': 1})
    #data extraction:
    if obj != None:
        max_h = obj['max_h']
        s_rate = obj['rate']
        tgt_vec = obj['vector']
    else:
        warnings.warn("Query: no match found.")

    return max_h, s_rate, tgt_vec


#QUERY FUNCTION BY RIDUTTORE AND PRESSATA TIMESTAMP:
def query_bytimestamp(riduttore, timestamp):
    '''
    Query for 1 Series object only from MongoDB, identified by a riduttore and timestamp.
    :params  (str) riduttore:, (int) timestamp:
    :return (series) Series object:

    METHODS:
    :series.max_altezza -> access value of max_altezza within 1 Series object in the Combo sequence;
    :series.max_forza -> access value of max_forza within 1 Series object in the Combo sequence;
    :series.altezza -> access list of altezza within 1 Series object in the Combo sequence;
    :series.forza -> access list of forza within 1 Series object in the Combo sequence;
    '''
    #Objects:
    riduttore = str(riduttore)
    timestamp = int(timestamp)
    series = Series(timestamp)
    
    #query:
    post = POSTS.find_one({'ID': riduttore}, {'steps.timestamp': 1, 'steps.warning':1, 'steps.max_altezza': 1, 'steps.max_forza': 1, 'steps.altezza': 1, 'steps.forza': 1})
    print(post)
    
    #data extraction:
    if post != None:
        #Search for timestamp in riduttore (list of dicts):
        for d in post['steps']:
            if d['timestamp'] == timestamp:
                #Store series for altezza and for forza:
                series.riduttore = riduttore
                series.warning = d['warning']
                series.max_altezza = d['max_altezza']
                series.max_forza = d['max_forza']
                series.altezza = d['altezza']
                series.forza = d['forza']
                break
    else:
        warnings.warn("Query: no match found.")

    return series


#DUPLICATES COUNT:
def get_assembly_seq(ripressate: bool, master = None, taglia = None, stadi = None):
    '''
    Get dictionary with the occurrences of every possible assembly sequence of components for a given master / taglia / both.
    :params  (bool) ripressate: if False, duplicates are counted only once (better);
    :other params  (str) master:, (str) taglia: (can use only one or both);
    :return (dict) dict with assembly sequence and frequency of its occurrence in the whole DB:
    '''
    #Objects:
    buf = []
    assembly = {}
    
    #query:
    if master and taglia and stadi:
        master = str(master)
        taglia = str(taglia)
        stadi = str(stadi)
        cases = POSTS.find({'master': master, 'taglia': taglia, 'stadi': stadi}, {'steps.id': 1, 'steps.timestamp': 1})
    elif master and stadi:
        master = str(master)
        stadi = str(stadi)
        cases = POSTS.find({'master': master, 'stadi': stadi}, {'steps.id': 1, 'steps.timestamp': 1})
    elif master and taglia:
        master = str(master)
        taglia = str(taglia)
        cases = POSTS.find({'master': master, 'taglia': taglia}, {'steps.id': 1, 'steps.timestamp': 1})
    elif taglia and stadi:
        taglia = str(taglia)
        stadi = str(stadi)
        cases = POSTS.find({'taglia': taglia, 'stadi': stadi}, {'steps.id': 1, 'steps.timestamp': 1})
    elif master:
        master = str(master)
        cases = POSTS.find({'master': master}, {'steps.id': 1, 'steps.timestamp': 1})
    elif taglia:
        taglia = str(taglia)
        cases = POSTS.find({'taglia': taglia}, {'steps.id': 1, 'steps.timestamp': 1})
    elif stadi:
        stadi = str(stadi)
        cases = POSTS.find({'stadi': stadi}, {'steps.id': 1, 'steps.timestamp': 1})
    
    #data extraction:
    if cases != None:
        #store idcomp in assembly sequence (list):
        for post in cases:
            for d in post['steps']:
                if (ripressate == False) and (d['id'] not in buf):
                    buf.append(d['id'])
                elif (ripressate == True):
                    if (buf != []) and (buf[-1][0] == d['id']):
                        #update count for idcomp:
                        c = buf[-1][1] + 1
                        #replace tuple:
                        buf.pop()
                    else:
                        #start count:
                        c = 1
                    #append tuple:
                    t = (d['id'], c)
                    buf.append(t)

            #save buffer:
            buf = str(buf)
            if buf not in assembly.keys():
                assembly[buf] = 1
            else:
                assembly[buf] = int(assembly[buf])+1
            #reset buffer:
            buf = []
    else:
        warnings.warn("Query: no match found.")

    return assembly


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
    post = POSTS.find_one({'ID': riduttore}, {'steps.id': 1, 'steps.timestamp': 1})

    #data extraction:
    if post != None:
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
    
    else:
        warnings.warn("Query: no match found.")

    return ripressate


#MAIN:

#Main:
def trial():
    '''
    Test functions in the module.
    '''
    combo = query_bycombo(taglia="MP080", idcomp='a0215')
    print(combo.series[0].timestamp)
    print(combo.series[0].riduttore)
    print(combo.series[0].max_altezza)
    print(combo.series[0].max_forza)
    print(combo.series[0].altezza)
    print(combo.series[0].forza)
    #print(combo.get_series(1584122174).forza) #return
    #print(combo.get_series(1584109742)) #no match found

    #print(query_tgtvectors(taglia='MP060', idcomp='a0007'))
    
    #serie = query_bytimestamp("20200313112012", 1584109742)
    #print(serie.altezza)
    #print(serie.forza)

    #ripressate = find_duplicates("20200313112012")
    #print(ripressate)

    #un = find_unique("taglia")
    #un = find_unique("steps.id")
    #print(un)

    # seqs = get_assembly_seq(ripressate=True, master=1)
    # for c in seqs.items():
    #    print(c)

    # taglie= ['MP060', 'MP053']
    # for t in taglie:
    #     print(t)
    #     seqs = get_assembly_seq(ripressate=False, master=1, taglia=t, stadi=1)
    #     for c in seqs.items():
    #         print(c)


#trial()
# MOLTO IMPORTANTE ricordarsi di metterlo ogni volta che si apre una connessione
mongo_disconnect(client)
