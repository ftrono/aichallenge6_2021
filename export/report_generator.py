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

# Save query as dataframe
warned = pd.read_sql("SELECT DISTINCT RiduttoreID FROM Warnings", conn)
warneds = warned.values.tolist()

entire_db = pd.read_sql("SELECT Pressate.RiduttoreID, Pressate.ComboID, Pressate.MaxForza , Pressate.MaxAltezza, Warnings.WarningID, WarningDesc.Description " \
                        "FROM ((Pressate " \
                        "LEFT JOIN Warnings ON Warnings.RiduttoreID = Pressate.RiduttoreID) " \
                        "LEFT JOIN WarningDesc ON WarningDesc.WarningID = Warnings.WarningID)", conn)

#  RiduttoreID  , ComboID  , S  ,   H  ,   WarningID
# 20200911155707,p0003MP105,2.36,135.21,    <null>
# 20200911155707,p0037MP105,0.38,139.56,,   <null>
# 20200911155707,p0037MP105,0.38,139.56,,   <null>
# 20200911155707,p0031MP105,2.20,201.50,,   <null>
# 20200911155707,p0031MP105,2.20,201.50,,   <null>
# 20200911155707,a0210MP105,9.50,194.68,,
# 20200911155707,p0009MP105,19.33,179.20,,
# 20200429145134,a0007MP060,8.83,231.01,,
# 20200429145134,a0007MP060,8.83,231.01,,
# 20200429145134,p0038MP060,0.61,207.31,,
# 20200429145134,p0038MP060,9.75,209.25,,
# 20200429145134,p0038MP060,9.59,209.25,,
# 20200429145134,p0038MP060,1.21,209.06,,
# 20200429145134,a0007MP060,1.37,201.32,,
# 20200429145134,a0007MP060,7.60,194.01,,
# 20200429145134,a0205MP060,0.08,173.71,,
# 20200429145134,a0205MP060,0.05,173.76,,
# 20200915161048,a0210MP080,12.48,200.04,,
# 20200915161048,a0211MP080,3.13,278.90,,
# 20200915161048,a0211MP080,33.88,307.33,,


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
            approval = input(f"Report for riduttore {str(id_rid[0])} already exists. Do you want to replace it?\n[y: replace; n: don't replace; A: replace all: ")
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

if report_num == 1:
    print("1 report has been generated")
else:
    print(f"{report_num} reports have been generated")
































# replace_all = False
# report_num = 0
# print("Generating reports")
# for index, id_rid in enumerate(riduttores):
#     df_by_riduttore = df.loc[df['RiduttoreID'] == riduttores[index]].drop(labels='RiduttoreID', axis=1)
#     SAVE_PATH_NAME = '.' + OUTPUT_PATH + '/' + str(riduttores[index]) + '.csv'
#     # Check overwrite
#     if replace_all == True:
#         df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)
#         report_num += 1
#     # Ask for overwriting approval
#     else:
#         if os.path.isfile(SAVE_PATH_NAME):
#             approval = input(f"Report for riduttore {str(riduttores[index])} already exists. Do you want to replace it?\n[y: replace; n: don't replace; A: replace all: ")
#             if approval == 'y':
#                 df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)
#                 report_num += 1
#             elif approval == 'n':
#                 pass
#             elif approval == 'A' or approval == 'a':
#                 replace_all = True
#                 df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)
#                 report_num += 1
#         else:
#             df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)
#             report_num += 1
#
# if report_num == 1:
#     print("1 report has been generated")
# else:
#     print(f"{report_num} reports have been generated")





# disconnect
db_disconnect(conn, cursor)
