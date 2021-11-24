import sys, logging, os
import pandas as pd
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.db_connect import db_connect, db_disconnect
from matplotlib import pyplot as plt 


# Connect
cnxn, cursor = db_connect()
timestamp = 1584106927

query = "SELECT PressateData.Timestamp, Pressate.ComboID, PressateData.Forza, PressateData.Altezza FROM PressateData INNER JOIN Pressate ON PressateData.Timestamp = Pressate.Timestamp WHERE PressateData.Timestamp = "+str(timestamp)
PressataData = pd.read_sql(query, cnxn)
print(PressataData)
comboid = str(PressataData['ComboID'].iloc[0])
altezza = PressataData['Altezza'].tolist()
forza = PressataData['Forza'].tolist()

query = "SELECT ComboID, TargetMA, TargetMF FROM Combos WHERE ComboID = '"+comboid+"'"
Combo = pd.read_sql(query, cnxn)
target_ma = float(Combo['TargetMA'].iloc[0])

fout = os.getcwd()+"/output/"+str(timestamp)+"_altezzaorig.png"
plt.plot(altezza, color='red', linewidth=2)
plt.title("ALTEZZA_ORIG", fontsize='small')
plt.savefig(fout)

plt.clf()
fout = os.getcwd()+"/output/"+str(timestamp)+"_forzaorig.png"
plt.plot(forza, color='red', linewidth=2)
plt.title("FORZA_ORIG", fontsize='small')
plt.savefig(fout)

plt.clf()
fout = os.getcwd()+"/output/"+str(timestamp)+"_FULL_ORIG.png"
plt.plot(altezza, forza, color='orange', linewidth=2)
plt.title("FULL_ORIG", fontsize='small')
plt.savefig(fout)

#flatten the portion of interest of curves:
def slice_curves(target_ma, altezza, forza):
    #vars:
    indices = []
    altezza_corr = []
    forza_corr = []
    max_p = 0

    #get indices of points of altezza curve in which it grows monotonically:
    for p in altezza[1:]:
        if p >= MIN_ALTEZZA and p <= target_ma:
            if p > (p-1) and p > max_p:
                max_p = p
                indices.append(altezza.index(p))

    #use the extracted indices to get a corrected version of the Pressata's altezza and forza curves:
    for ind in indices:
        altezza_corr.append(altezza[ind])
        forza_corr.append(forza[ind])

    return altezza_corr, forza_corr


altezza, forza = slice_curves(target_ma, altezza, forza)

fout = os.getcwd()+"/output/"+str(timestamp)+"_altezza.png"
plt.clf()
plt.plot(altezza, color='blue', linewidth=2)
plt.title("ALTEZZA_MONOT", fontsize='small')
plt.savefig(fout)

plt.clf()
fout = os.getcwd()+"/output/"+str(timestamp)+"_forza.png"
plt.plot(forza, color='blue', linewidth=2)
plt.title("FORZA_MONOT", fontsize='small')
plt.savefig(fout)

plt.clf()
fout = os.getcwd()+"/output/"+str(timestamp)+"_FULL.png"
plt.plot(altezza, forza, color='green', linewidth=2)
plt.title("FULL_MONOT", fontsize='small')
plt.savefig(fout)

# Disconnect
db_disconnect(cnxn, cursor)
