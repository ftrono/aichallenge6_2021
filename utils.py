import datetime
import pymongo
import matplotlib.pyplot as plt

CONNECTION_STRING="mongodb://localhost:27017/"

def name_parser(name): # take as input the file name
    # get information from file name
    tempcode=name[0:14]
    id=name[14:19]
    stazione=name[21:23]
    date_time=datetime.datetime(int(name[24:28]), int(name[29:31]), int(name[32:34]),int(name[35:37]),int(name[38:40]),int(name[41:43])) # convert string to date obj
    timestamp=datetime.datetime.timestamp(date_time) # convert date object to timestamp
    return tempcode,id,stazione,timestamp

def mongo_connect():
    client = pymongo.MongoClient(CONNECTION_STRING)
    db = client.novotic
    return db, client

def mongo_disconnect(client):
    client.close()

def plot_series(riduttore):
    '''
    Genera un diagramma per ogni riga contenuta nel parametro `riduttore`.
    OCCIO: necessita di un'ulteriore iterazione del tipo `POSTS.find()`
    :param riduttore: singolo elemento dell'iterazione di `POSTS.find()`.
    :return PNG
    '''
    for pressata in riduttore['steps']:
        # setting lists for plotting
        labels = list()
        xpoints = list()
        ypoints = list()

        # populating lists
        labels.append(pressata['id'])
        ypoints.append(pressata['forza'])
        xpoints.append(pressata['altezza'])

        # actual plotting
        plt.plot(xpoints[0], ypoints[0])
        plt.xlabel(labels[0])
        diagram = plt.show()
    return diagram