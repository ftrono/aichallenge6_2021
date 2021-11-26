import sys, logging, os
import pandas as pd
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.db_connect import db_connect, db_disconnect
from training_tools import slice_curves, interpolate_curve
from matplotlib import pyplot as plt 


# Connect
cnxn, cursor = db_connect()
timestamp = 1584549915

query = "SELECT PressateData.Timestamp, Pressate.ComboID, PressateData.Forza, PressateData.Altezza FROM PressateData INNER JOIN Pressate ON PressateData.Timestamp = Pressate.Timestamp WHERE PressateData.Timestamp = "+str(timestamp)
PressataData = pd.read_sql(query, cnxn)
#print(PressataData)
comboid = str(PressataData['ComboID'].iloc[0])
altezza = PressataData['Altezza'].tolist()
forza = PressataData['Forza'].tolist()
print(len(altezza))
print(altezza.index(max(altezza)))

query = "SELECT ComboID, TargetMA, TargetMF, StdMA FROM Combos WHERE ComboID = '"+comboid+"'"
Combo = pd.read_sql(query, cnxn)
target_ma = float(Combo['TargetMA'].iloc[0])
std_ma = float(Combo['StdMA'].iloc[0])
#target_ma = target_ma + (std_ma * SIGMA_MA)

query = "SELECT Altezza FROM CombosData WHERE ComboID = '"+comboid+"'"
altezza_combo = pd.read_sql(query, cnxn)
altezza_combo = altezza_combo['Altezza'].tolist()


fout = os.getcwd()+"/output/"+str(timestamp)+"_altezzaorig.png"
plt.figure(dpi=200)
plt.plot(altezza, color='red', linewidth=2)
plt.title("ALTEZZA_ORIG", fontsize='small')
plt.savefig(fout)

plt.clf()
fout = os.getcwd()+"/output/"+str(timestamp)+"_forzaorig.png"
plt.figure(dpi=200)
plt.plot(forza, color='red', linewidth=2)
plt.title("FORZA_ORIG", fontsize='small')
plt.savefig(fout)

plt.clf()
fout = os.getcwd()+"/output/"+str(timestamp)+"_FULL_ORIG.png"
plt.figure(dpi=200)
plt.plot(altezza, forza, color='orange', linewidth=2)
plt.title("FULL_ORIG", fontsize='small')
plt.savefig(fout)

plt.clf()
fout = os.getcwd()+"/output/"+str(timestamp)+"_FULL_ORIG_CUT.png"
plt.figure(dpi=200)
plt.plot(altezza[50:121], forza[50:121], color='orange', linewidth=2)
plt.title("FULL_ORIG_CUT", fontsize='small')
plt.savefig(fout)


altezza, forza = slice_curves(altezza_combo, altezza, forza)
forza = interpolate_curve(altezza_combo, altezza, forza)

fout = os.getcwd()+"/output/"+str(timestamp)+"_altezza.png"
plt.clf()
plt.figure(dpi=200)
plt.plot(altezza, color='blue', linewidth=2)
plt.title("ALTEZZA_MONOT", fontsize='small')
plt.savefig(fout)

plt.clf()
fout = os.getcwd()+"/output/"+str(timestamp)+"_forza.png"
plt.figure(dpi=200)
plt.plot(forza, color='blue', linewidth=2)
plt.title("FORZA_MONOT", fontsize='small')
plt.savefig(fout)

print(len(altezza_combo))
print(altezza_combo.index(max(altezza_combo)))

plt.clf()
fout = os.getcwd()+"/output/"+str(timestamp)+"_FULL.png"
plt.figure(dpi=200)
plt.plot(altezza_combo, forza, color='green', linewidth=2)
plt.title("FULL_MONOT", fontsize='small')
plt.savefig(fout)

plt.clf()
fout = os.getcwd()+"/output/"+str(timestamp)+"_FULL_CUT.png"
plt.figure(dpi=200)
plt.plot(altezza_combo[-7:-1], forza[-7:-1], color='green', linewidth=2)
plt.title("FULL_MONOT_CUT", fontsize='small')
plt.savefig(fout)

# Disconnect
db_disconnect(cnxn, cursor)
