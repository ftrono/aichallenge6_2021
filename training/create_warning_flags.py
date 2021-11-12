from database_functions.db_connect import db_connect, db_disconnect

# TODO: sigma thing, using write_warnings(timestamp, wid) da utils, con wid = 1

def warning_flags_marking()
    '''
    NOTE: requires 
    1. Retrieves max value of Altezza for each ComboID (FROM: table Pressate)
    2. Saves that value as TargetMA for the correspondent ComboID (TO: table Combos)
    '''
    # Connect
    conn, cursor = db_connect()

    # Get max value of max_altezza
    get_max_altezza = 'SELECT ComboID, MAX(MaxAltezza) FROM Pressate GROUP BY ComboID'
    cursor.execute(get_max_altezza)
    # Save query output
    list = cursor.fetchall()
    # Update current values to new values for TargetMA
    for item in list:
        for comboID, max_altezza in list:
            max_altezza = float(max_altezza) # (decimal.Decimal -> float)
            cursor.execute("UPDATE Combos SET TargetMA = ? WHERE ComboID = ?", max_altezza, comboID) # updates values
        cursor.commit()

    # Disconnect
    db_disconnect(conn, cursor)