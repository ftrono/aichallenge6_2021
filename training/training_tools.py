import sys, statistics
sys.path.insert(0, './')
from database_functions.db_connect import db_connect, db_disconnect
from utils import interpolate_curve
import pandas as pd

#TRAINING TOOLS:
# - train_max(mtype)
# - ideal_curve(batch_forces)
# - stdev_curve(batch_forces)
# - train_curves()


#train & set target MA/MF & its std within combo:
def train_max(mtype):
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


#BS1: curve of means:
def ideal_curve(batch_forces):
    '''
    Function to compute the ideal curve for a specific combination given by 
    the mean value between its points on the x-axis 

    Parameters
    batch_forces : list of lists
        It's the collection of already interpolated series of which we want to 
        compute the ideal force curve. That said it is critical that each series 
        should be of the same size!

    Returns
    out_curve : list
        A list contining the average value of each point in all the series, 
        it's lenght is the same as the one of every series

    '''
    out_curve = []
    #first cycle for a number of times equal to the number of point of each 
    #series of pressate
    for i in range(0,len(batch_forces[0])):
        temp = []
        #then cycle for the number of pressate to be taken into consideration
        for j in range(0, len(batch_forces)):
            #in this temporary list we collect all of the pressate values of
            #the same point in time
            temp.append(batch_forces[j][i])
        #of this list we compute the average and append it to the final list
        avg = statistics.mean(temp)
        out_curve.append(avg)
        #then we repeat the cycle for another set of pressate in the following
        #point in time
    return out_curve


#BS2: stdev of force curve:
def stdev_curve(batch_forces):
    '''
    Function to compute the average std_dev to be used as threshold 
    when looking if a new sample will be in or out the ideal curve boundaries

    Parameters
    ----------
    batch_forces : list of lists
        It's the collection of already interpolated series of which we want to 
        compute the ideal behaviour. That said it is critical that each series 
        should be of the same size!

    Returns
    -------
    std_curve : double
       The value of the average std_devs of all points in the series.

    '''
    stdev_list = []
    #we cycle for a number of times equal to the number of points of each series of pressate
    for i in range(0,len(batch_forces[0])):
        temp = []
        #then we cycle for the number of pressate to be taken into consideration
        for j in range(0, len(batch_forces)):
            #in this temporary list we collect all the pressate values of
            #the same point in time
            temp.append(batch_forces[j][i])
        #of this list we compute the standard deviation and append it to a list
        stdev = statistics.stdev(temp)
        stdev_list.append(stdev)
    #from the list of all the std_devs we compute the average to be used as 
    #threshold for the ideal curve
    std_curve = statistics.mean(stdev_list)

    return std_curve


#NEW BS4: train & set curves within combo:
def train_curves():
    # Connect
    conn, cursor = db_connect()
    combos = []
    timestamps = []
    batch_forces = []

    print("Started curves training.")

    #extract list of comboids:
    cursor.execute("SELECT DISTINCT ComboID FROM Combos")
    for tup in cursor.fetchall():
        combos.append(tup[0])
    
    #train each comboid:
    for comboid in combos:
        #print("Training comboid {}".format(comboid))
        #1) extract all timestamps with that ComboID and with NO warnings:
        cursor.execute("SELECT Pressate.Timestamp FROM Pressate WHERE Pressate.ComboID = ? AND NOT EXISTS (SELECT Warnings.Timestamp FROM Warnings WHERE Warnings.Timestamp = Pressate.Timestamp)", comboid)
        for tup in cursor.fetchall():
            timestamps.append(tup[0])

        #2) for each timestamp:
        for t in timestamps:
            #extract original curves (forza and altezza):
            query = "SELECT Altezza, Forza FROM PressateData WHERE Timestamp="+str(t)
            #store to Pandas dataframe
            df = pd.read_sql(query, conn)
            #extract data:
            cur_altezza = list(df['Altezza'].to_numpy())
            cur_forza = list(df['Forza'].to_numpy())

            #extract stamp vector (altezza_combo):
            query = "SELECT Altezza FROM CombosData WHERE ComboID='"+str(comboid)+"'"
            #store to Pandas dataframe
            df = pd.read_sql(query, conn)
            #extract data:
            combo_altezza = list(df['Altezza'].to_numpy())

            #interpolate force curve:
            itp_forza = interpolate_curve(combo_altezza, cur_altezza, cur_forza)

            #store to batch list for the current ComboID:
            batch_forces.append(itp_forza)
            
        #3) get target curve parameters for the combo (batch_standardize):
        forza_combo = ideal_curve(batch_forces)
        std_curve = stdev_curve(batch_forces)

        #4) store target curve parameters to DB (Combos & CombosData tables):
        cursor.execute("UPDATE CombosData SET Forza = ? WHERE ComboID = '?'", forza_combo, comboid)
        cursor.commit()
        cursor.execute("UPDATE Combos SET StdCurve = ? WHERE ComboID = '?'", std_curve, comboid)
        cursor.commit()

        #5) reset:
        timestamps = []
        batch_forces = []

    print("Training complete!")

    # Disconnect
    db_disconnect(conn, cursor)

    return 0


#MAIN:
if __name__ == '__main__':
    train_max(mtype='altezza')
    train_max(mtype='forza')
    train_curves()
