import logging
import sys
sys.path.insert(0, './')
from utils import interpolate_curve, visualize, write_warning
from extract_params import extract_params

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
    #SET LOG TO FILE:
    logging.basicConfig(level=logging.WARNING, filename='./logs/eval_warns.log', filemode='a', format='%(asctime)s %(levelname)s %(message)s')

    #QUERY:
    #call extract_params, which return 2 objects with all needed params 
    #(one for the current pressata, the other for the target combo):
    current, target = extract_params(timestamp)

    #INTERPOLATE CURVE (overwrite current.forza into collector object):
    current.forza = interpolate_curve(target.altezza, current.altezza, current.forza)

    #CHECKS:
    #check 1: max_altezza
    if (current.ma >= (target.ma - target.std_ma)) and (current.ma <= (target.ma + target.std_ma)):
        print(OKGREEN+"Max_altezza: accepted."+ENDCOLOR)    
    else:
        wid = 0
        print(WARNINGCOL+"WARNING! ID #"+str(wid)+ENDCOLOR)
        #logging
        logging.warning(str(timestamp)+" ID #"+str(wid)+": max_altezza out of acceptable range! Please check the assembly.")
        #write warning to DB:
        write_warning(timestamp, wid)
        if visual:
            visualize(target.forza, target.std_curve, target.altezza, current.forza)
        return -1

    #check 2: max_forza
    if (current.mf >= (target.mf - target.std_mf)) and (current.mf <= (target.mf + target.std_mf)):
        print(OKGREEN+"Max_forza: accepted."+ENDCOLOR)
    else:
        wid = 2
        print(WARNINGCOL+"WARNING! ID #"+str(wid)+ENDCOLOR)
        #logging
        logging.warning(str(timestamp)+" - ID #"+str(wid)+": max_forza out of acceptable range! Please check the assembly.")
        #write warning to DB:
        write_warning(timestamp, wid)
        if visual:
            visualize(target.forza, target.std_curve, target.altezza, current.forza)
        return -1
    
    #check 3: compare curve
    count_out = 0
    for i in range(len(current.forza)):
        if (current.forza[i] < (target.forza[i] - target.std_curve)) or (current.forza[i] > (target.forza[i] + target.std_curve)):
            #count points out of bounds:
            count_out = count_out + 1

    #final check on curve:
    if count_out == 0:
        print(OKGREEN+"Curve: assembly success. No warnings."+ENDCOLOR)
        return 0 #ok
    else:
        wid = 3
        print(WARNINGCOL+"WARNING! ID #"+str(wid)+ENDCOLOR)
        #logging
        logging.warning(str(timestamp)+" - ID #"+str(wid)+": curve out of bounds in "+str(count_out)+" points out of "+str(len(current.forza))+"! Please check the assembly.")
        #write warning to DB:
        write_warning(timestamp, wid)
        if visual:
            visualize(target.forza, target.std_curve, target.altezza, current.forza)
        return -1


#MAIN:
#print(evaluate_curve(1584106169, visual=True))
