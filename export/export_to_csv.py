import pandas as pd
import sys, logging,os

from pandas.core.frame import DataFrame
sys.path.insert(0, os.getcwd())
#sys.path.insert(0, './')
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
    percorso= os.path.join(OUTPUT_PATH,table_name+'.'+"csv")
    df.to_csv(percorso,index=False)
    db_disconnect(conn,cursor)
    
    return 0

def save_table_warnings(combo_id):
    '''
    Function that save a table warnings of db in a file with extension as 'formato'. '
    The file is located in OUTPUT_PATH with name "combo_id"+Warning.csv.
    For example: 
    a0215MP080Warning.csv

    Input:
    - combo_id :  string
    

    '''
    conn,cursor = db_connect()
    sql_query = pd.read_sql_query("SELECT Pressate.Timestamp, Pressate.ComboID, Warnings.WarningID FROM Pressate INNER JOIN Warnings ON (Warnings.Timestamp = Pressate.Timestamp) WHERE Pressate.ComboID='"+str(combo_id)+"'",conn)
    df = pd.DataFrame(sql_query)
    if not os.path.isdir(OUTPUT_PATH):
        os.mkdir(OUTPUT_PATH)
    percorso= os.path.join(OUTPUT_PATH,combo_id +"Warning"+'.'+"csv")
    df.to_csv(percorso,index=False)    
    db_disconnect(conn,cursor)


    return 0

#save_table_warnings("a0215MP080")