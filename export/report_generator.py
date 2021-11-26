from database_functions.db_connect import db_connect, db_disconnect
from export.export_to_csv import save_table_csv
from globals import *
import sys, logging, os
sys.path.insert(0, os.getcwd())
#sys.path.insert(0, './')
import pandas as pd
from database_functions.extract_data import Collector

# FRAMEWORK
# 1. Raggruppare per riduttore
# 2. Creare csv (per ciascun riduttore)
# 3. Inserire dati raggruppati per combo
# 4. Struttura della tabella
#    | ComboID | MaxForza | MaxAltezza | Stazione | WarningID | Description  |
#    -----------------------------------------------------------------------
#    |          |          |            |          |           |             |
#    | {bigint} |  ###.##  |   ###.##   | {string} | {1,2,3,4} |  {string}   |
#    |          |          |            |          |           |             |
#    |          |          |            |          |           |             |


def generate_report(riduttore=None):
    # connect
    conn, cursor = db_connect()

    if not riduttore:
        # Save riduttori with warnings
        warned = pd.read_sql("SELECT DISTINCT RiduttoreID FROM Warnings", conn)
        warneds = warned.values.tolist()

        # Extract entire database
        entire_db = pd.read_sql(
            "SELECT Pressate.Timestamp, Pressate.RiduttoreID, Pressate.ComboID, Pressate.MaxForza , Pressate.MaxAltezza, Warnings.WarningID, WarningDesc.Description " \
            "FROM ((Pressate " \
            "LEFT JOIN Warnings ON Warnings.RiduttoreID = Pressate.RiduttoreID) " \
            "LEFT JOIN WarningDesc ON WarningDesc.WarningID = Warnings.WarningID)", conn)

    else:
        warned = pd.read_sql("SELECT RiduttoreID FROM Warnings WHERE RiduttoreID = {}".format(riduttore), conn)

        if warned.isnull:
            print(f"Riduttore {riduttore} non ha warnings. Cercare comunque tra i riduttori senza warnings?")
            while True:
                approval = input("<y/n>: ")
                if approval != "y" or "n" or "Y" or "N":
                    pass
                elif input == "y" or "Y":
                    warneds = pd.read_sql("SELECT RiduttoreID FROM Pressate WHERE RiduttoreID = {}".format(riduttore), conn)
                    break
                else:
                    break





# TODO: INSERIRE IL MAIN (SOTTO) IN generate_reports()
replace_all = False
report_num = 0
print("Generating reports")
for id_rid in warneds:
    df_by_riduttore = entire_db.loc[entire_db['RiduttoreID'] == id_rid[0]].drop(labels='RiduttoreID', axis=1)
    SAVE_PATH_NAME = '.' + OUTPUT_PATH + '/' + str(id_rid[0]) + '.csv'
    # Check overwrite
    if replace_all == True:
        df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)
        report_num += 1
    # Ask for overwriting approval
    else:
        if os.path.isfile(SAVE_PATH_NAME):
            approval = input(f"Report for riduttore {str(id_rid[0])} already exists. Do you want to replace it?\n<y: replace; n: don't replace; A: replace all> : ")
            if approval == 'y':
                df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)
                report_num += 1
            elif approval == 'n':
                pass
            elif approval == 'A' or approval == 'a':
                replace_all = True
                df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)
                report_num += 1
        else:
            df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)
            report_num += 1

    # Extract current data
    current = Collector()
    current.timestamp = df_by_riduttore.Timestamp

if report_num == 1:
    print("1 report has been generated")
else:
    print(f"{report_num} reports have been generated")

# disconnect
db_disconnect(conn, cursor)
