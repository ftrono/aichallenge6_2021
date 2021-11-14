import statistics

#STATISTICAL ANALYSIS FUNCTIONS:
# - ideal_curve(in_curves)
# - stdev_curve(in_curves)
# - batch_standardize(batch_forces)

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
def stdev_curve(in_curves):
    '''
    Function to compute the average std_dev to be used as threshold 
    when looking if a new sample will be in or out the ideal curve boundaries

    Parameters
    ----------
    in_curves : list of lists
        It's the collection of already interpolated series of which we want to 
        compute the ideal behaviour. That said it is critical that each series 
        should be of the same size!

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

    return std_curve


#BS4: compute ideal curve and stdcurve for a combo (note: need to call interpolate_curve() before this!):
def batch_standardize(batch_forces):
    '''
    Function that, given as input a list of already interpolated force curves (for 1 combo only!), it computes the ideal force curve and its stdev (always for 1 combo).

    It puts together 2 different functions:
    - ideal_curve(in_curves)
    - stdev_curve(in_curves)

    Parameters:
    --------------
    batch_forces: list of lists
        List containing the already interpolated force curves (lists) of each series

    Returns
    -------------
    Output : 2 parameters
    - forza_combo (list)
    - std_curve (double)
    
    '''

    #Calculate target curve parameters:
    forza_combo = ideal_curve(batch_forces)
    std_curve = stdev_curve(batch_forces)

    return forza_combo, std_curve

