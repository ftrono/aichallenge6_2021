from utils import mongo_connect, mongo_disconnect, plot_series, normalize
from stats import get_stats
import matplotlib.pyplot as plt
from scipy.signal import lfilter
from scipy.ndimage import zoom
from tqdm import tqdm
import csv
import warnings

db,client = mongo_connect()
POSTS = db.test2

#_______________________________________________________
#ALL OF THE FOLLOWING ARE DISCARDED FUNCTIONS
#_______________________________________________________


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
    :param   key from database
    :return  same type as source
    '''
    data = pressata['steps'][0][str(key)]
    return data


#Clipping
def clipping(height,force):
    max_value = max(height)
    index_max = height.index(max_value)
    del height[index_max+1:len(height)] 
    del force [index_max+1:len(force)]
    return height, force


#Vertical normalization (original version):
def normalize_orig(array, plot=False):
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


#MAIN:
def old_stats_main():
    # Set up CSV properties
    fields = ['id', 'forza_media', 'forza_varianza', 'altezza_media', 'altezza_varianza']   # columns (fixed header row)
    rows = []                                                                               # rows
    filename = "stats_report.csv"                                                           # name of report

    # Ignoring Deprecation Warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    if db.test2.count() > 10000:
        warning = '(might take a while)'
    else:
        warning = ''
    print(f"📊 Computing Statistics... {warning}")

    # iterate rows searching by key
    for post in tqdm(POSTS.find(), total=db.test2.count()):

        # Actual statistics 📊
        id = get_data_from_db('id')                             # retrieve ID for `key`
        forza = get_data_from_db('forza')                       # retrieve strength for current ID
        forza_media = get_stats(forza, mean=True)               # retrieve average(mean) of given list
        altezza = get_data_from_db('altezza')                   # retrieve travel for current ID
        altezza_max = max(altezza)                              # (float)
        max_index = altezza.index(altezza_max)
        del altezza[max_index + 1 : len(altezza)]
        del forza[max_index + 1: len(forza)]
        altezza_media = get_stats(altezza, mean=True)           # retrieve average(mean) of given list
        forza_varianza = get_stats(forza, variance=True)        # retrieve variance of given list
        altezza_varianza = get_stats(altezza, variance=True)    # retrieve variance of given list

        # Prepare stats for CSV writer
        rows.append([id, round(forza_media, 2), round(forza_varianza, 2),
                         round(altezza_media, 2), round(altezza_varianza, 2)])


    print("Done analyzing")

    #writing csv file ✏️
    print("Writing data to csv file...")
    with open(filename, "w") as csv_file:
        #CSV object writer
        csvwriter = csv.writer(csv_file)

        csvwriter.writerow(fields)  # write headers
        csvwriter.writerows(rows)   # write data
    print("Report export succeeded")

    return 0


#Old module "do_the_hard_work.py":
def do_the_hard_work():
    i = 0
    for riduttore in POSTS.find():
        if i == 10:
            break
        for pressata in riduttore['steps']:
            if i == 10:
                break

            id = get_data_from_db(pressata, 'id')
            altezza = get_data_from_db(pressata, 'altezza')
            forza = get_data_from_db(pressata, 'forza')
            plot = plot_series(id, altezza, forza, title='Original')
            print(plot)

            # Filtering hi-frequencies
            hi_pass_forza, hi_pass_altezza = clipping(forza, altezza)
            # Filtering lo-frequencies
            filtered_altezza = filter_series(hi_pass_altezza)
            filtered_forza = filter_series(hi_pass_forza)


            # Saving changes...
            pressata['altezza'] = filtered_altezza
            pressata['forza'] = filtered_forza

            # Normalize array
            normalized_array = normalize(pressata)
            plot = plot_series(normalized_array['id'], normalized_array['altezza'], normalized_array['forza'], title='Norm+Filter')
            print(plot)

            print(f'id: {id}\n'
                f'forza: {normalized_array["forza"]}\n'
                f'altezza: {normalized_array["altezza"]}')
            i += 1
    
    return 0

# MOLTO IMPORTANTE ricordarsi di metterlo ogni volta che si apre una connessione
mongo_disconnect(client)
