import sys, logging
sys.path.insert(0, './')
from database_functions.db_connect import db_connect, db_disconnect
from evaluation.eval_tools import evaluate_max
from utils import write_warning

#TRAINING TOOLS:
# - set_targets_max(mtype)
# - flag_ma(sigma_ma)


#set target MA/MF & it std within combo:
def set_targets_max(mtype):
    '''
    NOTE: requires 
    1. Retrieves max value of Altezza (or average value of Forza) and the Stdev of MA (or MF) for each ComboID (FROM: table Pressate)
    2. Saves the values as TargetMA (or TargetMF) and StdMA (or StdMF) for the correspondent ComboID (TO: table Combos)
    '''
    #arg check: 
    if mtype == 'altezza':
        mt = 'MAX(MaxAltezza)'
        st = 'STDEV(MaxAltezza)'
        v = 'A'
    elif mtype == 'forza':
        mt = 'AVG(MaxForza)'
        st = 'STDEV(MaxForza)'
        v = 'F'
    else:
        print("ERROR: mtype must by either 'altezza' or 'forza'.")
        return -1

    # Connect
    conn, cursor = db_connect()
    # Extract info for Pressate
    cursor.execute("SELECT ComboID, "+mt+", "+st+" FROM Pressate GROUP BY ComboID")
    list = cursor.fetchall()
    # Update Combos values to TargetMA/MF and StdMA/MF
    for (comboID, max_v, std_v) in list:
        # updates values (decimal.Decimal -> float)
        cursor.execute("UPDATE Combos SET TargetM"+v+" = ?, StdM"+v+" = ? WHERE ComboID = ?", float(max_v), float(std_v), comboID)
    cursor.commit()

    # Disconnect
    db_disconnect(conn, cursor)
    return 0


#Dataset cleaning: flag warnings for MA:
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


#MAIN:
if __name__ == '__main__':
    set_targets_max(mtype='altezza')
    set_targets_max(mtype='forza')
    flag_ma(sigma_ma=1)
