import sys, os
sys.path.insert(0, os.getcwd())
from globals import *
from export.curves_plotting import get_boundaries, curves_to_png
from training.training_tools import slice_curves, interpolate_curve

#EVALUATION TOOLS:
# - evaluate_ma()
# - evaluate_mf()
# - evaluate_anomalous()
# - evaluate_points()
# - evaluate_full()


#Eval max_altezza (WID 1):
def evaluate_ma(log, current, target):
    '''
    Function that evaluates if the max_value of altezza is within the target +- a threshold (WID 1).
    
    Parameters:
    -------------------
    input:
    - log -> log file used by caller function
    - current (Collector) -> Collector object with the data for the current Pressata
    - target (Collector) -> Collector object with the targets for the Combo
    
    output:
    - wid (int) -> warning ID if warning found, else 0
    - message (str) -> log warning string (for verbose print)
    '''
    #a) check if current pressata reaches the minimum cutoff MIN_ALTEZZA:
    if current.ma <= MIN_ALTEZZA:
        wid = 1
        message = "ComboID: {}: Timestamp {}: WID {}. MaxAltezza below cutoff point! Current: {}, cutoff: {}. Please check the assembly.".format(target.comboid, current.timestamp, wid, current.ma, MIN_ALTEZZA)
        log.warning(message)
        return wid, message

    #b) (if enabled) evaluate current MA if within StdMA +- sigma:
    if CHECK_MA == True:
        cur = "{:.3f}".format(current.ma)
        cur = float(cur[:-2])
        tgt = "{:.3f}".format(target.ma)
        tgt = float(tgt[:-2])
        dev = target.std_ma * SIGMA_MA
        dev = "{:.3f}".format(dev)
        dev = float(dev[:-2])
        if (cur >= (tgt - dev)) and (cur <= (tgt + dev)):
            log.debug("ComboID: {}: Timestamp {}: MaxAltezza OK".format(target.comboid, current.timestamp))
            return 0, 0 #ok
        else:
            wid = 1
            message = "ComboID: {}: Timestamp {}: WID {}. MaxAltezza out of acceptable range! Current: {}, target: {}, dev: {}. Please check the assembly.".format(target.comboid, current.timestamp, wid, cur, tgt, dev)
            log.warning(message)
            return wid, message
    else:
        return 0, 0 #ok


#Eval max_forza (WID 3):
def evaluate_mf(log, current, target):
    '''
    Function that evaluates if the max_value of forza is within the target +- a threshold (WID 3).
    
    Parameters:
    -------------------
    input:
    - log -> log file used by caller function
    - current (Collector) -> Collector object with the data for the current Pressata
    - target (Collector) -> Collector object with the targets for the Combo
    
    output:
    - wid (int) -> warning ID if warning found, else 0
    - message (str) -> log warning string (for verbose print)
    '''
    #a) check flat curve:
    cur = "{:.3f}".format(current.mf)
    cur = float(cur[:-2])
    tgt = "{:.3f}".format(target.mf)
    tgt = float(tgt[:-2])
    threshold = target.mf * FLAT_THRESHOLD_PERC
    threshold = "{:.3f}".format(threshold)
    threshold = float(threshold[:-2])
    if cur < threshold:
        wid = 3
        message = "ComboID: {}: Timestamp {}: WID {}. Flat curve: Max_forza below threshold! Current: {}, target: {}, threshold: {}. Please check the assembly.".format(target.comboid, current.timestamp, wid, cur, tgt, threshold)
        log.warning(message)
        return wid, message

    #b) evaluate current MF if within StdMF +- sigma:
    dev = target.std_mf * SIGMA_MF
    dev = "{:.3f}".format(dev)
    dev = float(dev[:-2])
    if (cur >= (tgt - dev)) and (cur <= (tgt + dev)):
        log.debug("ComboID: {}: Timestamp {}: MaxForza OK".format(target.comboid, current.timestamp))
        return 0, 0 #ok
    else:
        wid = 3
        message = "ComboID: {}: Timestamp {}: WID {}. MaxForza out of acceptable range! Current: {}, target: {}, dev: {}. Please check the assembly.".format(target.comboid, current.timestamp, wid, cur, tgt, dev)
        log.warning(message)
        return wid, message


#Eval height curve trajectory and/or slice length (WID 2):
def evaluate_anomalous(log, current, target, trajectory=False, sliced=False):
    '''
    Function that evaluates the original altezza curve of a Pressata, making either one of 2 checks:
    a) if the original altezza curve of a Pressata starts with an increasing or decreasing trend (it actually should be increasing) or is shorter than a minimum number of csv rows (MIN_ORIG_ROWS);
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
    if (trajectory == True):
        if (len(current.altezza) <= MIN_ORIG_ROWS):
            wid = 2
        elif (float(current.altezza[0]) > float(current.altezza[1])):
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


#Eval point by point the interpolated curve (WID 4):
def evaluate_points(log, current, target):
    '''
    Function that evaluates if all points of the curve (already interpolated) are within the acceptable std_dev bound 
    from the ideal curve, increased by a sigma. (WID 4)

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
    cur_forza = ["{:.3f}".format(i) for i in current.forza]
    cur_forza = [float(i[:-2]) for i in cur_forza]
    for i in range(len(cur_forza)):
        if (cur_forza[i] < target.boundlow[i]) or (cur_forza[i] > target.boundup[i]):
            count_out = count_out + 1
            indices.append(i)
    #print(indices)
    #final check on curve:
    threshold = int(len(current.forza)*MIN_POINTS_PERC)
    if count_out <= threshold: #ok
        log.debug("ComboID: {}: Timestamp {}: assembly success. No warnings.".format(current.comboid, current.timestamp))
        return count_out, threshold, 0
    else:
        wid = 4
        log.warning("ComboID: {}: Timestamp {}: WID #{}. Curve out of bounds in {} points out of {}, threshold is {}! Please check the assembly.".format(current.comboid, current.timestamp, wid, count_out, len(current.forza), threshold))
    return count_out, threshold, wid


#CENTRAL EVALUATE FUNCTION:
def evaluate_full(log, current, target, preprocessed=False, save=SAVE_PNG, verbose=False):
    '''
    Function that evaluates if a pressata is correct or not. 
    It queries for the parameters of the pressata's combo, interpolates the curve and 
    then makes a series of checks through the following functions:
    1) evaluate_ma (cutoff point and, if enabled, vs TargetMA);
    2) evaluate_anomalous, which evaluates if the altezza curve is anomalous (decreasing trajectory or caused excessive slicing);
    2) evaluate_mf;
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
    - save (bool) -> save curves plot (done by visualization function) as png file
    - verbose (bool) -> prints evaluation output also if ok and to stdout
    
    output:
    - wid (int) -> warning ID if warning found, else 0

    '''
    #Preprocessing checks:
    if preprocessed == False:
        #check 1: max_altezza (will check for cutoff point and, only if enabled, for CHECK_MA):
        wid, message = evaluate_ma(log, current, target)
        if wid != 0:
            if verbose == True:
                print(message)
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
    wid, message = evaluate_mf(log, current, target)
    if wid != 0:
        if verbose == True:
            print(message)
        return wid
    
    #check 5: curve points
    count_out, threshold, wid = evaluate_points(log, current, target)
    if wid == 0:
        if verbose == True:
            log.info("ComboID: {}: Timestamp {}: assembly success. No warnings.".format(current.comboid, current.timestamp))
            print("ComboID: {}: Timestamp {}: assembly success. No warnings.".format(current.comboid, current.timestamp))
        if save == True:
            curves_to_png(current, target, wid=wid, count_out=count_out, threshold=threshold)
        return 0
    else:
        if verbose == True:
            print("ComboID: {}: Timestamp {}: WID #{}. Curve out of bounds in {} points out of {}, threshold is {}! Please check the assembly.".format(current.comboid, current.timestamp, wid, count_out, len(current.forza), threshold))
        if save == True:
            curves_to_png(current, target, wid=wid, count_out=count_out, threshold=threshold)
        return wid
