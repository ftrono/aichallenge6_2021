import pandas as pd
import matplotlib.pyplot as plt
import sys, os
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.extract_data import extract_data 
from database_functions.db_connect import db_connect, db_disconnect
from training.training_tools import slice_curves, interpolate_curve

#CURVES PLOTTING:
# - get_boundaries() - upper and lower boundary
# - export_curves() - to csv
# - visualize() - to png or to a Matplotlib window


#get upper and lower boundaries:
def get_boundaries(target):
    '''
    Get the upper and lower boundaries for evaluating a curve.
    
    Parameters:
    -------------------
    input:
    - target (Collector) -> Collector object with the targets for the Combo
    
    output:
    - boundup (lists) -> upper curve boundary in vector format
    - boundlow (lists) -> lower curve boundary in vector format
    '''
    if USE_AVG == True:
        #if average stdev:
        boundup = [(target.forza[i] + (target.std_curve_avg*SIGMA_CURVE)) for i in range(len(target.forza))]
        boundlow = [(target.forza[i] - (target.std_curve_avg*SIGMA_CURVE)) for i in range(len(target.forza))]
    else:
        #if stdev vector:
        boundup = [(target.forza[i] + (target.std[i]*SIGMA_CURVE)) for i in range(len(target.forza))]
        #limit lower boundary:
        #use average stdev as threshold if below zero:
        min_low = -target.std_curve_avg*SIGMA_CURVE
        boundlow = []
        for i in range(len(target.forza)):
            p = target.forza[i] - (target.std[i]*SIGMA_CURVE)
            if p >= min_low:
                boundlow.append(p)
            else:
                boundlow.append(min_low)
    return boundup, boundlow


#export to csv needed curves for visualization:
def export_curves(dbt=None, timestamp=None, current=None, target=None, wid=None):
    close = False
    if not dbt:
        cnxn, cursor = db_connect()
        dbt = {'cnxn': cnxn, 'cursor': cursor}
        close = True

    if not current:
        current = extract_data(dbt, stype='current', timestamp=timestamp)
    if not target:
        target = extract_data(dbt, stype='target', comboid=current.comboid)
    if not wid:
        if not close:
            cnxn, cursor = db_connect()
            dbt = {'cnxn': cnxn, 'cursor': cursor}
            close = True
        try:
            query = "SELECT WarningID FROM Warnings WHERE Timestamp="+str(current.timestamp)
            cursor.execute(query)
            tup = cursor.fetchall()
            wid = float(tup[0])
        except:
            wid = 0

    if len(current.forza) != len(target.forza):
        current.altezza, current.forza = slice_curves(target.altezza, current.altezza, current.forza)
        current.forza = interpolate_curve(target.altezza, current.altezza,current.forza)

    percorso= os.path.join(OUTPUT_PATH,"curves/"+str(current.comboid)+"_"+str(current.timestamp)+"_wid"+str(wid)+".csv")
    
    #boundaries:
    if target.boundup == [] or target.boundlow == []:
        target.boundup, target.boundlow = get_boundaries(target)

    data = {'Target Altezza Combo':target.altezza, 'Target Forza Combo':target.forza, 'Forza':current.forza, 
    'Upper Boundary': target.boundup, 'Lower Boundary': target.boundlow}

    df = pd.DataFrame(data)
    df.to_csv(percorso) 

    if close:
        db_disconnect(cnxn, cursor)
    return 0


#Visualize ideal curve, boundaries & current curve:
def visualize(current, target, wid=0, count_out=0, threshold=0, window=WINDOW, save=SAVE_PNG):
    '''
    Visualize the curves plot by either opening a Matplotlib window (note: will pause the process!) or saving it as png file.

    Parameters:
    -------------------
    input:
    - current (Collector) -> Collector object with the data for the current Pressata
    - target (Collector) -> Collector object with the targets for the Combo
    - wid (int) -> warning ID (if any)
    - count_out (int) -> count of points out of bounds
    - threshold (int) -> max number of points out allowed
    - window (bool) -> visualize the curves plot by opening a Matplotlib window (note: will pause the process!)
    - save (bool) -> saves the curves plot as png file.
    
    '''
    #title and filename:
    if count_out != 0:
        co = " - Points out: "+str(count_out)+"/"+str(threshold)
    else:
        co = ""
    title = "ComboID: "+str(current.comboid)+" - Timestamp: "+str(current.timestamp)+" - WID: "+str(wid)+co
    fout = OUTPUT_PATH+"/curves/"+str(current.comboid)+"_"+str(current.timestamp)+"_wid"+str(wid)+".png"

    #title color:
    if wid == 0:
        titcolor = 'green'
    else:
        titcolor = 'firebrick'

    #plot:
    plt.clf()
    plt.plot(target.altezza, target.forza, color='limegreen', linewidth=4, label="Ideal curve")
    plt.plot(target.altezza, target.boundup, color='orange', linestyle='--', linewidth=1, label="Upper boundary")
    plt.plot(target.altezza, target.boundlow, color='red', linestyle='--', linewidth=1, label="Lower boundary")
    plt.plot(target.altezza, current.forza, color='blue', linewidth=2, label="CURRENT CURVE")
    plt.xlabel('Altezza (mm)')
    plt.ylabel('Forza (kN)')
    plt.legend(fontsize='x-small', frameon=False)
    plt.title(title, fontsize='small', fontweight='bold', color=titcolor)
    if save == True:
        plt.savefig(fout)
    if window == True:
        plt.show()
    return 0
