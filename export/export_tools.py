import sys, os
import pandas as pd
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.db_connect import db_connect, db_disconnect

#EXPORT TOOLS:
# - prepend_lines()
# - warnings_stats()


#prepend informational lines to csv:
def prepend_lines(fpath, fout, lines):
    '''
    Insert informational lines at the beginning of a csv file.
    Input:
    - fout (str) -> full filename of original csv
    - temp (str) -> full filename of temporary csv to use
    - lines (list) -> list of string lines to prepend.
    '''
    #temp file:
    temp = fpath+"/temp.csv"
    header = True
    #open original file in read mode and temp file in write mode:
    with open(fout, 'r') as read_obj, open(temp, 'w') as write_obj:
        #first, write informational text to temp file:
        for line in lines:
            write_obj.write(str(line) + '\n')
        #second, migrate original file (fout) to temp, line by line:
        for line in read_obj:
            if header == True:
                #add Index keyword to header:
                extline = "Index"+line
                write_obj.write(extline)
                header = False
            else:
                #migrate all other lines:
                write_obj.write(line)
    #remove original file:
    os.remove(fout)
    #rename temp file as the original file:
    os.rename(temp, fout)
    return 0


#extract Warnings statistics and extended table with all info:
def warnings_stats():
    cnxn, cursor = db_connect()

    query = "SELECT Warnings.WarningID, Warnings.RiduttoreID, Warnings.Timestamp, Pressate.Stazione, Pressate.ComboID, Riduttori.Master, Riduttori.Rapporto, Riduttori.Stadi, Riduttori.Cd FROM Warnings INNER JOIN Pressate on Warnings.Timestamp = Pressate.Timestamp INNER JOIN Riduttori on Pressate.RiduttoreID = Riduttori.RiduttoreID"
    FullWarnings = pd.read_sql(query, cnxn)

    rids = FullWarnings['RiduttoreID'].unique().tolist()
    timestamps = FullWarnings['Timestamp'].unique().tolist()
    wids = FullWarnings['WarningID'].unique().tolist()
    header = "Riduttori,Timestamps"
    values = str(len(rids))+","+str(len(timestamps))
    for wid in sorted(wids):
        SubsetWid = FullWarnings[FullWarnings["WarningID"] == int(wid)]
        header = header+",WID"+str(wid)
        values = values+","+str(SubsetWid["WarningID"].count())
    
    #dataframe export:
    fout = OUTPUT_PATH+"/WarningsStats.csv"
    FullWarnings.to_csv(fout)

    #insert informational text:
    lines = [header, values]
    prepend_lines(OUTPUT_PATH, fout, lines)
    print("Exported.")

    db_disconnect(cnxn, cursor)
    return 0
