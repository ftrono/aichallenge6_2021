import pandas as pd
import sys,os
sys.path.insert(0, os.getcwd())
from globals import *
from export.curves_plotting import get_boundaries, visualize
from training.training_tools import slice_curves, interpolate_curve

#EVALUATION TOOLS:
# - evaluate_max()
# - evaluate_anomalous()
# - evaluate_points()
# - evaluate_full()


#Eval max_altezza or max_forza:
def evaluate_max(log, current, target, mtype):
    '''
    Function that evaluates if the max_value of either altezza or forza is within the target +- a threshold.
    
    Parameters:
    -------------------
    input:
    - log -> log file used by caller function
    - current (Collector) -> Collector object with the data for the current Pressata
    - target (Collector) -> Collector object with the targets for the Combo
    - mtype (str) -> must be either 'altezza' or 'forza'
    
    output:
    - wid (int) -> warning ID if warning found, else 0
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


#Eval height curve trajectory and/or slice length:
def evaluate_anomalous(log, current, target, trajectory=False, sliced=False):
    '''
    Function that evaluates the original altezza curve of a Pressata, making either one of 2 checks:
    a) if the altezza curve of a Pressata starts with an increasing or decreasing trend (it actually should be increasing);
    b) (if the curve has been sliced) the length of the kept portion of the sliced altezza curve (if the curve is too short, it was anomalous)

    Both cases trigger a WID 2 - anomalous height curve.
    
    Parameters:
    -------------------
    input:
    - log -> log file used by caller function
    - current (Collector) -> Collector object with the data for the current Pressata
    - target (Collector) -> Collector object with the targets for the Combo
    - trajectory (boolean) -> triggers check a
    - sliced_len (boolean) -> triggers check b
    
    output:
    - wid (int) -> warning ID if warning found, else 0
    '''
    wid = 0

    #check a) trajectory:
    if (trajectory == True) and (float(current.altezza[0]) > float(current.altezza[1])):
        wid = 2

    #check b) length of sliced vector:  
    if (sliced == True) and (len(current.altezza) <= 3):
        wid = 2

    #log:
    if wid != 0:
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
    - log -> log file used by caller function
    - current (Collector) -> Collector object with the data for the current Pressata
    - target (Collector) -> Collector object with the targets for the Combo
    
    output:
    - count_out (int) -> count of points out of bounds
    - threshold (int) -> max number of points out allowed
    - wid (int) -> warning ID if warning found, else 0
    '''
    count_out = 0
    indices = []

    #boundaries:
    target.boundup, target.boundlow = get_boundaries(target)
    
    #count points out of bounds:
    for i in range(len(current.forza)):
        if (current.forza[i] < target.boundlow[i]) or (current.forza[i] > target.boundup[i]):
            count_out = count_out + 1
            indices.append(i)

    #final check on curve:
    threshold= int(len(current.forza)*MIN_POINTS_PERC)
    if count_out <= threshold: #ok
        log.debug("ComboID: {}: Timestamp {}: assembly success. No warnings.".format(current.comboid, current.timestamp))
        return count_out, threshold, 0
    else:
        wid = 4
        log.warning("ComboID: {}: Timestamp {}: WID #{}. Curve out of bounds in {} points out of {}, threshold is {}! Please check the assembly.".format(current.comboid, current.timestamp, wid, count_out, len(current.forza), threshold))
    return count_out, threshold, wid


#CENTRAL EVALUATE FUNCTION:
def evaluate_full(log, current, target, preprocessed=False, visual=WINDOW, save=SAVE_PNG, verbose=False):
    '''
    Function that evaluates if a pressata is correct or not. 
    It queries for the parameters of the pressata's combo, interpolates the curve and 
    then makes 4 checks through the following functions:
    1) evaluate_max, with mtype = 'altezza';
    2) evaluate_anomalous, which evaluates if the altezza curve is anomalous (decreasing trajectory or caused excessive slicing);
    2) evaluate_max, with mtype = 'forza';
    3) evaluate_points, which scans the curve point by point;
    
    If one check fails, the function is immediately interrupted: the warning is returned
    and no further checks are made. A logging message is printed to a log file.

    If all checks are ok, then the pressata is considered acceptable.

    Parameters:
    -------------------
    input:
    - log -> log file used by caller function
    - current (Collector) -> Collector object with the data for the current Pressata
    - target (Collector) -> Collector object with the targets for the Combo
    - preprocessed (bool) -> indicates if the evaluation is done in the training context (after preprocessing, so: True) or as standalone full evaluation (so: False)
    - visual (bool) -> call curve visualization function in a window
    - save (bool) -> save curves plot (done by visualization function) as png file
    - verbose (bool) -> prints evaluation output also if ok and to stdout
    
    output:
    - wid (int) -> warning ID if warning found, else 0

    '''
    #Preprocessing checks:
    if preprocessed == False:
        #check 1: max_altezza
        if CHECK_MA == True:
            wid = evaluate_max(log, current, target, mtype='altezza')
            if wid != 0:
                if verbose == True:
                    print("ComboID: {}: Timestamp {}: WID {}. Max_altezza out of acceptable range! Current: {}, target: {}, dev: {}. Please check the assembly.".format(target.comboid, current.timestamp, wid, current.ma, target.ma, target.std_ma*SIGMA_MA))
                return wid

        #check 2: anomalous height vector: trajectory check
        wid = evaluate_anomalous(log, current, target, trajectory=True)
        if wid != 0:
            if verbose == True:
                print("ComboID: {}: Timestamp {}: WID #{}. Anomalous height curve.".format(current.comboid, current.timestamp, wid))
            return wid
        
        #Check if can go on with evaluating (only if preprocessed == False):
        if target.mf == 0 or target.altezza == []:
            print("ComboID: {}: ERROR: data not available for the Combo.".format(current.comboid))
            return -1

        #Slice curves (overwrite current.altezza and current.forza into collector object)
        current.altezza, current.forza = slice_curves(target.altezza, current.altezza, current.forza)

        #check 3: anomalous height vector: sliced check
        wid = evaluate_anomalous(log, current, target, sliced=True)
        if wid != 0:
            if verbose == True:
                print("ComboID: {}: Timestamp {}: WID #{}. Anomalous height curve.".format(current.comboid, current.timestamp, wid))
            return wid

        #Interpolate force curve (overwrite current.altezza and current.forza into collector object)
        current.forza = interpolate_curve(target.altezza, current.altezza, current.forza)

    #Always:
    #check 4: max_forza
    if CHECK_MF == True:
        wid = evaluate_max(log, current, target, mtype='forza')
        if wid != 0:
            if verbose == True:
                print("ComboID: {}: Timestamp {}: WID {}. Max_forza out of acceptable range! Current: {}, target: {}, dev: {}. Please check the assembly.".format(target.comboid, current.timestamp, wid, current.mf, target.mf, target.std_mf*SIGMA_MF))
            return wid
    
    #check 5: curve points
    count_out, threshold, wid = evaluate_points(log, current, target)
    if wid == 0:
        if verbose == True:
            log.info("ComboID: {}: Timestamp {}: assembly success. No warnings.".format(current.comboid, current.timestamp))
            print("ComboID: {}: Timestamp {}: assembly success. No warnings.".format(current.comboid, current.timestamp))
        if (visual == True) or (save == True):
            visualize(current, target, wid=wid, count_out=count_out, threshold=threshold, window=visual, save=save)
        return 0
    else:
        if verbose == True:
            print("ComboID: {}: Timestamp {}: WID #{}. Curve out of bounds in {} points out of {}, threshold is {}! Please check the assembly.".format(current.comboid, current.timestamp, wid, count_out, len(current.forza), threshold))
        if (visual == True) or (save == True):
            visualize(current, target, wid=wid, count_out=count_out, threshold=threshold, window=visual, save=save)
        return wid
