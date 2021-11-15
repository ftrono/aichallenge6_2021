import logging
import sys
sys.path.insert(0, './')
from utils import interpolate_curve, visualize, write_warning
from eval_tools import extract_params, evaluate_max, evaluate_curve


#PART III) EVALUATE

def evaluate(timestamp, visual=False, sigma_ma=1, sigma_mf=1, sigma_curve=1):
    '''
    Function that evaluates if a pressata is correct or not. 
    It queries for the parameters of the pressata's combo, interpolates the curve and 
    then makes 3 checks through the following functions:
    1) evaluate_max, with mtype = 'altezza';
    2) evaluate_max, with mtype = 'forza';
    3) evaluate_curve, which scans the curve point by point;
    
    If one check fails, the function is immediately interrupted: the warning is saved to the DB
    and no further checks are made. A logging message is printed to a log file. (Return: -1)

    If all 3 checks are ok, then the pressata is considered acceptable. (Return: 0)

    Parameters:
    -------------------
    input:
    - timestamp (int) -> current pressata
    - visual (bool) -> calls curve visualization function
    - sigma values (int) for: MA, MF and curve std (will increase the dev in the DB)
    
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
    wid = evaluate_max(current.ma, target.ma, target.std_ma, mtype='altezza', sigma=sigma_ma) 
    if wid != 0:
        #log:
        logging.warning(str(timestamp)+" ID #"+str(wid)+": max_altezza out of acceptable range! Please check the assembly.")
        #write warning to DB:
        write_warning(timestamp, wid)
        if visual:
            visualize(target.forza, target.std_curve, target.altezza, current.forza)
        return -1

    #check 2: max_forza
    wid = evaluate_max(current.mf, target.mf, target.std_mf, mtype='forza', sigma=sigma_mf)
    if wid != 0:
        #log:
        logging.warning(str(timestamp)+" - ID #"+str(wid)+": max_forza out of acceptable range! Please check the assembly.")
        #write warning to DB:
        write_warning(timestamp, wid)
        if visual:
            visualize(target.forza, target.std_curve, target.altezza, current.forza)
        return -1
    
    #check 3: compare curve
    count_out, wid = evaluate_curve(current.forza, target.forza, target.std_curve, sigma=sigma_curve)
    if count_out != 0:
        #log:
        logging.warning(str(timestamp)+" - ID #"+str(wid)+": curve out of bounds in "+str(count_out)+" points out of "+str(len(current.forza))+"! Please check the assembly.")
        #write warning to DB:
        write_warning(timestamp, wid)
        if visual:
            visualize(target.forza, target.std_curve, target.altezza, current.forza)
        return -1
    else:
        return 0


#MAIN:
#print(evaluate_curve(1584106169, visual=True))
