import pandas as pd
import sys
sys.path.insert(0, './')
from utils import interpolate_curve, visualize, write_warning

#EVALUATION TOOLS:
# - evaluate_max()
# - evaluate_curve()
# - evaluate_full()


#Eval max_altezza or max_forza:
def evaluate_max(dbt, riduttore, timestamp, cur, tgt, std, mtype, sigma=1):
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
    elif mtype == 'forza':
        wid = 3
    else:
        print("ERROR: mtype must by either 'altezza' or 'forza'.")
        return -1

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
def evaluate_curve(dbt, current, target, sigma=1):
    '''
    Function that evaluates if all points of the curve (already interpolated) are within the acceptable std_dev bound 
    from the ideal curve, increased by a sigma.

    Parameters:
    -------------------
    input:
    - cur_forza, tgt_forza, std_curve (list, list, float) -> current targets for the combo
    - sigma value (int) -> will increase the std_dev in the DB (acceptable boundary)
    
    output:
    - count_out (int) -> count of points out of bounds
    - wid (warning id) -> if warning found, else 0.
    '''
    logging = dbt['logging']
    count_out = 0
    dev = target.std_curve * sigma
    
    #count points out of bounds:
    for i in range(len(current.forza)):
        if (current.forza[i] < (target.forza[i] - dev)) or (current.forza[i] > (target.forza[i] + dev)):
            count_out = count_out + 1

    #final check on curve:
    if count_out == 0: #ok
        logging.info("Timestamp {}: assembly success. No warnings.".format(current.timestamp))
        return 0
    else:
        wid = 4
        logging.warning("Timestamp {}: flagged with WID #{}. Curve out of bounds in {} points out of {}! Please check the assembly.".format(current.timestamp, wid, count_out, len(current.forza)))
        #write warning to DB:
        write_warning(dbt, current.riduttoreid, wid, current.timestamp)
    return count_out


#CENTRAL EVALUATE FUNCTION:
def evaluate_full(dbt, current, target, sigmas, visual=False, preprocessed=False):
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
    sigma_ma = sigmas['sigma_ma']
    sigma_mf = sigmas['sigma_mf']
    sigma_curve = sigmas['sigma_curve']

    #INTERPOLATE CURVE (overwrite current.forza into collector object):
    current.forza = interpolate_curve(target.altezza, current.altezza, current.forza)

    if preprocessed == False:
        #check 1: max_altezza
        wid = evaluate_max(dbt, current.riduttoreid, current.timestamp, current.ma, target.ma, target.std_ma, mtype='altezza', sigma=sigma_ma)
        if visual:
            visualize(target.forza, target.std_curve, target.altezza, current.forza)
        if wid != 0:
            return -1

    #check 2: max_forza
    wid = evaluate_max(dbt, current.riduttoreid, current.timestamp, current.mf, target.mf, target.std_mf, mtype='forza', sigma=sigma_mf)
    if visual:
        visualize(target.forza, target.std_curve, target.altezza, current.forza)
    if wid != 0:
        return -1
    
    #check 3: compare curve
    count_out = evaluate_curve(current.forza, target.forza, target.std_curve, sigma=sigma_curve)
    if visual:
        visualize(target.forza, target.std_curve, target.altezza, current.forza)
    if count_out == 0:
        return 0
    else:
        return -1
