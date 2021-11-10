import pyodbc, datetime, warnings
import matplotlib.pyplot as plt

#COMMON UTILITY FUNCTIONS

#CONNECT TO: True=PRODUCTION; False=LOCALHOST
production = False

#DB connection parameters:
driver = '{ODBC Driver 17 for SQL Server}'
database = 'NovoticAI'
if production == True:
    #Novotic DB server address:
    server = ''
    username = 'sa' 
    password = 'AIchallenge6'
    authstr = ';Authentication=#####' #insert ActiveDirectoryPassword
else:
    #localhost:
    server = '127.0.0.1' 
    username = 'sa' 
    password = 'AIchallenge6'
    authstr = '' #leave empty

#DB utils:
def db_connect():
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password+authstr)
    csr = conn.cursor()
    return conn, csr

def db_disconnect(csr, conn):
    csr.close()
    conn.close()


#CSV name parser:
def name_parser(name): # take as input the file name
    # get information from file name
    tempcode=name[0:14]
    id=name[14:19]
    stazione=name[21:23]
    date_time=datetime.datetime(int(name[24:28]), int(name[29:31]), int(name[32:34]),int(name[35:37]),int(name[38:40]),int(name[41:43])) # convert string to date obj
    timestamp=datetime.datetime.timestamp(date_time) # convert date object to timestamp
    return tempcode,id,stazione,timestamp


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


#BASIC: plot a single series:
def plot_single(id, x, y, **title):
    '''
    :param id: label
    :param x: altezza
    :param y: forza
    :param title: optional
    :return:
    '''
    label = id
    plt.plot(x, y)
    plt.xlabel(label)
    plt.title(title)
    graph = plt.show()
    return graph


#VERTICAL NORMALIZATION:
#Push all force curve values bewteen [0, 1]:
def normalize(y_data, plot=False):
    '''
    Takes an array as input, returns the same array with normalized values (to be used only for `forza`).
    Plotting feature on request.
    
    :param array: array of numbers in the form [float1, float2, ... , floatN] or [int1, int2, ... , intN]
    :return: normalized array & plot of the array if requested
    '''
    #Strength data normalization:
    normie = [round(i/max(y_data), 4) for i in y_data]

    # Plotting (optional)
    if plot == True:
        plt.plot(normie)
        plt.show()

    return normie


#HORIZONTAL INTERPOLATION:
#interpolate curve based on target altezza vector for the combo:
def interpolate_curve(altezza_combo, altezza, forza):
    '''
    Aligns horizontally both the forza and altezza vectors on the basis of a "stamp",
    represented by the target altezza vector for a combo(taglia, id_comp).
    The target altezza vector has a standard number of points based on a predefined sample rate.

    NOTE:
    Function query_tgt_vectors() must be called before this, to get a altezza_combo vector to pass here.
    Example:
    _, _, altezza_combo = query_tgtvectors(taglia, id_comp)

    params: (list) target vector for a combo(taglia, altezza):,
            (list) orig altezza vector:,
            (list) orig forza vector.
    returns:
            (list) target altezza vector:,
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

    return altezza_combo, new_forza
