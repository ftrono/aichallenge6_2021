import pandas as pa
from extract_data import extract_data 
from database_functions.db_connect import db_connect, db_disconnect
from utils import interpolate_curve
from globals import *
import os

def export_curves(dbt=None, timestamp=None, current=None, target=None, wid=None):
    close = False
    if not dbt:
        cnxn, cursor = db_connect()
        dbt = {'cnxn' = cnxn, 'cursor' = cursor}
        close = True

    if not current:
        current = extract_data(dbt, stype='current', timestamp=timestamp)
    if not target:
        target = extract_data(dbt, stype='target', comboid=current.comboid)
    if not wid:
        if not close:
            cnxn, cursor = db_connect()
            dbt = {'cnxn' = cnxn, 'cursor' = cursor}
            close = True
        query = "SELECT WarningID FROM Warnings WHERE Timestamp="+str(current.timestamp)
        cursor.execute(query)
        tup = cursor.fetchall()
        wid = float(tup[0])

    if len(current.forza) != len(target.forza):
        #current.altezza, current.forza = slice_curves(target.ma, current.altezza, current.forza)
        current.forza = interpolate_curve(target.altezza, current.altezza,current.forza)

    percorso= os.path.join(OUTPUT_PATH,str(current.comboid)+"_"+str(current.timestamp)+"_wid"+str(wid)+'.'+"csv")
    
    if USE_AVG == True:
        ci_boundup = [(target.forza[i]+target.std_curve_avg) for i in range(len(target.forza))]
        ci_boundlow = [(target.forza[i]-target.std_curve_avg) for i in range(len(target.forza))]
    else:
        ci_boundup = [(target.forza[i]+target.std[i]) for i in range(len(target.forza))]
        ci_boundlow = [(target.forza[i]-target.std[i]) for i in range(len(target.forza))]

    data = {'Target Altezza Combo':target.altezza, 'Target Forza Combo':target.forza, 'Forza':current.forza, 
    'Upper Boundary':ci_boundup, 'Lower Boundary':ci_boundlow}

    df = pd.DataFrame(data)
    df.to_csv(percorso) 
    if close:
        db_disconnect(cnxn, cursor)
    