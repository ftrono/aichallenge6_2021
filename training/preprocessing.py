import sys, logging, os, time, math
import pandas as pd
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.db_connect import db_connect, db_disconnect, pd_db_connect
from database_functions.db_tools import empty_table, reset_marks
from evaluation.eval_tools import evaluate_ma, evaluate_anomalous
from database_functions.extract_data import Collector
import sqlalchemy as sa

#PART II.A) PREPROCESSING:
#Start populating Combos and Warnings tables.
# - set TargetMA and StdMA for every ComboID;
# - immediately flag all Pressate not reaching TargetMA (if enabled and with a sigma) or with an anomalous height start, to exclude them from training;
# - also flag riduttori that have an anomalous number of Pressate for each component.


def preprocessing():
    '''
    1) Preprocessing part:
    - resets Warnings table
    - learn TargetMA and StdMA for all Combos
    - exclude wrong pressate by MA (below cutoff and, only if enabled in globals, vs TargetMA)
    - exclude wrong pressate with anomalous height series for original trajectory (included original series length)
    - flag riduttori if incorrect number of pressate of same id_comps
    '''
    # Connect
    engine = pd_db_connect()
    cnxn, cursor = db_connect()

    #INIT:
    # Set logger:
    log=logging.getLogger('preprocessing')
    hdl=logging.FileHandler('./logs/preprocessing.log',mode='w')
    hdl.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    log.setLevel(logging.DEBUG)
    log.addHandler(hdl)

    start_time = time.time()

    #logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    log.info("Preprocessing STARTED.")
    print("Preprocessing STARTED.")

    #DB tools:
    dbt = {'cnxn': cnxn, 'cursor': cursor, 'logging': log}

    #0) Reset tables:
    #Warnings table:
    empty_table(dbt, tablename="Warnings")
    log.info("Warnings table emptied.")

    #Evaluated marks:
    reset_marks(dbt, remark=False)
    with engine.begin() as conn:
        #1) Extract full Pressate table into memory:
        log.info("Extracting needed tables from SQL DB...")
        query = sa.text("SELECT Timestamp, RiduttoreID, ComboID, MaxForza, MaxAltezza FROM Pressate")
        Pressate = pd.read_sql(query, conn)
        tot_pressate = len(Pressate['Timestamp'].tolist())
        log.info("Extracted table 1/2 (Pressate).")
        
        #PressateData:
        query = sa.text("SELECT Timestamp, Altezza FROM PressateData")
        PressateData = pd.read_sql(query, conn)
        log.info("Extracted table 2/2 (PressateData)...")

    #2) Extract all ComboIDs:
    combos_list = Pressate['ComboID'].unique().tolist()

    #accumulation lists:
    sets_targets = []
    sets_warnings = []
    sets_eval = []
    tot_cnt = 0
    db_error = False


    #2) PREPROCESS:
    #For each ComboID:
    for comboid in combos_list:

        #INIT:
        #init target Collector:
        target = Collector()
        target.comboid = str(comboid)
        cnt = 0

        log.info("ComboID {}: preprocessing started.".format(comboid))

        #extract portion of Pressate table only with the current ComboID:
        log.debug("ComboID {}: initializing data for preprocessing...".format(comboid))
        query = 'ComboID == "'+comboid+'"'
        PressateCombo = Pressate.query(query)
        tot_4combo = len(PressateCombo['Timestamp'].tolist())
        #remove this portion from the original Pressate table (to save memory):
        Pressate = Pressate[~Pressate.Timestamp.isin(PressateCombo.Timestamp)]


        #PREPROCESS:
        #1) Get TargetMA and StdMA for the Combo:
        target.ma = float(PressateCombo['MaxAltezza'].mean())
        try:
            target.std_ma = float(PressateCombo['MaxAltezza'].std()) + 1
        except:
            target.std_ma = 1
        if math.isnan(target.std_ma) == True:
            target.std_ma = 1
        log.debug("ComboID {}: TargetMA and StdMA generated".format(comboid))
        
        #2) Accumulate TargetMA and StdMA for later store:
        sets_targets.append((target.ma, target.std_ma, target.comboid))

        #3) Dataset cleaning:
        log.debug("ComboID {}: evaluating {} Pressate for preprocessing...".format(comboid, tot_4combo))
        #Flag wrong curves for MA:
        for row in PressateCombo.index:
            #init current Collector:
            current = Collector()
            current.timestamp = int(PressateCombo['Timestamp'][row])
            current.riduttoreid = int(PressateCombo['RiduttoreID'][row])
            current.ma = float(PressateCombo['MaxAltezza'][row])
            wid = 0

            #check MaxAltezza (will check for cutoff point and, only if enabled, for TargetMA):
            wid, _ = evaluate_ma(log, current, target)
            if wid != 0:
                cnt = cnt+1
                #accumulate warnings (WID 1: MaxAltezza out of range):
                sets_warnings.append((current.riduttoreid, current.timestamp, wid))
                sets_eval.append((1, current.timestamp))
            
            if wid == 0:
                #check anomalous curve:
                current.altezza = PressateData[PressateData['Timestamp'] == current.timestamp]['Altezza'].tolist()
                wid = evaluate_anomalous(log, current, target, trajectory=True)
                if wid != 0:
                    cnt = cnt+1
                    #accumulate warnings (WID 2: anomalous height curve):
                    sets_warnings.append((current.riduttoreid, current.timestamp, wid))
                    sets_eval.append((1, current.timestamp))

        #4) End statistics:
        tot_cnt = tot_cnt + cnt
        log.info("ComboID {}: preprocessing complete. Found {} Pressate to be flagged out of {}.".format(comboid, cnt, tot_4combo))


    #3) BULK STORE:
    #Bulk store all accumulated TargetMA and StdMA to SQL DB:
    try:
        cursor.fast_executemany = True
        cursor.executemany("UPDATE Combos SET TargetMA = ?, StdMA = ? WHERE ComboID = ?", sets_targets)
        cnxn.commit()
        log.info("Stored TargetMA and StdMA for all Combos into DB.")
        print("Stored TargetMA and StdMA for all Combos into DB.")
    except:
        db_error = True
        log.error("Insert error: TargetMA and StdMA not stored to DB. Please relaunch Preprocessing.")
        print("Insert error: TargetMA and StdMA not stored to DB. Please relaunch Preprocessing.")

    #Bulk store all accumulated warnings to SQL DB:
    try:
        cursor.fast_executemany = True
        cursor.executemany("INSERT INTO Warnings (RiduttoreID, Timestamp, WarningID) VALUES (?, ?, ?)", sets_warnings)
        cnxn.commit()
        log.info("Stored all warnings found into DB.")
        print("Stored all warnings found into DB.")
    except:
        db_error = True
        log.error("Insert error: warnings not stored to DB. Please relaunch Preprocessing.")
        print("Insert error: warnings not stored to DB. Please relaunch Preprocessing.")

    #Bulk store all accumulated booleans for Pressate to SQL DB:
    try:
        cursor.fast_executemany = True
        cursor.executemany("UPDATE Pressate SET Evaluated = ? WHERE Timestamp = ?", sets_eval)
        cnxn.commit()
        log.info("Stored Evaluated marks for flagged Pressate into DB.")
        print("Stored Evaluated marks for flagged Pressate into DB.")
    except:
        db_error = True
        log.error("Insert error: Evaluated marks not stored to DB. Please relaunch Preprocessing.")
        print("Insert error: Evaluated marks not stored to DB. Please relaunch Preprocessing.")

    #END:
    db_disconnect(cnxn, cursor)
    end_time = time.time()

    if CHECK_MA == True:
        ma_str = ", with sigma MA "+str(SIGMA_MA)
    else:
        ma_str = ""

    #FINAL LOG:
    if db_error == False:
        message = "Preprocessing COMPLETED in {} seconds! Flagged {} anomalous Pressate out of {}{}.".format(round((end_time-start_time),2), tot_cnt, tot_pressate, ma_str)
        log.info(message)
        print(message)
        return 0
    else:
        message = "Preprocessing COMPLETED in {} seconds. Error in storing data to the DB: please relaunch Preprocessing. Found {} Pressate to be flagged out of {}{}.".format(round((end_time-start_time),2), tot_cnt, tot_pressate, ma_str)
        log.info(message)
        print(message)
        return -1
