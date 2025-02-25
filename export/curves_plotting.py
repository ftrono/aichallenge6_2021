import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone
import sys, os
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.extract_data import extract_data 
from database_functions.db_connect import db_connect, db_disconnect, pd_db_connect
from training.training_tools import slice_curves, interpolate_curve, get_boundaries
from export.export_tools import prepend_lines

#CURVES PLOTTING:
# - commons_generator()
# - export_curves() - to csv
# - visualize() - to png or to a Matplotlib window


#filenames & informational text generator:
def commons_generator(current, wid, ftype):
    '''
    Generate filename and informational text for both the png plot and the csv export.
    Input:
    - current (Collector) - Collector object with the data for the current Pressata
    - wid (int)
    - ftype (str) -> must be either 'png' or 'csv' (no points).
    '''
    #directory:
    fpath = OUTPUT_PATH+"/curves/"+str(current.comboid)
    if not os.path.isdir(fpath):
        os.mkdir(fpath)
    #filename:
    fout = fpath+"/"+str(current.riduttoreid)+"_"+str(current.timestamp)+"_wid"+str(wid)+"."+ftype
    str_ma = str(SIGMA_MA) if CHECK_MA else "n/a"
    #informational text:
    if ftype == 'png':
        text1 = "ComboID: "+str(current.comboid)+", Timestamp: "+str(current.timestamp)+", WID: "+str(wid)
        text2 = "RiduttoreID: "+str(current.riduttoreid)+", Stazione: "+str(current.stazione)+", Assembly date: "+str(datetime.fromtimestamp(int(current.timestamp)).replace(tzinfo=timezone.utc))
        text3 = "Master: "+str(current.master)+", Rapporto: "+str(current.rapporto)+", Stadi: "+str(current.stadi)+", Cd: "+str(current.cd)
        text4 = "GLOBALS: MinRowsinCsv: "+str(MIN_ORIG_ROWS)+", SigmaMA: "+str_ma+", FlatCurveThreshold: "+str(FLAT_THRESHOLD_PERC*100)+"%, SigmaMF: "+str(SIGMA_MF)+", SigmaCurve: "+str(SIGMA_CURVE)+", MinPointsOut: "+str(MIN_POINTS_PERC*100)+"%"
        return fout, text1, text2, text3, text4
    else:
        header1 = "ComboID,Timestamp,WID,RiduttoreID,Stazione,Assembly_Date,Master,Rapporto,Stadi,Cd"
        values1 = str(current.comboid)+","+str(current.timestamp)+","+str(wid)+","+str(current.riduttoreid)+","+str(current.stazione)+","+str(datetime.fromtimestamp(int(current.timestamp)).replace(tzinfo=timezone.utc))+","+str(current.master)+","+str(current.rapporto)+","+str(current.stadi)+","+str(current.cd)
        header2 = "MinRowsinCsv,SigmaMA,FlatCurveThreshold,SigmaMF,SigmaCurve,MinPointsOut"
        values2 = str(MIN_ORIG_ROWS)+","+str_ma+","+str(FLAT_THRESHOLD_PERC*100)+"%,"+str(SIGMA_MF)+","+str(SIGMA_CURVE)+","+str(MIN_POINTS_PERC)+"%"
        lines = [header1, values1, header2, values2]
        return fout, lines


#Export to csv target curve, boundaries & current curve for visualization:
def curves_to_csv(dbt=None, timestamp=None, current=None, target=None, wid=None):
    close = False
    if not dbt:
        cnxn, cursor = db_connect()
        engine = pd_db_connect()
        dbt = {'cnxn': cnxn, 'cursor': cursor}
        close = True

    if not current:
        current = extract_data(engine, stype='current', timestamp=timestamp)
    if not target:
        target = extract_data(engine, stype='target', comboid=current.comboid)
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
        if len(current.altezza) > 3:
            current.forza = interpolate_curve(target.altezza, current.altezza,current.forza)
    
    #truncate decimals:
    tgt_forza = ["{:.3f}".format(i) for i in target.forza]
    tgt_forza = [float(i[:-2]) for i in tgt_forza]
    cur_forza = ["{:.3f}".format(i) for i in current.forza]
    cur_forza = [float(i[:-2]) for i in cur_forza]

    #generate filename, title and the other captions:
    fout, lines = commons_generator(current, wid, ftype='csv')
    
    #boundaries:
    if target.boundup == [] or target.boundlow == []:
        target.boundup, target.boundlow = get_boundaries(target)

    #dataframe export:
    data = {'Target_Altezza':target.altezza, 'Target_Forza':tgt_forza, 'Upper_Boundary': target.boundup, 
            'Lower_Boundary': target.boundlow, 'Current_Forza':cur_forza}
    df = pd.DataFrame(data)
    df.to_csv(fout) 

    #insert informational text:
    fpath = OUTPUT_PATH+"/curves/"+str(current.comboid)
    prepend_lines(fpath, fout, lines)

    if close:
        db_disconnect(cnxn, cursor)
    return 0


#Export to png target curve, boundaries & current curve for visualization:
def curves_to_png(current, target, wid=0, count_out=0, threshold=0):
    '''
    Visualize the curves plot by saving it as png file.

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
    #title color:
    if wid == 0:
        titcolor = 'green'
    else:
        titcolor = 'firebrick'

    #points out info:
    npoints = len(target.altezza)
    caption0 = "Points out: "+str(count_out)+"/"+str(npoints)+", Threshold: "+str(threshold)

    #generate filename, title and the other captions:
    fout, title, caption1, caption2, caption3 = commons_generator(current, wid, ftype='png')

    #plot:
    fig = plt.figure(figsize=(PNG_SIZE[0]/96, PNG_SIZE[1]/96))
    plt.plot(target.altezza, target.forza, color='limegreen', linewidth=4, label="Ideal curve")
    plt.plot(target.altezza, target.boundup, color='orange', linestyle='--', linewidth=1, label="Upper boundary")
    plt.plot(target.altezza, target.boundlow, color='red', linestyle='--', linewidth=1, label="Lower boundary")
    plt.plot(target.altezza, current.forza, color='blue', linewidth=2, label="CURRENT CURVE")
    xlab = 'Altezza (mm)'
    plt.xlabel(xlab+"\n\n"+caption0+"\n"+caption1+"\n"+caption2+"\n"+caption3)
    plt.ylabel('Forza (kN)')
    plt.legend(fontsize='x-small', frameon=False)
    plt.title(title, fontsize='small', fontweight='bold', color=titcolor)
    plt.tight_layout()
    fig.savefig(fout)
    plt.close(fig)
    return 0


#original png:
def plot_original(timestamp):
    engine = pd_db_connect()

    #extract data:
    current = extract_data(engine, stype='current', timestamp=timestamp)
    target = extract_data(engine, stype='target', comboid=current.comboid)

    #min cut:
    min_ind = 0
    for p in current.altezza:
        if p >= MIN_ALTEZZA:
            min_ind = current.altezza.index(p)
            break
    #max cut:
    max_ind = current.altezza.index(max(current.altezza))
    try:
        cur_altezza = current.altezza[min_ind:(max_ind+2)]
        cur_forza = current.forza[min_ind:(max_ind+2)]
    except:
        cur_altezza = current.altezza[min_ind:(max_ind)]
        cur_forza = current.forza[min_ind:(max_ind)]

    #slice:
    sliced_altezza, sliced_forza = slice_curves(target.altezza, current.altezza, current.forza)

    #interpolate (if possible):
    if len(current.altezza) > 3:
        itp = True
        itp_forza = interpolate_curve(target.altezza, sliced_altezza, sliced_forza)
        fig, axis = plt.subplots(nrows=1, ncols=3, figsize=(1280/96, 576/96))
    else:
        itp = False
        fig, axis = plt.subplots(nrows=1, ncols=2, figsize=(1024/96, 576/96))

    #filename:
    fout = OUTPUT_PATH+"/curves/"+str(current.riduttoreid)+"_"+str(current.timestamp)+"_orig.png"
    title = "ComboID: "+str(current.comboid)+", Timestamp: "+str(current.timestamp)
    caption1 = "RiduttoreID: "+str(current.riduttoreid)+", Stazione: "+str(current.stazione)+", Assembly date: "+str(datetime.fromtimestamp(int(current.timestamp)).replace(tzinfo=timezone.utc))
    caption2 = "Master: "+str(current.master)+", Rapporto: "+str(current.rapporto)+", Stadi: "+str(current.stadi)+", Cd: "+str(current.cd)

    #subplot 1: original curves:
    orig = axis[0]
    orig.plot(cur_altezza, cur_forza, color='darkgoldenrod', linewidth=2)
    orig.set_title("Full original (up to MA)", fontsize='small')
    orig.set(xlabel='Altezza (mm)', ylabel='Forza (kN)')

    #subplot 2: elaborated curves:
    slic = axis[1]
    slic.plot(sliced_altezza, sliced_forza, color='forestgreen', linewidth=2)
    slic.set_title("Sliced", fontsize='small')
    slic.set(xlabel='Altezza (mm)')

    #subplot 3: interpolated (if possible):
    if itp == True:
        itp = axis[2]
        itp.plot(target.altezza, itp_forza, color='dodgerblue', linewidth=2)
        itp.set_title("Interpolated", fontsize='small')
        itp.set(xlabel='Altezza (mm)')
    
    fig.suptitle(title+"\n"+caption1+"\n"+caption2, fontsize='small')

    fig.tight_layout()
    plt.savefig(fout)
    plt.close(fig)
    
    return 0
