# TODO: per ogni punto, a parità di altezza --> media + varianza

import statistics, csv
from tqdm import tqdm
import warnings
import pymongo
from pymongo import MongoClient
from utils import mongo_connect, mongo_disconnect
from access_db import find_duplicates, query_bycombo


db, client = mongo_connect()
POSTS = db.test2                #getting collection test2

def get_data_from_db(pressata, key):
    '''
    Returns all the database lines for the given key
    :param   key from database
    :return  same type as source
    '''
    data = pressata['steps'][0][str(key)]
    return data


def get_stats(misura):
    '''
    Computes mean and variance of all the elements contained in the list misura
    :param mean: Bool
    :param variance: Bool
    :param misura: array
    :return: (float, float)
    '''

    media = statistics.stdev(misura)
    varianza = statistics.stdev(misura)

    return media, varianza


def ideal_curve(input):
    '''
    Function to compute the ideal curve for a specific combination given by 
    the mean value between its points on the x-axis 

    Parameters
    input : list of list
        It's the collection of already normalized series of which we want to 
        compute the ideal behaviour. That said it is critical that each series 
        should be of the same size!

    Returns
    out : list
        A list contining the average value of each point in all the series, 
        it's lenght is the same as the one of every series

    '''
    out = []
    for i in range(0,len(input[0])):
        temp = []
        for j in range(0, len(input)):
            temp.append(input[j][i])
        avg, v = get_stats(temp)
        out.append(avg)
    return out

def threshold_variance(input):
    '''
    Function to compute the average variance value to be used as threshold 
    when looking if a new sample will be in or out the ideal curve

    Parameters
    ----------
    input : list of list
        It's the collection of already normalized series of which we want to 
        compute the ideal behaviour. That said it is critical that each series 
        should be of the same size!

    Returns
    -------
    avg_var : double
        A list contining the average value of each point in all the series, 
        it's lenght is the same as the one of every series

    '''
    var_list = []
    for i in range(0,len(input[0])):
        temp = []
        for j in range(0, len(input)):
            temp.append(input[j][i])
        a, var = get_stats(temp)
        var_list.append(var)
    avg_var, v = get_stats(var_list)
    return avg_var

def max_force_threshold(max_values):
    '''
    From a list of max strength values for each series, then finds the average 
    to be used as reference for this configuration. 
    Moreover it computes a value (the standard deviaion) for accepting or not 
    a new data 
    
    Parameters
    ----------
    max_values : list 
        List containing the max force applied for each series

    Returns
    -------
    max_force : double 
        Average force from all the series given as input
    threshold : double
        The standard deviation of the list collecting all of the max force for 
        each series

    '''
    avg, threshold = get_stats(max_values)
    return avg, threshold

def batch_standardize(taglia,idcomp):
    '''
    Function that computes the query selecting taglia and idcomp and 
    create a variable called combo; then for every series in the combo it appends
    on the list "batch_forces" -> 'forza' (list of the list) and
    it appends on the list "batch_max" -> 'max_forza'(list). 

    It puts togheter different functions:
    - query_bycombo(taglia,idcomp)
    - ideal_curve(input)
    - threshold_variance(input)
    - max_force_threshold(input)

    Parameters:
    --------------
    input : taglia and idcomp : string
    String containig the taglia of "riduttore" and id of the "componente"

    Returns
    -------------
    Output : 4 parameters
    - curva_ideale (list)
    - avg_var (double)
    - max_force (double)
    - threshold (oudble)
    
    '''
    batch_forces = []
    batch_max = []
    
    combo = query_bycombo(taglia,idcomp)
    for series in combo.series:
        batch_forces.append(series.forza)
        batch_max.append(series.max_forza)
    
    curva_ideale = ideal_curve(batch_forces)
    avg_var = threshold_variance(batch_forces)
    max_force,threshold = max_force_threshold(batch_max)

    return curva_ideale,avg_var,max_force,threshold

if __name__ == '__main__':

    # Set up CSV properties
    fields = ['id', 'forza_media', 'forza_varianza', 'altezza_media', 'altezza_varianza']   # columns (fixed header row)
    rows = []                                                                               # rows
    filename = "stats_report.csv"                                                           # name of report

    # Ignoring Deprecation Warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    if db.test2.count() > 10000:
        warning = '(might take a while)'
    else:
        warnings = ''
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

