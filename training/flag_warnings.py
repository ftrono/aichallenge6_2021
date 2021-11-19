import sys, logging,os
sys.path.insert(0, os.getcwd())
#sys.path.insert(0, './')
from globals import *
from database_functions.db_connect import db_connect, db_disconnect
from evaluation.eval_tools import evaluate_max

#FLAG WARNINGS (FOR DATASET CLEANING):
# - flag_ma()
# - (helper) pairwise_delta()
# - flag_rid()


#FLAG1: flag warnings for MA:
def flag_ma(dbt):
    '''
    Function that checks if MaxAltezza is out if the bounds. 
    Bounds = Target max altezza + - deviation.
    deviation = sigma (global) * target max altezza

    Input:
    - dbt (dict) -> dict with cnxn, cursor and logging objects

    Output:
    - Write on db if there is warning: warning #1

    '''
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logging = dbt['logging']

    #extract Timestamp, ComboID and MaxAltezza from Table Pressate and save in a list
    get_data = 'SELECT ComboID, Timestamp, MaxAltezza, RiduttoreID FROM Pressate'
    cursor.execute(get_data)
    list_press = cursor.fetchall()

    #extract ComboID, Target Max altezza and standard deviation max Altezza from Table Combos and save in a list (list_target)
    get_target = 'SELECT ComboID, TargetMA, StdMA FROM Combos'
    cursor.execute(get_target)
    list_target = cursor.fetchall()

    #CHECK id Max Altezza is out of the bounds
    for p in list_press:
        for t in list_target:
            if p[0] == t[0]: #same comboid
                riduttore = p[3]
                timestamp = p[1]
                cur_ma = float(p[2])
                tgt_ma = float(t[1])
                std_ma = float(t[2])
                #evaluate and flag:
                evaluate_max(dbt, riduttore, timestamp, cur_ma, tgt_ma, std_ma, mtype='altezza')
    return 0


# Helper: pairwise delta
def pairwise_delta(array):
    '''
    Helper function.
    Performs pairwise delta of the elements contained into a list
    param: array: list of tuples in the form (RiduttoreID, Timestamp).
    return: list of pairwise deltas
    '''
    #asc_array = array.sort()
    #print(type(asc_array))
    n = 0
    deltas = list()
    while n < (len(array)-1):
        deltas.append(array[n+1][0] - array[n][0])
        n += 1
    return deltas


#FLAG2: extract delta timestamps:
def flag_rid():
    '''
    WIP
    '''
    # Connect
    cnxn, cursor = db_connect()
    
    #Set log to file:
    logging.basicConfig(level=logging.DEBUG, filename='./logs/log_dtimes.log', filemode='w', format='%(message)s')

    # Get unique comboIDs from table Pressata
    cursor.execute("SELECT DISTINCT ComboID FROM Pressate")
    comboIDs = cursor.fetchall()

    for comb_id in comboIDs:
        cursor.execute("SELECT RiduttoreID, COUNT(Timestamp) FROM Pressate WHERE ComboID = ? GROUP BY RiduttoreID", comb_id[0])
        filtered_table = cursor.fetchall()  # list of tuples: (RiduttoreID, TimestampNum)
        for rid_id, tmstp_num in filtered_table:
            if tmstp_num > 3:
                cursor.execute("SELECT Timestamp FROM Pressate WHERE ComboID = ? AND RiduttoreID = ?", comb_id[0], rid_id)
                timestamps = cursor.fetchall()
                # Performing Delta
                deltas = pairwise_delta(timestamps)
                #Log:
                logging.debug(f"ComboID: {comb_id[0]}, RiduttoreID: {rid_id}")
                logging.debug(f"Number of pressate for combo: {tmstp_num}")
                logging.debug(f"Deltas: {deltas}\n")

    # Disconnect
    db_disconnect(cnxn, cursor)
        
    return 0
