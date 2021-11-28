import sys, os
import matplotlib.pyplot as plt
sys.path.insert(0, os.getcwd())
from globals import *


#VISUALIZATION FUNCTION
#Visualize ideal curve, boundaries & current curve:
def visualize(current, target, wid=0, count_out=0, window=WINDOW, save=SAVE_PNG):
    #title and filename:
    if count_out != 0:
        co = " - Points out: "+str(count_out)
    else:
        co = ""
    title = "ComboID: "+str(current.comboid)+" - Timestamp: "+str(current.timestamp)+" - WID: "+str(wid)+co
    fout = OUTPUT_PATH+"/curves/"+str(current.comboid)+"_"+str(current.timestamp)+"_wid"+str(wid)+".png"

    #title color:
    if wid == 0:
        titcolor = 'green'
    else:
        titcolor = 'firebrick'

    #plot:
    plt.clf()
    plt.plot(target.altezza, target.forza, color='limegreen', linewidth=4, label="Ideal curve")
    plt.plot(target.altezza, target.boundup, color='orange', linestyle='--', linewidth=1, label="Upper boundary")
    plt.plot(target.altezza, target.boundlow, color='red', linestyle='--', linewidth=1, label="Lower boundary")
    plt.plot(target.altezza, current.forza, color='blue', linewidth=2, label="CURRENT CURVE")
    plt.xlabel('Altezza (mm)')
    plt.ylabel('Forza (kN)')
    plt.legend(fontsize='x-small', frameon=False)
    plt.title(title, fontsize='small', fontweight='bold', color=titcolor)
    if save == True:
        plt.savefig(fout)
    if window == True:
        plt.show()
    return 0
