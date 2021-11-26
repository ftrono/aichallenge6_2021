import pandas as pd
import sys,os
sys.path.insert(0, os.getcwd())
from globals import *
from export.visualize import visualize
from training.training_tools import slice_curves, interpolate_curve

#EVALUATION TOOLS:
# - evaluate_max()
# - evaluate_points()
# - evaluate_full()


#Eval max_altezza or max_forza:
def evaluate_max(log, current, target, mtype):
    '''
    Function that evaluates if the max_value of either altezza or forza is within the target +- a threshold.
    
    Parameters:
    -------------------
    input:
    - dbt (dict) -> dict with cnxn, cursor and logging objects
    - cur, tgt, std (floats) -> current targets for the combo
    - mtype -> must be either 'altezza' or 'forza'
    
    output:
    - wid (warning id) -> if warning found, else 0
    '''
    #arg check: 
    if mtype == 'altezza':
        wid = 1
        sigma = SIGMA_MA
        cur = current.ma
        tgt = target.ma
        std = target.std_ma
    elif mtype == 'forza':
        wid = 3
        sigma = SIGMA_MF
        cur = current.mf
        tgt = target.mf
        std = target.std_mf
    else:
        print("ERROR: mtype must by either 'altezza' or 'forza'.")
        raise

    #evaluate current MA/MF if within StdMA/StdMF +- sigma:
    dev = std * sigma
    if (cur >= (tgt - dev)) and (cur <= (tgt + dev)):
        log.debug("ComboID: {}: Timestamp {}: Max_{} OK".format(target.comboid, current.timestamp, mtype))
        return 0 #ok
    else:
        log.warning("ComboID: {}: Timestamp {}: WID {}. Max_{} out of acceptable range! Current: {}, target: {}, dev: {}. Please check the assembly.".format(target.comboid, current.timestamp, wid, mtype, cur, tgt, dev))
        return wid


#Eval height curve trajectory:
def evaluate_anomalous(log, current, target):
    '''
    Function that evaluates if the max_value of either altezza or forza is within the target +- a threshold.
    
    Parameters:
    -------------------
    input:
    - ...
    
    output:
    - wid (warning id) -> if warning found, else 0
    '''
    #evaluate if height curve starts with an increasing or decreasing trajectory:
    if float(current.altezza[0]) > float(current.altezza[1]):
        wid = 2
        log.warning("ComboID: {}: Timestamp {}: WID {}. Anomalous height curve".format(target.comboid, current.timestamp, wid))
        return wid
    else:
        log.debug("ComboID: {}: Timestamp {}: height curve OK".format(target.comboid, current.timestamp))
        return 0 #ok


#Eval point by point the interpolated curve:
def evaluate_points(log, current, target):
    '''
    Function that evaluates if all points of the curve (already interpolated) are within the acceptable std_dev bound 
    from the ideal curve, increased by a sigma.

    Parameters:
    -------------------
    input:
    - dbt (dict) -> dict with cnxn, cursor and logging objects
    - current -> Collector object with the data for the current Pressata
    - target -> Collector object with the targets for the combo
    
    output:
    - count_out (int) -> count of points out of bounds
    - wid (warning id) -> if warning found, else 0.
    '''
    count_out = 0
    
    #boundaries:
    if USE_AVG == True:
        target.boundup = [(target.forza[i] + (target.std_curve_avg*SIGMA_CURVE)) for i in range(len(target.forza))]
        target.boundlow = [(target.forza[i] - (target.std_curve_avg*SIGMA_CURVE)) for i in range(len(target.forza))]
    else:
        target.boundup = [(target.forza[i] + (target.std[i]*SIGMA_CURVE)) for i in range(len(target.forza))]
        #limit lower boundary:
        #use average stdev as threshold if below zero:
        min_low = -target.std_curve_avg*SIGMA_CURVE
        target.boundlow = []
        for i in range(len(target.forza)):
            p = target.forza[i] - (target.std[i]*SIGMA_CURVE)
            if p >= min_low:
                target.boundlow.append(p)
            else:
                target.boundlow.append(min_low)

    indices = []
    #count points out of bounds:
    for i in range(len(current.forza)):
        if (current.forza[i] < target.boundlow[i]) or (current.forza[i] > target.boundup[i]):
            count_out = count_out + 1
            indices.append(i)

    #final check on curve:
    if count_out <= MIN_POINTS: #ok
        log.debug("ComboID: {}: Timestamp {}: assembly success. No warnings.".format(current.comboid, current.timestamp))
        return count_out, 0
    else:
        wid = 4
        log.warning("ComboID: {}: Timestamp {}: WID #{}. Curve out of bounds in {} points out of {}! Please check the assembly.".format(current.comboid, current.timestamp, wid, count_out, len(current.forza)))
        log.debug(indices)
    return count_out, wid


#CENTRAL EVALUATE FUNCTION:
def evaluate_full(log, current, target, preprocessed=False, visual=WINDOW, save=SAVE_PNG, verbose=False):
    '''
    Function that evaluates if a pressata is correct or not. 
    It queries for the parameters of the pressata's combo, interpolates the curve and 
    then makes 3 checks through the following functions:
    1) evaluate_max, with mtype = 'altezza';
    2) evaluate_max, with mtype = 'forza';
    3) evaluate_points, which scans the curve point by point;
    
    If one check fails, the function is immediately interrupted: the warning is saved to the DB
    and no further checks are made. A logging message is printed to a log file. (Return: -1)

    If all 3 checks are ok, then the pressata is considered acceptable. (Return: 0)

    Parameters:
    -------------------
    input:
    - dbt (dict) -> dict with cnxn, cursor and logging objects
    - current -> Collector object with the data for the current Pressata
    - target -> Collector object with the targets for the combo
    - preprocessed (bool) -> indicates if the evaluation is done in the training context (after preprocessing, so: True) or as standalone full evaluation (so: False)
    - visual (bool) -> call curve visualization function in a window
    - save (bool) -> save curves plot (done by visualization function) as png file
    - verbose (bool) -> prints evaluation output also to stdout
    
    output: 
    - 0 if pressata is accepted
    - wid (int) if warning found

    '''
    #Preprocessing checks:
    if preprocessed == False:
        #check 1: max_altezza
        wid = evaluate_max(log, current, target, mtype='altezza')
        if wid != 0:
            if verbose == True:
                print("ComboID: {}: Timestamp {}: WID {}. Max_altezza out of acceptable range! Current: {}, target: {}, dev: {}. Please check the assembly.".format(target.comboid, current.timestamp, wid, current.ma, target.ma, target.std_ma*SIGMA_MA))
            return wid
        
        #check 2: anomalous height vector
        wid = evaluate_anomalous(log, current, target)
        if wid != 0:
            if verbose == True:
                print("ComboID: {}: Timestamp {}: WID #{}. Anomalous height curve.".format(current.comboid, current.timestamp, wid))
            return wid

        #Check if can go on with evaluating (only if preprocessed == False):
        if target.mf == 0 or target.altezza == []:
            print("ComboID: {}: ERROR: data not available for the Combo.".format(current.comboid))
            return -1

        #Slice curves & interpolate force curve (overwrite current.altezza and current.forza into collector object)
        current.altezza, current.forza = slice_curves(target.altezza, current.altezza, current.forza)
        current.forza = interpolate_curve(target.altezza, current.altezza, current.forza)

    #Always:
    #check 3: max_forza
    wid = evaluate_max(log, current, target, mtype='forza')
    if wid != 0:
        if verbose == True:
            print("ComboID: {}: Timestamp {}: WID {}. Max_forza out of acceptable range! Current: {}, target: {}, dev: {}. Please check the assembly.".format(target.comboid, current.timestamp, wid, current.mf, target.mf, target.std_mf*SIGMA_MF))
        if (visual == True) or (save == True):
            visualize(current, target, wid=wid, count_out=0, window=visual, save=save)
        return wid
    
    #check 4: compare curve
    count_out, wid = evaluate_points(log, current, target)
    if wid == 0:
        if verbose == True:
            log.info("ComboID: {}: Timestamp {}: assembly success. No warnings.".format(current.comboid, current.timestamp))
            print("ComboID: {}: Timestamp {}: assembly success. No warnings.".format(current.comboid, current.timestamp))
        if (visual == True) or (save == True):
            visualize(current, target, wid=wid, count_out=count_out, window=visual, save=save)
        return 0
    else:
        if verbose == True:
            print("ComboID: {}: Timestamp {}: WID #{}. Curve out of bounds in {} points out of {}! Please check the assembly.".format(current.comboid, current.timestamp, wid, count_out, len(current.forza)))
        if (visual == True) or (save == True):
            visualize(current, target, wid=wid, count_out=count_out, window=visual, save=save)
        return wid
