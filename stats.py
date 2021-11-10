import statistics
import warnings
from main.utils import interpolate_curve


#STATISTICAL ANALYSIS & TRAINING FUNCTIONS:

#BS1: curve of means:
def ideal_curve(in_curves):
    '''
    Function to compute the ideal curve for a specific combination given by 
    the mean value between its points on the x-axis 

    Parameters
    in_curves : list of lists
        It's the collection of already interpolated series of which we want to 
        compute the ideal force curve. That said it is critical that each series 
        should be of the same size!

    Returns
    out_curve : list
        A list contining the average value of each point in all the series, 
        it's lenght is the same as the one of every series

    '''
    out_curve = []
    #first cycle for a number of times equal to the number of point of each 
    #series of pressate
    for i in range(0,len(in_curves[0])):
        temp = []
        #then cycle for the number of pressate to be taken into consideration
        for j in range(0, len(in_curves)):
            #in this temporary list we collect all of the pressate values of
            #the same point in time
            temp.append(in_curves[j][i])
        #of this list we compute the average and append it to the final list
        avg = statistics.mean(temp)
        out_curve.append(avg)
        #then we repeat the cycle for another set of pressate in the following
        #point in time
    return out_curve


#BS2: stdev of force curve:
def stdev_curve(in_curves, sigma=1):
    '''
    Function to compute the average std_dev to be used as threshold 
    when looking if a new sample will be in or out the ideal curve boundaries

    Parameters
    ----------
    in_curves : list of lists
        It's the collection of already interpolated series of which we want to 
        compute the ideal behaviour. That said it is critical that each series 
        should be of the same size!
    sigma : int 
        Multiplier to increase std_curve range (default: 1)

    Returns
    -------
    std_curve : double
       The value of the average std_devs of all points in the series.

    '''
    stdev_list = []
    #we cycle for a number of times equal to the number of points of each series of pressate
    for i in range(0,len(in_curves[0])):
        temp = []
        #then we cycle for the number of pressate to be taken into consideration
        for j in range(0, len(in_curves)):
            #in this temporary list we collect all the pressate values of
            #the same point in time
            temp.append(in_curves[j][i])
        #of this list we compute the standard deviation and append it to a list
        stdev = statistics.stdev(temp)
        stdev_list.append(stdev)
    #from the list of all the std_devs we compute the average to be used as 
    #threshold for the ideal curve
    std_curve = statistics.mean(stdev_list)
    #increase std_dev with given sigma
    std_curve = std_curve*sigma

    return std_curve


#BS3: target value & target stdev of max force or max height:
def max_targets(max_values, sigma=1):
    '''
    From a list of max strength or height values for each series, it finds the target value 
    to be used as reference for this configuration. 
    Moreover it computes an acceptable deviation for defining the pressata as acceptable.
    
    Parameters
    ----------
    max_values : list 
        List containing the max force or height applied for each series
    sigma : int
        Multiplier to increase acceptable deviation range (default: 1)

    Returns
    -------
    target : double 
        Target max force or height value (valid for all the series given as input)
    dev : double
        The acceptable deviation from this target max value.

    '''
    #in this implementation we simply compute the average of the maximum values of 
    #each series and its std_dev, but we may change it for better results
    target = statistics.mean(max_values)
    dev = statistics.stdev(max_values)
    #increase dev with given sigma
    dev = dev*sigma

    return target, dev


#BS4: compute target parameters for a combo:
def batch_standardize(batch_forces, batch_mf, sigmac=1, sigmaf=1):
    '''
    Function that, given as input a list of original force curves and max_forza values (BOTH for 1 combo only!), it first interpolates all curves, then computes the 4 target parameters for the combo.

    It puts together 4 different functions:
    - interpolate_curve(altezza_combo, altezza, forza)
    - ideal_curve(in_curves)
    - stdev_curve(in_curves)
    - max_targets(max_values, sigma)

    Parameters:
    --------------
    batch_forces: list of lists
        List containing the original force curves (lists) of each series
    batch_mf : list of values
        List containing the max force or height applied for each series
    sigmac, sigmaf : int 
        Multipliers to increase threshold range, one for curve and the other for max_forza (default: 1)

    Returns
    -------------
    Output : 4 parameters
    - forza_combo (list)
    - std_curve (double)
    - target_mf (double)
    - std_mf (double)
    
    '''
    #1) Interpolate all curves:
    batch_forces_itp = []
    for c in batch_forces:
        batch_forces_itp.append(interpolate_curve(c))

    #2) Calculate targets parameters:
    forza_combo = ideal_curve(batch_forces_itp)
    std_curve = stdev_curve(batch_forces_itp, sigmac)
    target_mf, std_mf = max_targets(batch_mf, sigmaf)

    return forza_combo, std_curve, target_mf, std_mf

