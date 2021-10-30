import statistics
import warnings
from access_db import query_bycombo

#STATISTICAL ANALYSIS, TRAINING & EVALUATION FUNCTIONS:

#Mean & variance:
def get_stats(misura):
    '''
    Computes mean and variance of all the elements contained in the list misura
    :param mean: Bool
    :param variance: Bool
    :param misura: array
    :return: (float, float)
    '''

    media = statistics.stdev(misura)
    varianza = statistics.stdev(misura)

    return media, varianza


#BS1:
def ideal_curve(input):
    '''
    Function to compute the ideal curve for a specific combination given by 
    the mean value between its points on the x-axis 

    Parameters
    input : list of list
        It's the collection of already normalized series of which we want to 
        compute the ideal behaviour. That said it is critical that each series 
        should be of the same size!

    Returns
    out : list
        A list contining the average value of each point in all the series, 
        it's lenght is the same as the one of every series

    '''
    out = []
    for i in range(0,len(input[0])):
        temp = []
        for j in range(0, len(input)):
            temp.append(input[j][i])
        avg, v = get_stats(temp)
        out.append(avg)
    return out


#BS2:
def threshold_variance(input):
    '''
    Function to compute the average variance value to be used as threshold 
    when looking if a new sample will be in or out the ideal curve

    Parameters
    ----------
    input : list of list
        It's the collection of already normalized series of which we want to 
        compute the ideal behaviour. That said it is critical that each series 
        should be of the same size!

    Returns
    -------
    avg_var : double
        A list contining the average value of each point in all the series, 
        it's lenght is the same as the one of every series

    '''
    var_list = []
    for i in range(0,len(input[0])):
        temp = []
        for j in range(0, len(input)):
            temp.append(input[j][i])
        a, var = get_stats(temp)
        var_list.append(var)
    avg_var, v = get_stats(var_list)
    return avg_var


#BS3:
def max_force_threshold(max_values):
    '''
    From a list of max strength values for each series, then finds the average 
    to be used as reference for this configuration. 
    Moreover it computes a value (the standard deviaion) for accepting or not 
    a new data 
    
    Parameters
    ----------
    max_values : list 
        List containing the max force applied for each series

    Returns
    -------
    max_force : double 
        Average force from all the series given as input
    threshold : double
        The standard deviation of the list collecting all of the max force for 
        each series

    '''
    avg, threshold = get_stats(max_values)
    return avg, threshold


#BS4:
def batch_standardize(taglia,idcomp):
    '''
    Function that computes the query selecting taglia and idcomp and 
    create a variable called combo; then for every series in the combo it appends
    on the list "batch_forces" -> 'forza' (list of the list) and
    it appends on the list "batch_max" -> 'max_forza'(list). 

    It puts togheter different functions:
    - query_bycombo(taglia,idcomp)
    - ideal_curve(input)
    - threshold_variance(input)
    - max_force_threshold(input)

    Parameters:
    --------------
    input : taglia and idcomp : string
    String containig the taglia of "riduttore" and id of the "componente"

    Returns
    -------------
    Output : 4 parameters
    - curva_ideale (list)
    - avg_var (double)
    - max_force (double)
    - threshold (oudble)
    
    '''
    batch_forces = []
    batch_max = []
    
    combo = query_bycombo(taglia,idcomp)
    for series in combo.series:
        batch_forces.append(series.forza)
        batch_max.append(series.max_forza)
    
    curva_ideale = ideal_curve(batch_forces)
    avg_var = threshold_variance(batch_forces)
    max_force, mfthreshold = max_force_threshold(batch_max)

    return curva_ideale, avg_var, max_force, mfthreshold


#EV0: Evaluate function:
def evaluate(max_forza, forza, curva_ideale, avg_var, max_forza_target, mfthreshold):
    '''
    Function that evaluates if pressata is correctly or not. 
    If: the value that represents the max force in the process is between max force
    target +- a threshold, the algorithm makes another comparison with ideal curve: 
        if the curves already interpolate and normalized is similar to the ideal 
        curve, then pressata is correctly 

    Otherwise something is wrong

    Parameters:
    -------------------
    input: 
    - max_forza (double)
    - forza(list) 
    - curva_ideale (list)
    - avg_var (double)
    - max_forza_target (double)
    - mfthreshold (double) 
    
    output: 
    count (int): that counts how many times pressata is correctly
    '''
    count_out = 0

    if (max_forza >= max_forza_target - mfthreshold) and (max_forza <= max_forza_target + mfthreshold):
        print("Max_forza: accepted.")
        for i,item in enumerate(forza):
            if (item < curva_ideale[i]- avg_var) or (item > curva_ideale[i] + avg_var):
                count_out+= count_out
        
        if count_out == 0:
            print("Curve: assembly success. .")
        else:
            warnings.warn("WARNING: curve out of bounds in {} points out of {}! Please check the assembly.".format(count_out, len(forza)))

    else:
        warnings.warn("WARNING: max_forza out of acceptable range! Please check the assembly.")
    
    return count_out

