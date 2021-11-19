import sys, statistics,os
sys.path.insert(0, os.getcwd())
#sys.path.insert(0, './')
from globals import *
import numpy as np

#TRAINING TOOLS:
# - set_target_max()
# - (helper) compute_rate()
# - (helper) ideal_curve()
# - (helper) stdev_curve()


#set target MA/MF & its std within combo:
def set_target_max(dbt, mtype):
    '''
    Train MA/MF and StdMA/MF for a Combo.
    1. Retrieves target value of Altezza (or Forza) and the Stdev of MA (or MF) for each ComboID (FROM: table Pressate)
    2. Saves the values as TargetMA (or TargetMF) and StdMA (or StdMF) for the correspondent ComboID (TO: table Combos)

    Parameters:
    -------------------
    input:
    - dbt (dict) -> dict with cnxn, cursor and logging objects
    - mtype (str) -> must be either 'altezza' or 'forza'
    '''
    #arg check: 
    if mtype == 'altezza':
        mt = 'MAX(Pressate.MaxAltezza)'
        st = 'STDEV(Pressate.MaxAltezza)'
        v = 'A'
    elif mtype == 'forza':
        mt = 'AVG(Pressate.MaxForza)'
        st = 'STDEV(Pressate.MaxForza)'
        v = 'F'
    else:
        print("ERROR: mtype must by either 'altezza' or 'forza'.")
        raise

    # Extract info for Pressate
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logging = dbt['logging']
    cursor.execute("SELECT Pressate.ComboID, "+mt+", "+st+" FROM Pressate WHERE NOT EXISTS (SELECT Warnings.Timestamp FROM Warnings WHERE Warnings.Timestamp = Pressate.Timestamp) GROUP BY ComboID")
    list = cursor.fetchall()
    # Update Combos values to TargetMA/MF and StdMA/MF
    for (comboID, max_v, std_v) in list:
        # updates values (decimal.Decimal -> float)
        if (std_v == None) or (float(std_v) < 1):
            std_v=1
        cursor.execute("UPDATE Combos SET TargetM"+v+" = ?, StdM"+v+" = ? WHERE ComboID = ?", float(max_v), float(std_v), comboID)
        logging.debug("Setting TargetM{} and StdM{} for ComboID = {}".format(v, v, comboID))
    cursor.commit()
    return 0


#helper: compute sample_rate for a pressata (for height vector):
def compute_rate(orig_altezza):
    '''
    Helper function: computes the sample rate for a Pressata for target height vector calculation.

    input:
    - orig_altezza (list) for a Pressata
    
    returns:
    - sample_rate (float)
    '''
    #get vector of differences:
    diff_vector=np.diff(orig_altezza)
    diff_vector=np.absolute(diff_vector)
    diff_vector=np.round(diff_vector,2)
    #compute max freq:
    unique, counts = np.unique(diff_vector, return_counts=True)
    max_index_col = np.argmax(counts, axis=0) #max freq
    sample_rate = unique[max_index_col]
    return sample_rate


#helper: calculate curve of means:
def ideal_curve(batch_forces):
    '''
    Function to compute the ideal curve for a specific combination given by 
    the mean value between its points on the x-axis 

    Parameters
    batch_forces : list of lists
        It's the collection of already interpolated series of which we want to 
        compute the ideal force curve. That said it is critical that each series 
        should be of the same size!

    Returns
    out_curve : list
        A list contining the average value of each point in all the series, 
        its lenght is the same as the one of every series

    '''
    out_curve = []
    #first cycle for a number of times equal to the number of point of each 
    #series of pressate
    for i in range(0,len(batch_forces[0])):
        temp = []
        #then cycle for the number of pressate to be taken into consideration
        for j in range(0, len(batch_forces)):
            #in this temporary list we collect all of the pressate values of
            #the same point in time
            temp.append(batch_forces[j][i])
        #of this list we compute the average and append it to the final list
        avg = statistics.mean(temp)
        out_curve.append(avg)
        #then we repeat the cycle for another set of pressate in the following
        #point in time
    return out_curve


#helper: calculate stdev of force curve:
def stdev_curve(batch_forces):
    '''
    Function to compute the average std_dev to be used as threshold 
    when looking if a new sample will be in or out the ideal curve boundaries

    Parameters
    ----------
    batch_forces : list of lists
        It's the collection of already interpolated series of which we want to 
        compute the ideal behaviour. That said it is critical that each series 
        should be of the same size!

    Returns
    -------
    std_list : list
       Vector with the std_dev for all points in the series.

    '''
    stdev_list = []
    #we cycle for a number of times equal to the number of points of each series of pressate
    for i in range(0,len(batch_forces[0])):
        temp = []
        #then we cycle for the number of pressate to be taken into consideration
        for j in range(0, len(batch_forces)):
            #in this temporary list we collect all the pressate values of
            #the same point in time
            temp.append(batch_forces[j][i])
        #of this list we compute the standard deviation and append it to a list
        stdev = statistics.stdev(temp)
        stdev_list.append(stdev)
    return stdev_list
