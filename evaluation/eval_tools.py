import sys
sys.path.insert(0, './')
from database_functions.db_connect import db_connect, db_disconnect
import pandas as pd

#EVALUATION TOOLS:
# - class Collector(id) (to provisionally store parameters)
# - evaluate_max(cur, tgt, std, mtype, sigma=1)
# - evaluate_curve(cur_forza, tgt_forza, std_curve, sigma=1)


#Color codes for printing to stdout:
OKGREEN = '\033[92m'
WARNINGCOL = '\033[93m'
ENDCOLOR = '\033[0m' #reset to white

#container class:
class Collector:
    def __init__(self, id):
        self.id = id
        self.ma = 0
        self.mf = 0
        self.std_ma = 0
        self.std_mf = 0
        self.std_curve = 0
        self.altezza = []
        self.forza = []


#Eval max_altezza or max_forza:
def evaluate_max(cur, tgt, std, mtype, sigma=1):
    '''
    Function that evaluates if the max_value of either altezza or forza is within the target +- a threshold.
    
    Parameters:
    -------------------
    input:
    - cur, tgt, std (floats) -> current targets for the combo
    - mtype -> must be either 'altezza' or 'forza'
    - sigma value (int) -> will increase the std_dev in the DB (acceptable boundary)
    
    output:
    - wid (warning id) -> if warning found, else 0 (if success) or -1 (if arg error).
    '''
    #arg check: 
    if mtype == 'altezza':
        wid = 1
    elif mtype == 'forza':
        wid = 3
    else:
        print("ERROR: mtype must by either 'altezza' or 'forza'.")
        return -1
    
    #eval:
    dev = std * sigma
    if (cur >= (tgt - dev)) and (cur <= (tgt + dev)):
        print(OKGREEN+"Max_"+mtype+": accepted."+ENDCOLOR)
        return 0
    else:
        print(WARNINGCOL+"WARNING! ID #"+str(wid)+ENDCOLOR)
        return wid


#Eval curve (point by point):
def evaluate_curve(cur_forza, tgt_forza, std_curve, sigma=1):
    '''
    Function that evaluates if all points of the curve (already interpolated) are within the acceptable std_dev bound 
    from the ideal curve, increased by a sigma.

    Parameters:
    -------------------
    input:
    - cur_forza, tgt_forza, std_curve (list, list, float) -> current targets for the combo
    - sigma value (int) -> will increase the std_dev in the DB (acceptable boundary)
    
    output:
    - count_out (int) -> count of points out of bounds
    - wid (warning id) -> if warning found, else 0.
    '''
    count_out = 0
    dev = std_curve * sigma
    
    #count points out of bounds:
    for i in range(len(cur_forza)):
        if (cur_forza[i] < (tgt_forza[i] - dev)) or (cur_forza[i] > (tgt_forza[i] + dev)):
            count_out = count_out + 1

    #final check on curve:
    if count_out == 0:
        wid = 0
        print(OKGREEN+"Curve: assembly success. No warnings."+ENDCOLOR)
    else:
        wid = 4
        print(WARNINGCOL+"WARNING! ID #"+str(wid)+ENDCOLOR)
    return count_out, wid


#Extract parameters from DB:
def extract_params(timestamp):
    '''
    Function that extracts from the DB all the needed parameters and values for the evaluation.

    Parameters:
    -------------------
    input:
    - timestamp (int) -> timestamp of the pressata under analysis
    
    output:
    - count_out (int) -> count of points out of bounds
    - current, target (Collector) -> 2 Collector objects storing provisionally all the parameters and values needed: one for the current pressata under analysis, the other for the target reference combo.
    '''
    # open connection
    cnxn, cursor = db_connect()
    
    #1) CURRENT PRESSATA:
    #init collector:
    current = Collector(timestamp)

    #EXTRACT DATA FOR CURRENT TIMESTAMP:
    query = "SELECT ComboID, MaxForza, MaxAltezza FROM Pressate WHERE Timestamp="+str(timestamp)
    df = pd.read_sql(query, cnxn)
    #comboid:
    combo_id = str(df['ComboID'][0])
    #extract data:
    current.mf = float(df['MaxForza'][0])
    current.ma = float(df['MaxAltezza'][0])

    #EXTRACT ORIGINAL CURVES FOR CURRENT TIMESTAMP:
    query = "SELECT Forza, Altezza FROM PressateData WHERE Timestamp="+str(timestamp)
    #store to Pandas dataframe
    df = pd.read_sql(query, cnxn)
    #extract data:
    current.forza = list(df['Forza'].to_numpy())
    current.altezza = list(df['Altezza'].to_numpy())


    #2) TARGET COMBOID:
    #init collector:
    target = Collector(combo_id)

    #EXTRACT TARGET COMBO DATA:
    query = "SELECT TargetMA, TargetMF, StdMA, StdMF, StdCurve FROM Combos WHERE ComboID='"+str(combo_id)+"'"
    df = pd.read_sql(query, cnxn)
    #extract data:
    target.ma = float(df['TargetMA'][0])
    target.mf = float(df['TargetMF'][0])
    target.std_ma = float(df['StdMA'][0])
    target.std_mf = float(df['StdMF'][0])
    target.std_curve = float(df['StdCurve'][0])

    #EXTRACT TARGET CURVES FOR THE COMBO:
    query = "SELECT Forza, Altezza FROM CombosData WHERE ComboID='"+str(combo_id)+"'"
    #store to Pandas dataframe
    df = pd.read_sql(query, cnxn)
    #extract data:
    target.forza = list(df['Forza'].to_numpy())
    target.altezza = list(df['Altezza'].to_numpy())

    #close cursor and connection
    db_disconnect(cnxn, cursor)

    return current, target 


#MAIN (for tests):
if __name__ == '__main__':
    timestamp = 1584106169
    current, target = extract_params(timestamp)
    print("Current:")
    print(vars(current).items())
    print("\nTarget:")
    print(vars(target).items())

