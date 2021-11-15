import sys
sys.path.insert(0, './')
from database_functions.db_connect import db_connect, db_disconnect

#TRAINING TOOLS:
# - set_targets_max(mtype)

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

    #1) TARGET VALUE OF MAX_ALTEZZA FOR COMBOS:
    cursor.execute("SELECT ComboID, "+mt+" FROM Pressate GROUP BY ComboID")
    # Save query output
    list = cursor.fetchall()
    # Update current values to new values for TargetMA or TargetMF
    for (comboID, max_v) in list:
        # updates values (decimal.Decimal -> float)
        cursor.execute("UPDATE Combos SET TargetM"+v+" = ? WHERE ComboID = ?", float(max_v), comboID)
    cursor.commit()

    #2) STDEV OF MAX_ALTEZZA FOR COMBOS:
    cursor.execute("SELECT ComboID, "+st+" FROM Pressate GROUP BY ComboID")
    #Save query output
    list = cursor.fetchall()
    #Update current values to new values for StdMA
    for (comboID, std_v) in list:
        # updates values
        cursor.execute("UPDATE Combos SET StdM"+v+" = ? WHERE ComboID = ?", float(std_v), comboID) 
    cursor.commit()

    # Disconnect
    db_disconnect(conn, cursor)

    return 0


#MAIN:
if __name__ == '__main__':
    set_targets_max(mtype='altezza')
    set_targets_max(mtype='forza')
