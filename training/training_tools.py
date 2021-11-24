import sys, statistics,os
sys.path.insert(0, os.getcwd())
#sys.path.insert(0, './')
from globals import *
import numpy as np
from scipy import interpolate

#TRAINING TOOLS:
# - set_target_max()
# - (helper) compute_rate()
# - (helper) ideal_curve()
# - (helper) stdev_curve()


#helper: compute sample_rate for a pressata (for height vector):
def compute_rate(batch_altezze):
    '''
    Helper function: computes the sample rate for a Pressata for target height vector calculation.

    input:
    - orig_altezza (list) for a Pressata
    
    returns:
    - sample_rate (float)
    '''
    rates = []

    #get sample rate of each Pressata in the batch:
    for ls in batch_altezze:
        #get vector of differences:
        diff_vector=np.diff(ls)
        diff_vector=np.absolute(diff_vector)
        diff_vector=np.round(diff_vector,2)
        #compute max freq:
        unique, counts = np.unique(diff_vector, return_counts=True)
        max_index_col = np.argmax(counts, axis=0) #max freq
        rates.append(unique[max_index_col])

    #get overall target sample rate (the max frequent):
    unique, counts = np.unique(rates, return_counts=True)
    max_index_col = np.argmax(counts, axis=0)
    sample_rate = unique[max_index_col]

    return sample_rate


#generate target height vector for a comboid:
def generate_hvec(tgt_rate, min_h, target_ma):
    '''
    Generate target height vector for a Combo.

    Parameters:
    -------------------
    input:
    - dbt (dict) -> dict with cnxn, cursor and logging objects
    - timestamps (list) -> list of timestamps to analyze
    - target_ma (float) -> TargetMA for the Combo.

    returns:
    - altezza_combo (list) -> target height vector for the Combo.
    '''

    #tgt_rate correction (to allow integer division):
    rangelen = int((target_ma-min_h) // tgt_rate)
    tgt_rate = (target_ma-min_h) / rangelen
    altezza_combo = []

    #4) compute target h vector:
    for i in range(rangelen+1):
        altezza_combo.append(round(min_h + (i*tgt_rate),2))
    return altezza_combo


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


#slice the portions of interest of curves:
def slice_curves(target_ma, altezza, forza):
    #vars:
    indices = []
    altezza_corr = []
    forza_corr = []
    max_p = 0

    #get indices of points of altezza curve in which it grows monotonically:
    for p in altezza[1:]:
        if p >= MIN_ALTEZZA and p <= target_ma:
            if p > (p-1) and p > max_p:
                max_p = p
                indices.append(altezza.index(p))

    #use the extracted indices to get a corrected version of the Pressata's altezza and forza curves:
    for ind in indices:
        altezza_corr.append(altezza[ind])
        forza_corr.append(forza[ind])

    return altezza_corr, forza_corr


#interpolate curve:
def interpolate_curve(altezza_combo, altezza, forza):
    def f(x):
        x_points = altezza
        y_points = forza

        tck = interpolate.splrep(x_points, y_points)
        return interpolate.splev(x, tck)
    
    new_forza=[]
    for point in altezza_combo:
        if point<altezza[0]:
            new_forza.append(0)
        else:
            new_forza.append(round(float(f(point)),2))
    return new_forza
