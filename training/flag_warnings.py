import logging
import sys
sys.path.insert(0, './')
from database_functions.db_connect import db_connect, db_disconnect
from evaluation.eval_tools import evaluate_max
from utils import write_warning

#FLAG WARNINGS (FOR DATASET CLEANING):
# - flag_ma(sigma_ma)
# - pairwise_delta(array)
# - flag_dtimes()


#FLAG1: flag warnings for MA:
def flag_ma(sigma_ma=1):
    '''
    Function that checks if MaxAltezza is out if the bounds. 
    Bounds = Target max altezza + - deviation.
    deviation = sigma * target max altezza

    Input:
    - Sigma: int

    Output:
    - Write on db if there is warning: warning #1

    ''' 
    conn, cursor = db_connect()

    #SET LOG TO FILE:
    logging.basicConfig(level=logging.WARNING, filename='./logs/training.log', filemode='a', format='%(asctime)s %(levelname)s %(message)s')

    #extract data from Pressate and Combos with inner join:
    cursor.execute("SELECT Pressate.Timestamp, Pressate.MaxAltezza, Pressate.ComboID, Combos.TargetMA, Combos.StdMA FROM Pressate INNER JOIN Combos ON Pressate.ComboID = Combos.ComboID")
    ls = cursor.fetchall()
    #print(ls[0])
    for row in ls:
        timestamp = row[0]
        cur_ma = float(row[1])
        tgt_ma = float(row[3])
        #dev = std_ma * sigma:
        dev = float(row[4]) * sigma_ma
        #evaluate:
        wid = evaluate_max(cur_ma, tgt_ma, dev, mtype='altezza', sigma=sigma_ma)
        if wid != 0:
            #log:
            logging.warning("Timestamp: {}. ID #{}: max_altezza out of acceptable range.".format(timestamp, wid))
            #write warning to DB:
            write_warning(timestamp, wid)

    # Disconnect
    db_disconnect(conn, cursor)


# Helper: pairwise delta
def pairwise_delta(array):
    '''
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
def flag_dtimes():
    # Connect
    conn, cursor = db_connect()
    
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
    db_disconnect(conn, cursor)
        
    return 0


#MAIN:
if __name__ == '__main__':
    flag_ma(sigma_ma=1)
    flag_dtimes()
