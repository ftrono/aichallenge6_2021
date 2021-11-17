import sys, warnings, pyodbc
import matplotlib.pyplot as plt
sys.path.insert(0, './')
from database_functions.db_connect import db_connect, db_disconnect

#COMMON UTILITY FUNCTIONS:
# - execute_query_file()
# - write_warning()
# - visualize()
# - interpolate_curve()


# Execute commands by filename
def execute_query_file(filename):
    '''
    Runs all the commands (queries) contained into a file.sql

    params: filename: specify name of the file.sql to run
    '''
    # Open and read the file as a single buffer
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()

    # Split sql commands on ';'
    sqlCommands = sqlFile.split(';')

    # open connection
    cnxn, cursor = db_connect()

    # Execute every command from the input file
    for command in sqlCommands:
        try:
            cursor.execute(command)
            cursor.commit()
        except pyodbc.OperationalError as msg:
            print("Command skipped: ", msg)
    
    # Close cursor and connection 
    db_disconnect(cnxn, cursor)


#Write warnings to DB
def write_warning(dbt, riduttore, wid, timestamp=None):
    '''
    Write a warning for the current pressata / riduttore to the Warnings table in the DB.
    
    (params):
        - riduttore (int) : id of the riduttore under analysis
        - wid (int): warning_id to write to the table for the pressata [1, 2, 3 or 4]
        - timestamp (long, optional) : timestamp of the pressata under analysis, if known.
    '''
    dbt['cursor'].execute("INSERT INTO Warnings (RiduttoreID, Timestamp, WarningID) VALUES (?, ?, ?)", riduttore, timestamp, wid)
    dbt['cursor'].commit()
    return 0


#FULL (AFTER EVALUATE): visualize ideal curve, boundaries & current curve:
def visualize(forza_combo, std_curve, altezza_combo, cur_forza):
    #calculate upper & lower bound:
    ci_boundup = [(forza_combo[i]+std_curve) for i in range(len(forza_combo))]
    ci_boundlow = [(forza_combo[i]-std_curve) for i in range(len(forza_combo))]

    #plot:
    plt.plot(altezza_combo, forza_combo, color='green', linewidth=4, label="Ideal curve")
    plt.plot(altezza_combo, ci_boundup, color='orange', linestyle='--', linewidth=1, label="Upper boundary")
    plt.plot(altezza_combo, ci_boundlow, color='red', linestyle='--', linewidth=1, label="Lower boundary")
    plt.plot(altezza_combo, cur_forza, color='blue', linewidth=2, label="CURRENT CURVE")
    plt.xlabel('Altezza (mm)')
    plt.ylabel('Forza (kN)')
    plt.legend(fontsize='x-small', frameon=False)
    
    plt.show()

    return 0


#HORIZONTAL INTERPOLATION:
#interpolate curve based on target altezza vector for the combo:
def interpolate_curve(altezza_combo, altezza, forza):
    '''
    Aligns horizontally both the forza and altezza vectors on the basis of a "stamp",
    represented by the target altezza vector for a combo(taglia, id_comp).
    The target altezza vector has a standard number of points based on a predefined sample rate.

    params: (list) target vector for a combo(taglia, altezza):,
            (list) orig altezza vector:,
            (list) orig forza vector.
    returns:
            (list) interpolated forza vector.
    '''
    #objects:
    new_forza = []
    i = 0
    v = 0
    tgt_len = len(altezza_combo)

    if altezza == [] or altezza_combo == []:
        return warnings.warn("Error: empty list.")

    #1) initial padding:
    if altezza[0] > altezza_combo[0]:
        while altezza_combo[i] < altezza[0]:
            #pad:
            new_forza.append(0)
            i = i+1

    #2) interpolate values:
    for i in range(i, tgt_len):
        #pad check:
        if v < len(altezza):
            #find closest value of altezza_combo[i] in orig altezza list:
            #the loop will stop at the last index (v) in which the value of altezza is before (or equal to) the value of altezza_combo[i]:
            while (altezza[v] < altezza_combo[i]):
                #go to next:
                v = v+1
                #check end of orig list:
                if v >= len(altezza):
                    #ending padding:
                    new_forza.append(0)
                    break
            
            if v < len(altezza):
                #calculate interpolated value:
                if altezza[v] == altezza_combo[i]:
                    #if equal, save same:
                    new_forza.append(forza[v])
                else:
                    #INTERPOLATE:
                    #indices:
                    left = v-1
                    right = v

                    dx = altezza[right]-altezza[left]
                    xgap = altezza[right]-altezza_combo[i]
                    dy = forza[right]-forza[left]
                    #xgap:dx=ygap:dy
                    ygap = (xgap*dy)/dx

                    #calculate:
                    new_forza.append(round((forza[right]-ygap),2))
                    
                    #print("Altezza: {}, {}, {}".format(altezza[left], altezza[right], altezza_combo[i]))
                    #print("Forza: {}, {}, {}".format(forza[left], forza[right], new_forza[i]))
        
        else:
            #3) Ending padding:
            new_forza.append(0)

    return new_forza
