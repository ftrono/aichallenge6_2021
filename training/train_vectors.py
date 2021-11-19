import sys, logging, statistics,os
import numpy as np
import pandas as pd
sys.path.insert(0, os.getcwd())
from globals import *
from utils import interpolate_curve
from training.training_tools import compute_rate, ideal_curve, stdev_curve

#GENERATE TARGET VECTORS FOR A COMBOID:
# - generate_hvec() #for height
# - generate_hcur() #for force
# - train_vectors() 


#generate target height vector for a comboid:
def generate_hvec(dbt, timestamps, target_ma):
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logging = dbt['logging']
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


#generate ideal force curve for a comboid:
def generate_hcur(dbt, comboid, timestamps, altezza_combo):
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logging = dbt['logging']
    batch_forces = []
    logging.debug("Started modeling ComboID {}".format(comboid))

    #2) for each timestamp:
    for t in timestamps:
        logging.debug("Modeling Pressata {} for ComboID {}".format(t, comboid))
        #extract original curves (forza and altezza):
        query = "SELECT Altezza, Forza FROM PressateData WHERE Timestamp="+str(t)
        #store to Pandas dataframe
        df = pd.read_sql(query, cnxn)
        #extract data:
        cur_altezza = list(df['Altezza'].to_numpy())
        cur_forza = list(df['Forza'].to_numpy())

        #interpolate force curve:
        itp_forza = interpolate_curve(altezza_combo, cur_altezza, cur_forza)

        #store to batch list for the current ComboID:
        batch_forces.append(itp_forza)
        
    #3) get target curve parameters for the combo (batch_standardize):
    logging.debug("Training final curve parameters for ComboID {}".format(comboid))
    forza_combo = ideal_curve(batch_forces)
    std_list = stdev_curve(batch_forces)
    logging.debug("Successfully modeled ComboID {}".format(comboid))
    return forza_combo, std_list


#JOINT: generate target height vector & ideal force curve for a ComboID:
def train_vectors(dbt, comboid, target_ma, timestamps):
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logging = dbt['logging']

    if len(timestamps) == 0:
        logging.error("ComboId {} is empty.")
        raise
    elif len(timestamps) == 1:
        logging.warning("ComboId {} only has 1 Pressata: its original curves will be now saved as targets.")
         #extract original curves (forza and altezza):
        query = "SELECT Altezza, Forza FROM PressateData WHERE Timestamp="+str(timestamps[0])
        #store to Pandas dataframe
        df = pd.read_sql(query, cnxn)
        #extract data:
        altezza_combo = list(df['Altezza'].to_numpy())
        forza_combo = list(df['Forza'].to_numpy())
        std_list = [0 for i in forza_combo] #empty std_list vector
        std_curve_avg = statistics.stdev(forza_combo)
    else:
        #1) Target height vector:
        altezza_combo = generate_hvec(dbt, timestamps, target_ma)
        logging.debug("Target Altezza vector calculated for ComboID {}".format(comboid))

        #2) Target Forza curve and Std_curve:
        forza_combo, std_list = generate_hcur(dbt, comboid, timestamps, altezza_combo)
        std_curve_avg = statistics.mean(std_list)
        logging.debug("Target Forza curve and std_curve generated for ComboID {}".format(comboid))

    #3) Store target curve parameters to DB (Combos & CombosData tables):
    dataList = []
    for ind in range(len(forza_combo)):
        dataList.append("('"+str(comboid)+"',"+str(altezza_combo[ind])+","+str(forza_combo[ind])+","+str(std_list[ind])+")")
    #accumulate queries:
    try:
        cursor.execute("UPDATE Combos SET StdCurveAvg = ? WHERE ComboID = ?", std_curve_avg, str(comboid))
        #batch_insert:
        pr_i = 0
        if len(dataList) < 1000:
            new_i = len(dataList)
        else:
            new_i = 1000
        while new_i <= len(dataList):
            cursor.execute("INSERT INTO CombosData (ComboID, Altezza, Forza, Std) VALUES "+','.join(dataList[pr_i:new_i]))
            pr_i = new_i
            new_i = new_i+1000
    except:
        logging.warning("Insert error for targets of ComboID {}".format(comboid))
        raise

    #4) commit accumulated queries to DB:
    cnxn.commit()
    logging.debug("Stored target data and curves for ComboID {}".format(comboid))
    return 0
