import sys
sys.path.insert(0, './')
from database_functions.db_connect import db_connect, db_disconnect

#SET TARGET_MA/MF & STD_MA/MF TO COMBOS TABLES:

#set target MA: max & std of max_altezza within combo:
def set_targets_ma():
    '''
    NOTE: requires 
    1. Retrieves max value of Altezza for each ComboID (FROM: table Pressate)
    2. Saves that value as TargetMA for the correspondent ComboID (TO: table Combos)
    3. Repeats the process for the Stdev of MA
    '''
    # Connect
    conn, cursor = db_connect()

    #1) TARGET VALUE OF MAX_ALTEZZA FOR COMBOS:
    cursor.execute('SELECT ComboID, MAX(MaxAltezza) FROM Pressate GROUP BY ComboID')
    # Save query output
    list = cursor.fetchall()
    # Update current values to new values for TargetMA
    for (comboID, max_altezza) in list:
        # updates values (decimal.Decimal -> float)
        cursor.execute("UPDATE Combos SET TargetMA = ? WHERE ComboID = ?", float(max_altezza), comboID)
    cursor.commit()

    #2) STDEV OF MAX_ALTEZZA FOR COMBOS:
    cursor.execute('SELECT ComboID, STDEV(MaxAltezza) FROM Pressate GROUP BY ComboID')
    #Save query output
    list = cursor.fetchall()
    #Update current values to new values for StdMA
    for (comboID, std_ma) in list:
        # updates values
        cursor.execute("UPDATE Combos SET StdMA = ? WHERE ComboID = ?", float(std_ma), comboID) 
    cursor.commit()

    # Disconnect
    db_disconnect(conn, cursor)

    return 0


#set target MF: avg & std of max_forza within combo:
def set_targets_mf():
    '''
    NOTE: requires 
    1. Retrieves average value of Forza for each ComboID (FROM: table Pressate)
    2. Saves that value as TargetMF for the correspondent ComboID (TO: table Combos)
    3. Repeats the process for the Stdev of MF
    '''
    # Connect
    conn, cursor = db_connect()

    #1) TARGET VALUE OF MAX_FORZA FOR COMBOS:
    cursor.execute('SELECT ComboID, AVG(MaxForza) FROM Pressate GROUP BY ComboID')
    #Save query output
    list = cursor.fetchall()
    #Update current values to new values for TargetMF
    for (comboID, max_forza) in list:
        # updates values
        cursor.execute("UPDATE Combos SET TargetMF = ? WHERE ComboID = ?", float(max_forza), comboID) 
    cursor.commit()

    #2) STDEV OF MAX_FORZA FOR COMBOS:
    cursor.execute('SELECT ComboID, STDEV(MaxForza) FROM Pressate GROUP BY ComboID')
    #Save query output
    list = cursor.fetchall()
    #Update current values to new values for StdMF
    for (comboID, std_mf) in list:
        # updates values
        cursor.execute("UPDATE Combos SET StdMF = ? WHERE ComboID = ?", float(std_mf), comboID)
    cursor.commit()

    # Disconnect
    db_disconnect(conn, cursor)

    return 0


#MAIN:
set_targets_ma()
#set_targets_mf()
