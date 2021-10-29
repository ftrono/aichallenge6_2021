import warnings
from utils import mongo_connect, mongo_disconnect
from access_db import query_bycombo, query_tgtvectors
import matplotlib.pyplot as plt
import warnings

#HORIZONTAL INTERPOLATION:
#interpolate curve based on target altezza vector for the combo:
def interpolate_curve(taglia, idcomp, altezza, forza):
    #objects:
    new_forza = []
    i = 0
    v = 0

    #get target vector for (taglia, idcomp):
    _, _, tgt_h = query_tgtvectors(taglia, idcomp)
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

#MAIN:
def trial():
    #combos tested:
    #"MP080", "a0215"
    #"MP080", "a0206"
    #"MP080", "a0211"
    #"MP060", "a0007"
    combo = query_bycombo(taglia="MP080", idcomp="a0206")
    altezza = combo.series[0].altezza
    forza = combo.series[0].forza

    #trial3(tgt_altezza, altezza, forza)
    tgth, newf = interpolate_curve("MP080", "a0206", altezza, forza)
    print(tgth)
    print(newf)
    print(len(tgth), len(newf))

    #PLOT:
    plt.plot(altezza, forza, linewidth = 4)
    plt.plot(tgth, newf, linewidth=2)
    plt.show()

#MAIN:
#trial()
