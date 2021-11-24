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
#    | Combo | ... | Warning | Warning_description |
#    -----------------------------------------------
#    |       | ... |         |                     |
#    |       | ... |         |                     |
#    |       | ... |         |                     |

# connect
conn, cursor = db_connect()

query = ("SELECT Pressate.RiduttoreID, Pressate.ComboID, Pressate.MaxForza , Pressate.MaxAltezza, Pressate.Stazione, Warnings.WarningID, WarningDesc.Description FROM ((Pressate INNER JOIN Warnings ON Warnings.RiduttoreID = Pressate.RiduttoreID) INNER JOIN WarningDesc ON WarningDesc.WarningID = Warnings.WarningID) WHERE Warnings.WarningID != 0")

# Save query as dataframe
df = pd.read_sql(query, conn)
riduttores = df['RiduttoreID'].unique()

# Check if folder path already exists
if not os.path.isdir('.' + OUTPUT_PATH):
    os.mkdir('.' + OUTPUT_PATH)

for index, id_rid in enumerate(riduttores):
    df_by_riduttore = df.loc[df['RiduttoreID'] == riduttores[index]].drop(labels='RiduttoreID', axis=1)
    SAVE_PATH_NAME = '.' + OUTPUT_PATH + '/' + str(riduttores[index]) + '.csv'
    # Check overwrite
    if os.path.isfile(SAVE_PATH_NAME):
        approval = input(f"Report for riduttore {str(riduttores[index])} already exists. Do you want to replace it?\n[y: replace; n: don't replace; A: replace all; N: replace none]: ")
        if approval == 'y':
            df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)
        elif approval == 'n':
            pass
    else:
        df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)





# disconnect
db_disconnect(conn, cursor)
