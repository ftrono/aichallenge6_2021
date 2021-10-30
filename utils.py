import datetime, pymongo, warnings
import matplotlib.pyplot as plt

CONNECTION_STRING="mongodb://localhost:27017/" #to executing locally
#CONNECTION_STRING="mongodb://team6:MLoMuk2b@hitvmiac-06.northeurope.cloudapp.azure.com:27017" #for executing on the Azure VM
#CONNECTION_STRING="mongodb://team6:MLoMuk2b@localhost:27017" #for executing on the Azure VM


#COMMON UTILITY FUNCTIONS:

#CSV name parser:
def name_parser(name): # take as input the file name
    # get information from file name
    tempcode=name[0:14]
    id=name[14:19]
    stazione=name[21:23]
    date_time=datetime.datetime(int(name[24:28]), int(name[29:31]), int(name[32:34]),int(name[35:37]),int(name[38:40]),int(name[41:43])) # convert string to date obj
    timestamp=datetime.datetime.timestamp(date_time) # convert date object to timestamp
    return tempcode,id,stazione,timestamp

#Mongo utils:
def mongo_connect():
    client = pymongo.MongoClient(CONNECTION_STRING)
    db = client.novotic
    return db, client

def mongo_disconnect(client):
    client.close()


#FULL (AFTER EVALUATE): visualize ideal curve, boundaries & current curve:
def plot_curves(curva_ideale, avg_var, tgt_h, cur_forza):
    #calculate upper & lower bound:
    ci_boundup = [(curva_ideale[i]+avg_var) for i in range(len(curva_ideale))]
    ci_boundlow = [(curva_ideale[i]-avg_var) for i in range(len(curva_ideale))]

    #plot:
    plt.plot(tgt_h, curva_ideale, color='green', linewidth=4, label="Ideal curve")
    plt.plot(tgt_h, ci_boundup, color='orange', linestyle='--', linewidth=1, label="Upper boundary")
    plt.plot(tgt_h, ci_boundlow, color='red', linestyle='--', linewidth=1, label="Lower boundary")
    plt.plot(tgt_h, cur_forza, color='blue', linewidth=2, label="CURRENT CURVE")
    plt.xlabel('Altezza (mm)')
    plt.ylabel('Forza (kN)')
    plt.legend(fontsize='x-small', frameon=False)
    
    plt.show()

    return 0


#BASIC: plot a single series:
def plot_series(id, x, y, **title):
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
def normalize(array, plot=False):
    '''
    Takes an array as input, returns the same array with normalized values for `altezza` and `forza`.
    Plotting and Resizing features on request.
    :param array: array of numbers in the form [float1, float2, ... , floatN] or [int1, int2, ... , intN]
    :param size: Size you want the array to be resized to. (length)
    :return: normalized array & plot of the array if requested
    '''
    x_data = array['altezza']
    y_data = array['forza']
    lenx = len(x_data)
    leny = len(y_data)

    # Handling error for discordant lenghts for 'altezza' and 'forza'
    if lenx != leny:
        raise Warning('Illegal values! The number of elements for x axis and y axis should coincide.'
                      f'Instead you provided {lenx}, and {leny}, respectively!')

    # Strength data normalization
    # leaving x data untouched
    norm_ydata = [round(i/max(y_data), 4) for i in y_data]

    # Creating normalized array to preserve original
    normie = array
    normie['forza'] = norm_ydata

    # Plotting (optional)
    if plot == True:
        label = normie['id']
        plt.plot(normie, norm_ydata)
        plt.xlabel(label)
        graph = plt.show()
        return graph

    return normie


#HORIZONTAL INTERPOLATION:
#interpolate curve based on target altezza vector for the combo:
def interpolate_curve(tgt_h, altezza, forza):
    '''
    Aligns horizontally both the forza and altezza vectors on the basis of a "stamp",
    represented by the target altezza vector for a combo(taglia, idcomp).
    The target altezza vector has a standard number of points based on a predefined sample rate.

    NOTE:
    Function query_tgt_vectors() must be called before this, to get a tgt_h vector to pass here.
    Example:
    _, _, tgt_h = query_tgtvectors(taglia, idcomp)

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
    tgt_len = len(tgt_h)

    if altezza == [] or tgt_h == []:
        return warnings.warn("Error: empty list.")

    #1) initial padding:
    if altezza[0] > tgt_h[0]:
        while tgt_h[i] < altezza[0]:
            #pad:
            new_forza.append(0)
            i = i+1

    #2) interpolate values:
    for i in range(i, tgt_len):
        #pad check:
        if v < len(altezza):
            #find closest value of tgt_h[i] in orig altezza list:
            #the loop will stop at the last index (v) in which the value of altezza is before (or equal to) the value of tgt_h[i]:
            while (altezza[v] < tgt_h[i]):
                #go to next:
                v = v+1
                #check end of orig list:
                if v >= len(altezza):
                    #ending padding:
                    new_forza.append(0)
                    break
            
            if v < len(altezza):
                #calculate interpolated value:
                if altezza[v] == tgt_h[i]:
                    #if equal, save same:
                    new_forza.append(forza[v])
                else:
                    #INTERPOLATE:
                    #indices:
                    left = v-1
                    right = v

                    dx = altezza[right]-altezza[left]
                    xgap = altezza[right]-tgt_h[i]
                    dy = forza[right]-forza[left]
                    #xgap:dx=ygap:dy
                    ygap = (xgap*dy)/dx

                    #calculate:
                    new_forza.append(round((forza[right]-ygap),2))
                    
                    #print("Altezza: {}, {}, {}".format(altezza[left], altezza[right], tgt_h[i]))
                    #print("Forza: {}, {}, {}".format(forza[left], forza[right], new_forza[i]))
        
        else:
            #3) Ending padding:
            new_forza.append(0)

    return tgt_h, new_forza
