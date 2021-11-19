import pandas as pd
import sys
sys.path.insert(0, './')
from globals import *
from utils import interpolate_curve, visualize, write_warning

#EVALUATION TOOLS:
# - evaluate_max()
# - evaluate_curve()
# - evaluate_full()


#Eval max_altezza or max_forza:
def evaluate_max(dbt, riduttore, timestamp, cur, tgt, std, mtype):
    '''
    Function that evaluates if the max_value of either altezza or forza is within the target +- a threshold.
    
    Parameters:
    -------------------
    input:
    - cur, tgt, std (floats) -> current targets for the combo
    - mtype -> must be either 'altezza' or 'forza'
    - sigma value (int) -> will increase the std_dev in the DB (acceptable boundary)
    
    output:
    - wid (warning id) -> if warning found, else 0 (if success) or -1 (if arg error).
    '''
    #arg check: 
    if mtype == 'altezza':
        wid = 1
        sigma = SIGMA_MA
    elif mtype == 'forza':
        wid = 3
        sigma = SIGMA_MF
    else:
        print("ERROR: mtype must by either 'altezza' or 'forza'.")
        raise

    logging = dbt['logging']
    #evaluate current MA/MF if within StdMA/StdMF +- sigma:
    dev = std * sigma
    if (cur >= (tgt - dev)) and (cur <= (tgt + dev)):
        return 0 #ok
    else:
        logging.warning("Timestamp {}: flagged with WID #{}. Max_{} out of acceptable range! Please check the assembly.".format(timestamp, wid, mtype))
        #write warning to DB:
        write_warning(dbt, riduttore, wid, timestamp)
        return wid


#Eval curve (point by point):
def evaluate_curve(dbt, current, target):
    '''
    Function that evaluates if all points of the curve (already interpolated) are within the acceptable std_dev bound 
    from the ideal curve, increased by a sigma.

    Parameters:
    -------------------
    input:
    - cur_forza, tgt_forza, std_curve_avg (list, list, float) -> current targets for the combo
    - sigma value (int) -> will increase the std_dev in the DB (acceptable boundary)
    
    output:
    - count_out (int) -> count of points out of bounds
    - wid (warning id) -> if warning found, else 0.
    '''
    logging = dbt['logging']
    count_out = 0    
    
    #count points out of bounds:
    if USE_AVG == True:
        #use: average deviation:
        dev = target.std_curve_avg * SIGMA_CURVE
        for i in range(len(current.forza)):
            if (current.forza[i] < (target.forza[i] - dev)) or (current.forza[i] > (target.forza[i] + dev)):
                count_out = count_out + 1
    else:
        #use deviation vector:
        for i in range(len(current.forza)):
            if (current.forza[i] < (target.forza[i] - (target.std[i]*SIGMA_CURVE))) or (current.forza[i] > (target.forza[i] + (target.std[i]*SIGMA_CURVE))):
                count_out = count_out + 1

    #final check on curve:
    if count_out <= MIN_POINTS: #ok
        logging.info("Timestamp {}: assembly success. No warnings.".format(current.timestamp))
        return count_out, 0
    else:
        wid = 4
        logging.warning("Timestamp {}: flagged with WID #{}. Curve out of bounds in {} points out of {}! Please check the assembly.".format(current.timestamp, wid, count_out, len(current.forza)))
        #write warning to DB:
        write_warning(dbt, current.riduttoreid, wid, current.timestamp)
    return count_out, wid


#CENTRAL EVALUATE FUNCTION:
def evaluate_full(dbt, current, target, preprocessed=False, visual=WINDOW, save=SAVE_PNG, verbose=False):
    '''
    Function that evaluates if a pressata is correct or not. 
    It queries for the parameters of the pressata's combo, interpolates the curve and 
    then makes 3 checks through the following functions:
    1) evaluate_max, with mtype = 'altezza';
    2) evaluate_max, with mtype = 'forza';
    3) evaluate_curve, which scans the curve point by point;
    
    If one check fails, the function is immediately interrupted: the warning is saved to the DB
    and no further checks are made. A logging message is printed to a log file. (Return: -1)

    If all 3 checks are ok, then the pressata is considered acceptable. (Return: 0)

    Parameters:
    -------------------
    input:
    - timestamp (int) -> current pressata
    - visual (bool) -> calls curve visualization function
    - sigma values (int) for: MA, MF and curve std (will increase the dev in the DB)
    
    output: 
    - 0 if pressata is accepted
    - -1 if warnings found.

    '''
    #sigmas:
    comboid = current.comboid
    timestamp = current.timestamp

    #INTERPOLATE CURVE (overwrite current.forza into collector object):
    current.forza = interpolate_curve(target.altezza, current.altezza, current.forza)

    if preprocessed == False:
        #check 1: max_altezza
        wid = evaluate_max(dbt, current.riduttoreid, current.timestamp, current.ma, target.ma, target.std_ma, mtype='altezza')
        if wid != 0:
            if verbose == True:
                print("Timestamp {}: flagged with WID #{}. Max_altezza out of acceptable range! Please check the assembly.".format(timestamp, wid))
            return -1

    #check 2: max_forza
    wid = evaluate_max(dbt, current.riduttoreid, current.timestamp, current.mf, target.mf, target.std_mf, mtype='forza')
    if wid != 0:
        if verbose == True:
            print("Timestamp {}: flagged with WID #{}. Max_forza out of acceptable range! Please check the assembly.".format(timestamp, wid))
        if (visual == True) or (save == True):
            visualize(current, target, wid=wid, count_out=0, window=visual, save=save)
        return -1
    
    #check 3: compare curve
    count_out, wid = evaluate_curve(dbt, current, target)
    if wid == 0:
        if verbose == True:
            print("Timestamp {}: assembly success. No warnings.".format(current.timestamp))
        if (visual == True) or (save == True):
            visualize(current, target, wid=wid, count_out=count_out, window=visual, save=save)
        return 0
    else:
        if verbose == True:
            print("Timestamp {}: flagged with WID #{}. Curve out of bounds in {} points out of {}! Please check the assembly.".format(current.timestamp, wid, count_out, len(current.forza)))
        if (visual == True) or (save == True):
            visualize(current, target, wid=wid, count_out=count_out, window=visual, save=save)
        return -1
