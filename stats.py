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

def get_data_from_db(key):
    '''
    Returns all the database lines for the given key
    :param   key from database
    :return  same type as source
    '''
    data = post['steps'][0][str(key)]
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
        media = statistics.fmean(misura)
        return media
    if variance == True:
        varianza = statistics.variance(misura)
        return varianza
    return media, varianza


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

