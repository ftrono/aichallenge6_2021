import sys, statistics,os
sys.path.insert(0, os.getcwd())
#sys.path.insert(0, './')
from globals import *
import numpy as np
from scipy import interpolate

#TRAINING TOOLS:
# - compute_rate()
# - generate_hvec()
# - slice_curves()
# - interpolate_curve()
# - ideal_curve()
# - stdev_curve()
# - get_boundaries()


#compute sample_rate for a pressata (for height vector):
def compute_rate(batch_altezze):
    '''
    Compute the sample rate for target height vector calculation from a batch of Pressate.

    input:
    - batch_altezze (list of lists) -> list of original altezze vectors for a Combo
    
    returns:
    - sample_rate (float) -> target sample rate for the target altezza vector for the Combo.
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
    - tgt_rate (float) -> target sample rate calculated for the Combo (from the compute_rate() function)
    - min_h (float) -> ninimum height value from which to cut the beginning of the height vector
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


#slice the portions of interest of curves:
def slice_curves(altezza_combo, altezza, forza):
    '''
    Function that slices the portions of original altezza and forza curves of a Pressata,
    keeping only the points (from both curves) in which Altezza is monotonically increasing.

    The function removes the parts related to where Altezza is decreasing or is back at some levels already covered,
    in order to remove duplicate values to allow interpolation.

    Parameters:
    -------------------
    input:
    - altezza_combo (list) -> target height vector for the Combo
    - altezza (list) -> original altezza vector for a Pressata
    - forza (list) -> original forza vector for a Pressata

    returns:
    - altezza_corr (list) -> sliced and monotonically increasing portion of the original Altezza curve for the Pressata
    - forza_corr (list) -> sliced portion of the original Forza curve for the Pressata, corresponding to the kept portions 
    of the altezza vector.
    '''
    #vars:
    target_ma = max(altezza_combo)
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
        if forza[ind] >= 0:
            forza_corr.append(forza[ind])
        else:
            forza_corr.append(0)
    return altezza_corr, forza_corr


#interpolate curve:
def interpolate_curve(altezza_combo, altezza, forza):
    '''
    Function that interpolates the sliced forza vector of a Pressata, on the basis of its sliced altezza vector
    and the target altezza vector for the Combo.

    Parameters:
    -------------------
    input:
    - altezza_combo (list) -> target height vector for the Combo
    - altezza (list) -> original altezza vector for a Pressata
    - forza (list) -> original forza vector for a Pressata

    returns:
    - new_forza (list) -> interpolated forza vector for the Pressata.
    '''
    #vars:
    max_f = max(forza)
    new_forza = []

    #filling:
    f = interpolate.interp1d(altezza, forza, kind='linear', fill_value='extrapolate')

    #interpolate & pad:
    for point in altezza_combo:
        if (point < altezza[0]) or (point > altezza[-1]):
            new_forza.append(0)
        else:
            itp = max(0, round(float(f(point)),2))
            new_forza.append(min(itp, max_f))
    
    return new_forza


#calculate curve of means:
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


#calculate stdev of force curve:
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
    #upper boundary:
    boundup = [(target.forza[i] + (target.std[i]*SIGMA_CURVE)) for i in range(len(target.forza))]
    #limit lower boundary:
    boundlow = []
    for i in range(len(target.forza)):
        p = target.forza[i] - (target.std[i]*SIGMA_CURVE)
        if p >= 0:
            boundlow.append(p)
        else:
            boundlow.append(0)
    return boundup, boundlow
