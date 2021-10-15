# TODO: group statistics by id before writing csv (due 10/16/21)
# TODO: chech for duplicates (due 10/16/21)

import statistics, math, csv
from tqdm import tqdm
import warnings
import pymongo
from pymongo import MongoClient
from utils import mongo_connect, mongo_disconnect

db, client = mongo_connect()
POSTS = db.test2 #getting collection test2

def get_infos(key):
    '''
    Returns ALL the queries associated with the parameter key (string) passed
    :param   key from database
    :return  same type as source
    '''
    infos = post['steps'][0][str(key)]
    return infos

def get_stats(misura, mean=False, variance=False):
    '''
    :param mean: Bool
    :param variance: Bool
    :param misura: any
    :return: (float, float)
    '''
    if mean == True:
        media = statistics.fmean(misura)
        return media
    if variance == True:
        varianza = statistics.variance(misura)
        return varianza
    return media, varianza


# Set up CSV properties
fields = ['id', 'forza_media', 'forza_varianza', 'altezza_media', 'altezza_varianza']   # columns
rows = []                                                                               # rows
filename = "stats_report.csv"                                                           # name of report

# Ignoring Deprecation Warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# iterate rows searching by key
i = 0
if db.test2.count() > 10000:
    warning = '(might take a while)'
else:
    warnings = ''
print(f"📊 Computing Statistics... {warning}")
for post in tqdm(POSTS.find(), total=db.test2.count()):
    if i > 0:
        break
    # Actual statistics 📊
    id = get_infos('id')                                    # retrieve ID for `key`
    forza = get_infos('forza')                              # retrieve strength for current ID
    forza_media = get_stats(forza, mean=True)               # retrieve average(mean) of given list
    altezza = get_infos('altezza')                          # retrieve travel for current ID
    altezza_media = get_stats(altezza, mean=True)           # retrieve average(mean) of given list
    forza_varianza = get_stats(forza, variance=True)        # retrieve variance of given list
    altezza_varianza = get_stats(altezza, variance=True)    # retrieve variance of given list

    # Prepare stats for CSV writer
    rows.append([id,
                 round(forza_media,2), round(forza_varianza,2),
                 round(altezza_media,2), round(altezza_varianza,2)])
print("Done analyzing")

#writing csv file ✏️
print("Writing data to csv file...")
with open(filename, "w") as csv_file:
    #CSV object writer
    csvwriter = csv.writer(csv_file)

    csvwriter.writerow(fields)  # write headers
    csvwriter.writerows(rows)   # write data
print("Report export succeeded")

