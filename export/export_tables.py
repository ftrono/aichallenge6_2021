import pandas as pd
import sys, os
from collections.abc import Iterable
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.db_connect import db_connect, db_disconnect



def save_table_csv(table_name):
    '''
    Function that save a table of db in a file with extension as csv
    The file is located in OUTPUT_PATH with name "table_name".csv.
    For example: 
    dbo.Combos.csv

    Input:
    - table_name :  string
    
    '''
    conn,cursor = db_connect()
    sql_query = pd.read_sql_query("SELECT * FROM "+str(table_name),conn)
    df = pd.DataFrame(sql_query)
    if not os.path.isdir(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)
    percorso= os.path.join(OUTPUT_PATH,table_name+".csv")
    df.to_csv(percorso,index=False)
    db_disconnect(conn,cursor)
    return 0


def save_table_warnings(combo_id=None, timestamp=None, riduttore_id=None,wid=None,stazione=None):
    '''
    Function that saves a table warnings of db in a file with extension as 'formato'. '
    The file is located in OUTPUT_PATH with name "combo_id"+Warning.csv.
    NOTE: Reports previously generated (also with the same name) will be replaced!
    For example:
    a0215MP080Warning.csv

    Input:
    - combo_id : string
    - timestamp: string
    - riduttore_id: string, int or list
    - wid (warningID): string
    - stazione  : string
    '''
    # Connect
    conn,cursor = db_connect()

    num_generated = 0
    if combo_id and (not timestamp) and (not riduttore_id) and (not wid) and (not stazione):
        sql_query = pd.read_sql_query("SELECT Pressate.Timestamp, Pressate.RiduttoreID, Pressate.ComboID, Pressate.Stazione, Warnings.WarningID FROM Pressate INNER JOIN Warnings ON (Warnings.Timestamp = Pressate.Timestamp) WHERE Pressate.ComboID={}".format(combo_id),conn)
        df = pd.DataFrame(sql_query)
        if not os.path.isdir(OUTPUT_PATH):
            os.mkdir(OUTPUT_PATH)
        percorso= os.path.join(OUTPUT_PATH,combo_id +"Warnings.csv")
        df.to_csv(percorso,index=False)
        num_generated += 1

    elif (not combo_id) and timestamp and (not riduttore_id) and (not wid) and (not stazione):
        sql_query = pd.read_sql_query("SELECT Pressate.Timestamp, Pressate.RiduttoreID, Pressate.ComboID, Pressate.Timestamp, Pressate.Stazione, Warnings.WarningID FROM Pressate INNER JOIN Warnings ON (Warnings.Timestamp = Pressate.Timestamp) WHERE Warnings.Timestamp={}".format(timestamp),conn)
        df = pd.DataFrame(sql_query)
        if not os.path.isdir(OUTPUT_PATH):
            os.mkdir(OUTPUT_PATH)
        percorso= os.path.join(OUTPUT_PATH, timestamp +"Warnings.csv")
        df.to_csv(percorso,index=False)
        num_generated += 1

    elif (not combo_id) and (not timestamp) and riduttore_id and (not wid)and (not stazione):
        if not os.path.isdir(OUTPUT_PATH):
            os.mkdir(OUTPUT_PATH)
        # riduttore_id is a list
        if isinstance(riduttore_id, Iterable):
            for rid in riduttore_id:
                sql_query = pd.read_sql_query("SELECT Pressate.Timestamp, Pressate.RiduttoreID, Pressate.ComboID, Pressate.Timestamp, Pressate.Stazione, Warnings.WarningID FROM Pressate INNER JOIN Warnings ON (Warnings.Timestamp = Pressate.Timestamp) WHERE Pressate.RiduttoreID={}".format(rid[0]),conn)
                df = pd.DataFrame(sql_query)
                percorso = os.path.join(OUTPUT_PATH, str(rid[0]) + "Warnings.csv")
                df.to_csv(percorso, index=False)
                num_generated += 1
        # riduttore is a string or int
        elif not isinstance(riduttore_id, Iterable):
            sql_query = pd.read_sql_query("SELECT Pressate.Timestamp, Pressate.RiduttoreID, Pressate.ComboID, Pressate.Timestamp, Pressate.Stazione, Warnings.WarningID FROM Pressate INNER JOIN Warnings ON (Warnings.Timestamp = Pressate.Timestamp) WHERE Pressate.RiduttoreID={}".format(riduttore_id),conn)
            df = pd.DataFrame(sql_query)
            percorso= os.path.join(OUTPUT_PATH,str(riduttore_id) + "Warnings.csv")
            df.to_csv(percorso,index=False)
            num_generated += 1
        else:
            raise TypeError("Riduttore must be either string, int or list.")

    elif (not combo_id) and (not timestamp) and (not riduttore_id) and wid and (not stazione):
        sql_query = pd.read_sql_query("SELECT Pressate.Timestamp, Pressate.RiduttoreID, Pressate.ComboID, Pressate.Timestamp, Pressate.Stazione, Warnings.WarningID FROM Pressate INNER JOIN Warnings ON (Warnings.Timestamp = Pressate.Timestamp) WHERE Warnings.WarningID={}".format(wid),conn)
        df = pd.DataFrame(sql_query)
        if not os.path.isdir(OUTPUT_PATH):
            os.mkdir(OUTPUT_PATH)
        percorso= os.path.join(OUTPUT_PATH,wid +"Warnings.csv")
        df.to_csv(percorso,index=False)
        num_generated += 1

    elif (not combo_id) and (not timestamp) and (not riduttore_id) and (not wid) and stazione:
        sql_query = pd.read_sql_query("SELECT Pressate.Timestamp, Pressate.RiduttoreID, Pressate.ComboID, Pressate.Timestamp, Pressate.Stazione, Warnings.WarningID FROM Pressate INNER JOIN Warnings ON (Warnings.Timestamp = Pressate.Timestamp) WHERE Pressate.Stazione={}".format(stazione),conn)
        df = pd.DataFrame(sql_query)
        if not os.path.isdir(OUTPUT_PATH):
            os.mkdir(OUTPUT_PATH)
        percorso= os.path.join(OUTPUT_PATH,stazione +"Warnings.csv")
        df.to_csv(percorso,index=False)
        num_generated += 1

    # Disconnect
    db_disconnect(conn,cursor)
    if num_generated == 1:
        print("1 report generated.")
    else:
        print("{} reports generated.".format(num_generated))

    return 0

