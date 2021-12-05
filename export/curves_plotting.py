import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys, os
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.extract_data import extract_data 
from database_functions.db_connect import db_connect, db_disconnect
from training.training_tools import slice_curves, interpolate_curve, get_boundaries

#CURVES PLOTTING:
# - commons_generator()
# - prepend_lines()
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
    #informational text:
    if ftype == 'png':
        text1 = "ComboID: "+str(current.comboid)+", Timestamp: "+str(current.timestamp)+", WID: "+str(wid)
        text2 = "RiduttoreID: "+str(current.riduttoreid)+", Stazione: "+str(current.stazione)+", Assembly date: "+str(datetime.fromtimestamp(int(current.timestamp)))
        text3 = "Master: "+str(current.master)+", Rapporto: "+str(current.rapporto)+", Stadi: "+str(current.stadi)+", Cd: "+str(current.cd)
        return fout, text1, text2, text3
    else:
        header = "ComboID,Timestamp,WID,RiduttoreID,Stazione,Assembly_Date,Master,Rapporto,Stadi,Cd"
        values = str(current.comboid)+","+str(current.timestamp)+","+str(wid)+","+str(current.riduttoreid)+","+str(current.stazione)+","+str(datetime.fromtimestamp(int(current.timestamp)))+","+str(current.master)+","+str(current.rapporto)+","+str(current.stadi)+","+str(current.cd)
        return fout, header, values


#prepend informational lines to csv:
def prepend_lines(fout, temp, lines):
    '''
    Insert informational lines at the beginning of a csv file.
    Input:
    - fout (str) -> full filename of original csv
    - temp (str) -> full filename of temporary csv to use
    - lines (list) -> list of string lines to prepend.
    '''
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


#Export to csv target curve, boundaries & current curve for visualization:
def curves_to_csv(dbt=None, timestamp=None, current=None, target=None, wid=None):
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
        if len(current.altezza) > 3:
            current.forza = interpolate_curve(target.altezza, current.altezza,current.forza)

    #generate filename, title and the other captions:
    fout, header, values = commons_generator(current, wid, ftype='csv')
    lines = [header, values]

    #temp file:
    fpath = OUTPUT_PATH+"/curves/"+str(current.comboid)
    temp = fpath+"/temp.csv"
    
    #boundaries:
    if target.boundup == [] or target.boundlow == []:
        target.boundup, target.boundlow = get_boundaries(target)

    #dataframe export:
    data = {'Target_Altezza':target.altezza, 'Target_Forza':target.forza, 'Upper_Boundary': target.boundup, 
            'Lower_Boundary': target.boundlow, 'Current_Forza':current.forza}
    df = pd.DataFrame(data)
    df.to_csv(fout) 

    #insert informational text:
    prepend_lines(fout, temp, lines)

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
    fout, title, caption1, caption2 = commons_generator(current, wid, ftype='png')

    #plot:
    fig = plt.figure(figsize=(PNG_SIZE[0]/96, PNG_SIZE[1]/96))
    plt.plot(target.altezza, target.forza, color='limegreen', linewidth=4, label="Ideal curve")
    plt.plot(target.altezza, target.boundup, color='orange', linestyle='--', linewidth=1, label="Upper boundary")
    plt.plot(target.altezza, target.boundlow, color='red', linestyle='--', linewidth=1, label="Lower boundary")
    plt.plot(target.altezza, current.forza, color='blue', linewidth=2, label="CURRENT CURVE")
    xlab = 'Altezza (mm)'
    plt.xlabel(xlab+"\n\n"+caption0+"\n"+caption1+"\n"+caption2)
    plt.ylabel('Forza (kN)')
    plt.legend(fontsize='x-small', frameon=False)
    plt.title(title, fontsize='small', fontweight='bold', color=titcolor)
    plt.tight_layout()
    fig.savefig(fout)
    plt.close(fig)
    return 0


#original png:
def plot_original(timestamp):
    cnxn, cursor = db_connect()
    dbt = {'cnxn': cnxn, 'cursor': cursor}

    #extract data:
    current = extract_data(dbt, stype='current', timestamp=timestamp)
    target = extract_data(dbt, stype='target', comboid=current.comboid)

    #min cut:
    min_ind = 0
    for p in current.altezza:
        if p >= MIN_ALTEZZA:
            min_ind = current.altezza.index(p)
    #max cut:
    max_ind = current.forza.index(max(current.forza))
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
    caption1 = "RiduttoreID: "+str(current.riduttoreid)+", Stazione: "+str(current.stazione)+", Assembly date: "+str(datetime.fromtimestamp(int(current.timestamp)))
    caption2 = "Master: "+str(current.master)+", Rapporto: "+str(current.rapporto)+", Stadi: "+str(current.stadi)+", Cd: "+str(current.cd)

    #subplot 1: original curves:
    orig = axis[0]
    orig.plot(cur_altezza, cur_forza, color='darkgoldenrod', linewidth=2)
    orig.set_title("Full original (up to MF)", fontsize='small')
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

    db_disconnect(cnxn, cursor)
    return 0
