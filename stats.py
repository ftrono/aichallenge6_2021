# TODO: per ogni punto, a parità di altezza --> media + varianza

import statistics, csv
from tqdm import tqdm
import warnings
import pymongo
from pymongo import MongoClient
from utils import mongo_connect, mongo_disconnect
from access_db import find_duplicates

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


def get_stats(misura, mean=False, variance=False):
    '''
    Computes mean and variance of all the elements contained in the list misura
    :param mean: Bool
    :param variance: Bool
    :param misura: list
    :return: (float, float)
    '''
    if mean == True:
        media = statistics.stdev(misura)
        return media
    if variance == True:
        varianza = statistics.stdev(misura)
        return varianza
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
        avg = get_stats(temp, mean=True, variance=False)
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
        var = get_stats(temp, mean=False, variance=True)
        var_list.append(var)
    avg_var = get_stats(var_list, mean=True, variance=False)
    return avg_var

def batch_standardize(input):
    '''
    From a list of strength values find the maximum one to be used as reference
    for this configuration. Moreover it computes a value (the standerd deviaion)
    for accepting or not a new data 
    
    Parameters
    ----------
    input : list of list
        It's the collection of already normalized series of which we want to 
        compute the ideal behaviour. That said it is critical that each series 
        should be of the same size!

    Returns
    -------
    max_force : double 
        It's the highest value of the force for all the series given as input
    threshold : double
        The standard deviation of the list collecting all of the max force for 
        each series

    '''
    max_values = []
    for l in input:
        max_values.append(max(l))
    max_force = max(max_values)
    threshold = get_stats(max_values, mean=False, variance=True)
    return max_force, threshold

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

