from database_functions.db_connect import db_connect, db_disconnect
from export.export_to_csv import save_table_csv
from globals import *
import sys, logging, os
sys.path.insert(0, os.getcwd())
#sys.path.insert(0, './')
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


def export_report(warneds=None, not_warneds=None, replace_all=False):
    '''
    Exports a report for each riduttore contained in passed list warneds
    param: warneds: list containing RiduttoreIDs with warnings
    return: None
    '''
    report_num = 0
    print("Generating reports with warnings")

    # Check for output folder
    if not os.path.isdir('.' + OUTPUT_PATH):
        os.mkdir('.' + OUTPUT_PATH)
        print("output folder created: ." + OUTPUT_PATH)

    if warneds != None:
        # Iterate through passed list
        print("entering for loop...")
        for warned_rid in warneds:
            print("handling riduttore {}".format(warned_rid[0]))
            warned_db = pd.read_sql(
                "SELECT Pressate.Timestamp, Pressate.RiduttoreID as Riduttore, Pressate.ComboID as Combo, "
                "Pressate.MaxForza as TargetForza, Pressate.MaxAltezza as TargetAltezza, "
                "Warnings.WarningID as Warning, WarningDesc.Description "
                "FROM Pressate, Warnings, WarningDesc "
                "WHERE Pressate.RiduttoreID = {}".format(warned_rid[0]), conn)
            SAVE_PATH_NAME = '.' + OUTPUT_PATH + '/' + str(warned_rid[0]) + '.csv'
            # Check overwrite
            if replace_all == True:
                print("replace_all = True")
                warned_db.to_csv(SAVE_PATH_NAME, index=False)
                report_num += 1
                pass
            # Ask for overwriting approval
            else:
                if os.path.isfile(SAVE_PATH_NAME):
                    approval = input("Report for riduttore {} already exists. Do you want to replace it?\n"
                                     "<y: replace; n: don't replace; A: replace all>  ".format(warned_rid[0]))
                    if approval == 'y' or 'Y':
                        warned_db.to_csv(SAVE_PATH_NAME, index=False)
                        report_num += 1
                    elif approval == 'n' or 'N':
                        pass
                    elif approval == 'a' or 'A':
                        replace_all = True
                        warned_db.to_csv(SAVE_PATH_NAME, index=False)
                        report_num += 1
                    else:
                        raise SyntaxError("Invalid input key. Please choose a valid key.")
    if not_warneds:
        print("She sells seashells on the seashore!!")
    return None






# Connect
conn, cursor = db_connect()

def generate_report(riduttore=False):
    # Specified riduttore
    if not riduttore == False:
        warned_query = cursor.execute("SELECT DISTINCT RiduttoreID FROM Warnings "
                             "WHERE RiduttoreID = {}".format(riduttore))
        warned = warned_query.fetchone()
        # riduttore not in Warnings
        if warned == None:
            not_warned_query = cursor.execute("SELECT DISTINCT RiduttoreID FROM Pressate "
                                        "WHERE RiduttoreID = {}".format(riduttore))
            not_warned = not_warned_query.fetchone()
            if not_warned == None:
                raise FileNotFoundError("No match found for riduttore {}".format(riduttore))
            else:
                export_report(warneds=False, not_warned=not_warned)
                # print("Not Warned: {}".format(not_warned[0]))
                pass
        else:
            export_report(warned=warned, not_warneds=False, replace_all=True)
            # print("Warned: {}".format(warned[0]))

    # Unspecified riduttore
    else:
        tot_warned = pd.read_sql("SELECT DISTINCT RiduttoreID FROM Warnings", conn)
        tot_warneds = tot_warned.values.tolist()
        export_report(warneds=tot_warneds, not_warneds=False, replace_all=True)



        # MAIN EXTRACTION HERE
        # print(warned.fetchone()[0])
    return None

generate_report()




# disconnect
db_disconnect(conn, cursor)









# BACKUP COPY OF FUNCTION, DO NOT DELETE --> KEEP AS IT IS
# replace_all = False
# report_num = 0
# print("Generating reports")
# for id_rid in warneds:
#     df_by_riduttore = entire_db.loc[entire_db['RiduttoreID'] == id_rid[0]].drop(labels='RiduttoreID', axis=1)
#     SAVE_PATH_NAME = '.' + OUTPUT_PATH + '/' + str(id_rid[0]) + '.csv'
#     # Check overwrite
#     if replace_all == True:
#         df_by_riduttore.to_csv(SAVE_PATH_NAME, index=False)
#         report_num += 1
#     # Ask for overwriting approval
#     else:
#         if os.path.isfile(SAVE_PATH_NAME):
#             approval = input(f"Report for riduttore {str(id_rid[0])} already exists. Do you want to replace it?\n[y: replace; n: don't replace; A: replace all: ")
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
