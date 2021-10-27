import datetime
import pymongo
import matplotlib.pyplot as plt
from scipy.signal import lfilter
from scipy.ndimage import zoom

CONNECTION_STRING="mongodb://localhost:27017/" #to executing locally
#CONNECTION_STRING="mongodb://team6:MLoMuk2b@hitvmiac-06.northeurope.cloudapp.azure.com:27017" #for executing on the Azure VM
#CONNECTION_STRING="mongodb://team6:MLoMuk2b@localhost:27017" #for executing on the Azure VM


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



def plot_series(id, x, y, **title):
    '''

    :param id: label
    :param x: altezza
    :param y: forza
    :param title: optional
    :return:
    '''
    label = id
    plt.plot(x, y)
    plt.xlabel(label)
    plt.title(title)
    graph = plt.show()
    return graph



def filter_series(series):
    '''
    Funzione per fare uno smoothing di una curva e rimuovere il rumore 
    Visto che modifica abbastanza i valori sarebbe meglio utilizzarla solo per la 
    prima parte del grafico.
    : series: array dei valori da cui rimuovere il rumore (nel nostro caso le potenze)
    : return un array della stessa dimensione  
    '''
    n = 15
    b = [1.0 / n] * n
    a = 1
    filtered_series = lfilter(b,a,series)
    return filtered_series


def get_data_from_db(pressata, key):
    '''
    Returns all the database lines for the given key
    :param   string key from database
    :return  same type as source
    '''
    if not type(key) == str:
        raise Warning('Parameter key must be a string!')
    data = pressata[str(key)]
    return data

def normalize(array, plot=False):
    '''
    Takes an array as input, returns the same array with normalized values for `altezza` and `forza`.
    Plotting and Resizing features on request.
    :param array: array of numbers in the form [float1, float2, ... , floatN] or [int1, int2, ... , intN]
    :param size: Size you want the array to be resized to. (length)
    :return: normalized array & plot of the array if requested
    '''
    x_data = array['altezza']
    y_data = array['forza']
    lenx = len(x_data)
    leny = len(y_data)

    # Handling error for discordant lenghts for 'altezza' and 'forza'
    if lenx != leny:
        raise Warning('Illegal values! The number of elements for x axis and y axis should coincide.'
                      f'Instead you provided {lenx}, and {leny}, respectively!')

    # Strength data normalization
    # leaving x data untouched
    norm_ydata = [round(i/max(y_data), 4) for i in y_data]

    # Creating normalized array to preserve original
    normie = array
    normie['forza'] = norm_ydata

    # Plotting (optional)
    if plot == True:
        label = normie['id']
        plt.plot(normie, norm_ydata)
        plt.xlabel(label)
        graph = plt.show()
        return graph

    return normie


#Clipping
def clipping(height,force):
    max_value = max(height)
    index_max = height.index(max_value)
    del height[index_max+1:len(height)] 
    del force [index_max+1:len(force)]
    return height, force
