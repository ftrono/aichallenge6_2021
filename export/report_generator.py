from database_functions.db_connect import db_connect, db_disconnect
from export.export_to_csv import save_table_csv
from export.export_to_csv import save_table_warnings
from globals import *
import sys, logging, os
sys.path.insert(0, os.getcwd())
#sys.path.insert(0, './')
import pandas as pd
from database_functions.extract_data import Collector



def export_report(warneds=None, not_warneds=None, replace_all=False):
    '''
    Exports a report for each riduttore contained in passed list warneds
    param: warneds: list containing RiduttoreIDs with warnings
    return: None
    '''
    report_num = 0
    print("Generating reports with warnings")

    # Check for output folder
    if not os.path.isdir(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)
        print("output folder created: " + OUTPUT_PATH)

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
            SAVE_PATH_NAME = OUTPUT_PATH + '/' + str(warned_rid[0]) + '.csv'
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
        print("suck my balls!!")
    return None



def generate_report_riduttore(riduttore=None):
    '''
    Generates reports for the passed riduttore. Generates reports for all riduttori if no param is passed.
    If report is not amongst warnings, search will switch to Pressate table.
    param: riduttore (optional): int or string
    output: cvs files placed in OUTPUT_PATH folder.
    returns: None
    '''
    # Connect
    conn, cursor = db_connect()

    # Specified riduttore
    if riduttore is not None:
        warned_query = cursor.execute("SELECT DISTINCT RiduttoreID FROM Warnings "
                             "WHERE RiduttoreID = {}".format(riduttore))
        warned = warned_query.fetchone()[0]
        # Riduttore not in Warnings
        if warned is None:
            not_warned_query = cursor.execute("SELECT DISTINCT RiduttoreID FROM Pressate "
                                        "WHERE RiduttoreID = {}".format(riduttore))
            not_warned = not_warned_query.fetchone()[0]
            if not_warned is None:
                raise FileNotFoundError("No match found for riduttore {}".format(riduttore))
            else:
                save_table_warnings(riduttore_id=not_warned)
                # export_report(warneds=False, not_warned=not_warned)
                # print("Not Warned: {}".format(not_warned[0]))
                pass
        else:
            save_table_warnings(riduttore_id=warned)
            # export_report(warned, False, replace_all=True)
            # print("Warned: {}".format(warned[0]))

    # Unspecified riduttore
    else:
        tot_warned = pd.read_sql("SELECT DISTINCT RiduttoreID FROM Warnings", conn)
        tot_warneds = tot_warned.values.tolist()
        save_table_warnings(riduttore_id=tot_warneds)
        # export_report(warneds=tot_warneds, not_warneds=False, replace_all=True)


    # Disconnect
    db_disconnect(conn, cursor)

    return None


generate_report_riduttore()