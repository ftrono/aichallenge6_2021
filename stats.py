import statistics
import warnings
from access_db import query_bycombo

#Color codes for printing to stdout:
OKGREEN = '\033[92m'
WARNINGCOL = '\033[93m'
ENDCOLOR = '\033[0m' #reset to white


#STATISTICAL ANALYSIS, TRAINING & EVALUATION FUNCTIONS:

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
        avg = statistics.mean(temp)
        out.append(avg)
    return out


#BS2:
def threshold_variance(input, sigma=1):
    '''
    Function to compute the average variance value to be used as threshold 
    when looking if a new sample will be in or out the ideal curve

    Parameters
    ----------
    input : list of list
        It's the collection of already normalized series of which we want to 
        compute the ideal behaviour. That said it is critical that each series 
        should be of the same size!
    sigma : int 
        Multiplier to increase avg_var range (default: 1)

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
        var = statistics.stdev(temp)
        var_list.append(var)

    avg_var = statistics.mean(var_list)
    avg_var = avg_var*sigma

    return avg_var


#BS3:
def max_force_threshold(max_values, sigma=1):
    '''
    From a list of max strength values for each series, then finds the average 
    to be used as reference for this configuration. 
    Moreover it computes a value (the standard deviaion) for accepting or not 
    a new data 
    
    Parameters
    ----------
    max_values : list 
        List containing the max force applied for each series
    sigma : int 
        Multiplier to increase threshold range (default: 1)

    Returns
    -------
    max_force : double 
        Average force from all the series given as input
    threshold : double
        The standard deviation of the list collecting all of the max force for 
        each series

    '''
    avg = statistics.mean(max_values)
    threshold = statistics.stdev(max_values)
    threshold = threshold*sigma

    return avg, threshold


#BS4:
def batch_standardize(taglia,idcomp, sigmac=1, sigmaf=1):
    '''
    Function that computes the query selecting taglia and idcomp and 
    create a variable called combo; then for every series in the combo it appends
    on the list "batch_forces" -> 'forza' (list of the list) and
    it appends on the list "batch_max" -> 'max_forza'(list). 

    It puts together different functions:
    - query_bycombo(taglia,idcomp)
    - ideal_curve(input)
    - threshold_variance(input)
    - max_force_threshold(input)

    Parameters:
    --------------
    taglia, idcomp : string
        Strings containing the taglia of "riduttore" and id of the "componente"
    sigmac, sigmaf : int 
        Multipliers to increase threshold range, one for curve and the other for max_forza (default: 1)

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
    avg_var = threshold_variance(batch_forces, sigmac)
    mf_tgt, mf_threshold = max_force_threshold(batch_max, sigmaf)

    return curva_ideale, avg_var, mf_tgt, mf_threshold


#EV0: Evaluate function:
def evaluate(max_forza, forza, curva_ideale, avg_var, mf_tgt, mf_threshold):
    '''
    Function that evaluates if pressata is correctly or not. 
    If: the value that represents the max force in the process is between max force
    target +- a threshold, the algorithm makes another comparison with ideal curve: 
        if all points of the curve (already interpolated and normalized) are within the acceptable variance bound from the ideal curve, then the pressata is considered accepted.

    Otherwise, the count of the curve points that are out of bounds is returned.

    Parameters:
    -------------------
    input: 
    - max_forza (double)
    - forza(list) 
    - curva_ideale (list)
    - avg_var (double)
    - mf_tgt (double)
    - mf_threshold (double) 
    
    output: 
    count_out (list): count of how many points of pressata curve are out of bound.
    '''
    count_out = 0

    if (max_forza >= (mf_tgt-mf_threshold)) and (max_forza <= (mf_tgt+mf_threshold)):
        print(OKGREEN+"Max_forza: accepted."+ENDCOLOR)
        for i in range(len(forza)):
            if (forza[i] < (curva_ideale[i]-avg_var)) or (forza[i] > (curva_ideale[i]+avg_var)):
                count_out = count_out + 1
        
        if count_out == 0:
            print(OKGREEN+"Curve: assembly success."+ENDCOLOR)
        else:
            print(WARNINGCOL+"WARNING: curve out of bounds in "+str(count_out)+" points out of "+str(len(forza))+"! Please check the assembly."+ENDCOLOR)

    else:
        print("WARNING: max_forza out of acceptable range! Please check the assembly.")
    
    return count_out

