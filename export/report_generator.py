from database_functions.db_connect import db_connect, db_disconnect
from export.export_to_csv import save_table_csv
from globals import *
import os
import pandas as pd

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

# connect
conn, cursor = db_connect()

# TODO: MODIFY query SO AS TO MAKE IT GET NOT ONLY WARNING-FLAGGED RIDUTTORI

query = ("SELECT Pressate.RiduttoreID, Pressate.ComboID, Pressate.MaxForza , Pressate.MaxAltezza, Pressate.Stazione, Warnings.WarningID, WarningDesc.Description FROM ((Pressate LEFT JOIN Warnings ON Warnings.RiduttoreID = Pressate.RiduttoreID) LEFT JOIN WarningDesc ON WarningDesc.WarningID = Warnings.WarningID)")

# Save query as dataframe
df = pd.read_sql(query, conn)
riduttores = df['RiduttoreID'].unique()

# Check if folder path already exists
if not os.path.isdir('.' + OUTPUT_PATH):
    os.mkdir('.' + OUTPUT_PATH)

replace_all = False
report_num = 0
print("Generating reports")
for index, id_rid in enumerate(riduttores):
    df_by_riduttore = df.loc[df['RiduttoreID'] == riduttores[index]].drop(labels='RiduttoreID', axis=1)
    SAVE_PATH_NAME = '.' + OUTPUT_PATH + '/' + str(riduttores[index]) + '.csv'
    # Check overwrite
    if replace_all == True:
        df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)
        report_num += 1
    # Ask for overwriting approval
    else:
        if os.path.isfile(SAVE_PATH_NAME):
            approval = input(f"Report for riduttore {str(riduttores[index])} already exists. Do you want to replace it?\n[y: replace; n: don't replace; A: replace all: ")
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


if report_num == 1:
    print("1 report has been generated")
else:
    print(f"{report_num} reports have been generated")





# disconnect
db_disconnect(conn, cursor)
