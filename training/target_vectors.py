from datetime import time
import numpy as np
from training_tools import train_curve

#GENERATE TARGET HEIGHT VECTORS FOR COMBOS:
# - (helper) compute_rate(orig_altezza)
# - generate_hvectors(cnxn, cursor, logging)

#helper: compute sample_rate for a pressata:
def compute_rate(orig_altezza):
    #get vector of differences:
    diff_vector=np.diff(orig_altezza)
    diff_vector=np.absolute(diff_vector)
    diff_vector=np.round(diff_vector,2)
    #compute max freq:
    unique, counts = np.unique(diff_vector, return_counts=True)
    max_index_col = np.argmax(counts, axis=0) #max freq
    sample_rate = unique[max_index_col]
    return sample_rate


#generate target height vector for a comboid:
def generate_hvector(dbt, timestamps, target_ma):
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logging = dbt['logging']
    timestamps = []
    rates = []

    #2) for each timestamp:
    for t in timestamps:
        cur_altezza = []
        #extract original altezza curve:
        cursor.execute("SELECT Altezza FROM PressateData WHERE Timestamp = ?", t)
        for tup in cursor.fetchall():
            cur_altezza.append(float(tup[0]))
        #store sample rate for the current pressata:
        rates.append(compute_rate(cur_altezza))
        logging.debug("Calculated sample_rate for timestamp {}".format(t))

    #3) get target sample rate:
    unique, counts = np.unique(rates, return_counts=True)
    max_index_col = np.argmax(counts, axis=0)
    tgt_rate = unique[max_index_col]
    #tgt_rate correction (to allow integer division):
    rangelen = int(target_ma // tgt_rate)
    tgt_rate = target_ma / rangelen
    altezza_combo = []

    #4) compute target h vector:
    for i in range(rangelen):
        altezza_combo.append(tgt_rate*(i+1))
    logging.debug("Target Altezza vector ready to store")
    return altezza_combo


def train_vectors(dbt, comboid, target_ma, timestamps):
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logging = dbt['logging']
    
    #1) Target height vector:
    altezza_combo = generate_hvector(dbt, timestamps, target_ma)
    logging.debug("Target Altezza vector calculated for ComboID {}".format(comboid))

    #2) Target Forza curve and Std_curve:
    forza_combo, std_curve = train_curve(dbt, comboid, timestamps)
    logging.debug("Target Forza curve and std_curve generated for ComboID {}".format(comboid))

    #3) Store target curve parameters to DB (Combos & CombosData tables):
    dataList = []
    for ind in range(len(forza_combo)):
        dataList.append("("+str(comboid)+","+str(altezza_combo[ind])+","+str(forza_combo[ind])+")")
    #accumulate queries:
    try:
        cursor.execute("UPDATE Combos SET StdCurve = ? WHERE ComboID = ?", std_curve, str(comboid))
        cursor.execute("INSERT INTO CombosData (ComboID, Altezza, Forza) VALUES "+','.join(dataList))
    except:
        logging.warning("Insert error for targets of ComboID {}".format(comboid))

    #4) commit accumulated queries to DB:
    cnxn.commit()
    logging.debug("Stored target data and curves for ComboID {}".format(comboid))
    return 0
