import logging
from utils import interpolate_curve, visualize

#Color codes for printing to stdout:
OKGREEN = '\033[92m'
WARNINGCOL = '\033[93m'
ENDCOLOR = '\033[0m' #reset to white


#PART III) EVALUATE

#EV0: Evaluate a new curve:
def evaluate_curve(timestamp, visual=False):
    '''
    Function that evaluates if a pressata is correct or not. 
    It queries for the parameters of the pressata's combo, interpolates the curve and 
    then makes 3 checks:
        1) if the value that represents the max force in the process is between max force
        target +- a threshold;
        2) if the value that represents the max altezza in the process is between max altezza
        target +- a threshold;
        3) if all points of the curve (already interpolated and normalized) are within the acceptable std_dev bound from the ideal curve.
    
    If one check fails, the function is immediately interrupted: the warning is saved to the DB
    and no further checks are made. A logging message is printed to a log file. (Return: -1)

    If all 3 checks are ok, then the pressata is considered acceptable. (Return: 0)

    Parameters:
    -------------------
    input:
    - timestamp (int) -> current pressata
    - visual (bool) -> calls curve visualization function
    
    output: 
    - 0 if pressata is accepted
    - -1 if warnings found.

    '''
    #LOGGING TO FILE (DA CONFIGURARE):
    #logging.basicConfig(filename='./logs/eval_warnings.log', filemode='a', format='%(message)s')

    #QUERY:
    #Sostituire i parametri di input: lasciare solo il timestamp e chiamare qui dentro la query che prenda 
    #tutti i parametri che servono:
    cur_mf = 0 #da query
    cur_ma = 0 #da query
    cur_forza = [] #da query
    cur_altezza = [] #da query
    forza_combo = [] #da query
    altezza_combo = [] #da query
    std_curve = 0 #da query
    target_mf = 0 #da query
    std_mf = 0 #da query
    target_ma = 0 #da query
    std_ma = 0 #da query

    #INTERPOLATE CURVE:
    cur_forza = interpolate_curve(altezza_combo, cur_altezza, cur_forza)

    #CHECKS:
    #check 1: max_altezza
    if (cur_ma >= (target_ma-std_ma)) and (cur_ma <= (target_ma+std_ma)):
        print(OKGREEN+"Max_altezza: accepted."+ENDCOLOR)    
    else:
        print(WARNINGCOL+"WARNING! ID #0"+ENDCOLOR)
        #logging
        logging.warning(str(timestamp)+" - WARNING! ID #0: max_altezza out of acceptable range! Please check the assembly.")
        #salvare il giusto warning_id nel DB.
        if visual:
            visualize(forza_combo, std_curve, altezza_combo, cur_forza)
        return -1

    #check 2: max_forza
    if (cur_mf >= (target_mf-std_mf)) and (cur_mf <= (target_mf+std_mf)):
        print(OKGREEN+"Max_forza: accepted."+ENDCOLOR)
    else:
        print(WARNINGCOL+"WARNING! ID #2"+ENDCOLOR)
        #logging
        logging.warning(str(timestamp)+" - WARNING! ID #2: max_forza out of acceptable range! Please check the assembly.")
        #salvare il giusto warning_id nel DB.
        if visual:
            visualize(forza_combo, std_curve, altezza_combo, cur_forza)
        return -1
    
    #check 3: compare curve
    count_out = 0
    for i in range(len(cur_forza)):
        if (cur_forza[i] < (forza_combo[i]-std_curve)) or (cur_forza[i] > (forza_combo[i]+std_curve)):
            #count points out of bounds:
            count_out = count_out + 1

    #final check on curve:
    if count_out == 0:
        print(OKGREEN+"Curve: assembly success. No warnings."+ENDCOLOR)
        return 0 #ok
    else:
        print(WARNINGCOL+"WARNING! ID #3"+ENDCOLOR)
        #logging
        logging.warning(str(timestamp)+" - WARNING! ID #3: curve out of bounds in "+str(count_out)+" points out of "+str(len(cur_forza))+"! Please check the assembly.")
        #salvare il giusto warning_id nel DB.
        if visual:
            visualize(forza_combo, std_curve, altezza_combo, cur_forza)
        return -1
