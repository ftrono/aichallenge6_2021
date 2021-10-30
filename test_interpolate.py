import matplotlib.pyplot as plt
from access_db import query_bycombo
from utils import interpolate_curve

#____________________________________________________________________________
#NOTE:
#This is just a test module for the interpolate_curves() function.
#The actual function is available in utils.py
#____________________________________________________________________________


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
