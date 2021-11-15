import sys
sys.path.insert(0, './')
from database_functions.db_connect import db_connect, db_disconnect
from utils import write_warning

#TRAINING TOOLS:
# - set_targets_max(mtype)
# - flag_ma(sigma)

#set target MA/MF & it std within combo:
def set_targets_max(mtype):
    '''
    NOTE: requires 
    1. Retrieves max value of Altezza or average value of Forza for each ComboID (FROM: table Pressate)
    2. Saves that value as TargetMA or TargetMF for the correspondent ComboID (TO: table Combos)
    3. Repeats the process for the Stdev of MA or MF
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


#MAIN:
if __name__ == '__main__':
    set_targets_max(mtype='altezza')
    set_targets_max(mtype='forza')
