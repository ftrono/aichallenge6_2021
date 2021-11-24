import sys, logging, os, time, statistics
from numpy.core.numeric import full
import pandas as pd
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.db_connect import db_connect, db_disconnect
from database_functions.db_tools import reset_table
from database_functions.extract_data import Collector
from training.training_tools import compute_rate, generate_hvec, slice_curves, interpolate_curve, ideal_curve, stdev_curve
from evaluation.eval_tools import evaluate_full

#TRAINING:
#Complete population of the Combos, CombosData and Warnings tables.
# - set TargetMF and StdMF for every ComboID;
# - learn target curves (altezza_combo, forza_combo and points_std) for every ComboID;
# - evaluate all Pressate in the DB and flag those not reaching TargetMF (with a sigma) and with anomalous curves.


def train(epoch):
    '''
    2) Training part:
    - resets CombosData table (curves learnt previously)
    - for each epoch:
        - learn TargetMF and StdMF for all Combos
        - for each ComboID:
            - get list of Pressate with no warnings
            - train target vectors for the Combo (target height vector, ideal force curve and points stdev vector)
            - store Combos target parameters
            - evaluate all Pressate in the combo and flag the warnings found
    '''
    # Connect
    cnxn, cursor = db_connect()
    e = epoch+1

    #INIT:
    # Set logger:
    log=logging.getLogger('training')
    filename = './logs/training_epoch'+str(e)+'.log'
    hdl=logging.FileHandler(filename,mode='w')
    hdl.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    log.setLevel(logging.INFO)
    log.addHandler(hdl)

    start_time = time.time()
    
    #logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    log.info("Epoch {}: Training STARTED".format(e))
    print("Epoch {}: Training STARTED".format(e))

    #DB tools:
    dbt = {'cnxn': cnxn, 'cursor': cursor, 'logging': log}

    #accumulation lists:
    sets_curves = []
    sets_warnings = []
    tot_cnt = 0

    #0) Reset learned CombosData table:
    reset_table(dbt, tablename="CombosData")
    log.info("CombosData table reset")

    #1) Extract ALL needed tables into memory (only timestamps with no warnings):
    #Pressate:
    log.info("Extracting tables from SQL DB...")
    query = "SELECT Pressate.Timestamp, Pressate.RiduttoreID, Pressate.ComboID, Pressate.MaxForza, Pressate.MaxAltezza FROM Pressate WHERE NOT EXISTS (SELECT Warnings.Timestamp FROM Warnings WHERE Warnings.Timestamp = Pressate.Timestamp)"
    Pressate = pd.read_sql(query, cnxn)
    tot_pressate = len(Pressate['Timestamp'].tolist())
    log.info("Extracted table 1/3 (Pressate)...")

    #PressateData:
    query = "SELECT PressateData.Timestamp, Pressate.ComboID, PressateData.Forza, PressateData.Altezza FROM PressateData INNER JOIN Pressate ON PressateData.Timestamp = Pressate.Timestamp WHERE NOT EXISTS (SELECT Warnings.Timestamp FROM Warnings WHERE Warnings.Timestamp = PressateData.Timestamp)"
    PressateData = pd.read_sql(query, cnxn)
    log.info("Extracted table 2/3 (PressateData)...")

    #Combos:
    query = "SELECT ComboID, TargetMA, TargetMF, StdMF, StdCurveAvg FROM Combos"
    Combos = pd.read_sql(query, cnxn)
    log.info("Extracted table 3/3 (Combos)...")
    #convert dataframe to lists:
    combos_list = Combos['ComboID'].tolist()
    tgtma_list = Combos['TargetMA'].tolist()
    del Combos
    
    log.info("Total number of Combos to train: {}".format(len(combos_list)))
    print("Total number of Combos to train: {}".format(len(combos_list)))

    #2) For each ComboID:
    for comboid in combos_list:
        #training accumulation lists:
        currents = []
        batch_heights = []
        batch_forces = []
        cnt = 0
        combo_start = time.time()

        #extract portion of Pressate table only with the current ComboID:
        log.info("NEW ComboID: {}. Extracting timestamps...".format(comboid))
        query = 'ComboID == "'+comboid+'"'
        PressateCombo = Pressate.query(query)
        #remove this portion from the original Pressate table (to save memory):
        rows = PressateCombo.index.values.tolist()
        Pressate.drop(rows, inplace=True)
        #list of clean Pressate:
        timestamps = PressateCombo['Timestamp'].tolist()

        #INIT CHECK:
        if len(timestamps) < MIN_PRESSATE:
            #skip ComboID:
            log.info("ComboID skipped {}, number of clean Pressate lower than {}".format(comboid, len(timestamps)))
            
        else:
            #TRAIN!
            log.info("Training {} Pressate for ComboID {}".format(len(timestamps), comboid))
            print("\nTraining {} Pressate for ComboID {}".format(len(timestamps), comboid))
            comboid4store = "'"+comboid+"'"


            #1) INIT:
            #init target Collector:
            target = Collector()
            target.comboid = str(comboid)
            target.ma = float(tgtma_list[combos_list.index(comboid)])

            log.info("ComboID: {}. Extracting original curves...".format(comboid))
            #extract portion of PressateData table related only to the current ComboID:
            PressateComboData = PressateData.query(query)
            #remove this portion from the original Pressate table (to save memory):
            rows = PressateComboData.index.values.tolist()
            PressateData.drop(rows, inplace=True)


            #2) LEARN:           
            #i) Populating Collectors for every Pressata:
            for i in range(len(timestamps)):
                #init target Collector:
                currents.append(Collector())
                currents[i].timestamp = timestamps[i]
                #getting Pressata:
                Pressata = PressateCombo[PressateCombo['Timestamp'] == timestamps[i]]
                #getting PressataData:
                PressataData = PressateComboData[PressateComboData['Timestamp'] == timestamps[i]]

                #populate Collector with Pressata's data:
                currents[i].comboid = comboid
                currents[i].mf = float(Pressata['MaxForza'].iloc[0])
                currents[i].ma = float(Pressata['MaxAltezza'].iloc[0])
                currents[i].riduttoreid = int(Pressata['RiduttoreID'].iloc[0])
                currents[i].altezza = PressataData['Altezza'].tolist()
                batch_heights.append(currents[i].altezza)
                currents[i].forza = PressataData['Forza'].tolist()
                log.info("ComboID: {}. Collectors ready".format(comboid))
            
            #clean memory:
            del Pressata
            del PressataData


            #ii) Learn the target vectors & parameters for the Combo:
            # Target altezza vector:
            sample_rate = compute_rate(batch_heights)
            target.altezza = generate_hvec(sample_rate, MIN_ALTEZZA, target.ma)
            log.info("ComboID: {}. Learned target Altezza vector".format(comboid))
            del batch_heights

            # Slice & interpolate original curves:
            for current in currents:
                #i) slice portions of interest of original curves:
                current.altezza, current.forza = slice_curves(target.ma, current.altezza, current.forza)
                #ii) interpolate force curve:
                current.forza = interpolate_curve(target.altezza, current.altezza, current.forza)
                batch_forces.append(current.forza)
            log.info("ComboID: {}. Sliced and interpolated original curves in all Collectors".format(comboid))


            #iii) Learn the target Forza curve and Std_curve for the Combo:
            target.forza = ideal_curve(batch_forces)
            target.std = stdev_curve(batch_forces)
            target.std_curve_avg = float(statistics.mean(target.std))
            del batch_forces
            log.info("ComboID {}. Target Forza curve and std_curve generated".format(comboid))

            #accumulate every index in target lists:
            for i in range(len(target.altezza)):
                sets_curves.append((comboid, float(target.altezza[i]), float(target.forza[i]), float(target.std[i])))


            #iv) Learn TargetMF and StdMF for the Combo:
            target.mf = float(PressateCombo['MaxForza'].mean())
            try:
                target.std_mf = float(PressateCombo['MaxForza'].std()) + 1
            except:
                target.std_mf = 1


            #3) BULK STORE LEARNED PARAMETERS AND CURVES TO SQL DB:
            #Store TargetMF, StdMF and StdCurveAvg:
            print(target.mf, target.std_mf, target.std_curve_avg, comboid4store)
            print(sets_curves[0])
            try:
                cursor.execute("UPDATE Combos SET TargetMF = ?, StdMF = ?, StdCurveAvg = ? WHERE ComboID = ?", float(target.mf), float(target.std_mf), float(target.std_curve_avg), comboid4store)
                cnxn.commit()
                log.info("ComboID {}: Successfully stored TargetMF, StdMF and StdCurveAvg into DB.".format(comboid))
                print("ComboID {}: Successfully stored TargetMF, StdMF and StdCurveAvg into DB.".format(comboid))
            except:
                log.error("ComboID {}: Insert error: TargetMF, StdMF and StdCurveAvg not stored to DB. Please retry later.".format(comboid))
                print("ComboID {}: Insert error: TargetMF, StdMF and StdCurveAvg not stored to DB. Please retry later.".format(comboid))

            #Bulk store target curves (index by index):
            try:
                cursor.fast_executemany = True
                cursor.executemany("INSERT INTO CombosData (ComboID, Altezza, Forza, Std) VALUES (?, ?, ?, ?)", sets_curves)
                cnxn.commit()
                log.info("ComboID {}: Successfully stored target curves into DB.".format(comboid))
                print("ComboID {}: Successfully stored target curves into DB.".format(comboid))
            except:
                log.error("ComboID {}: Insert error: target curves not stored to DB. Please retry later.".format(comboid))
                print("ComboID {}: Insert error: target curves not stored to DB. Please retry later.".format(comboid))
            
            #reset accumulation list:
            sets_curves = []


            #4) EVALUATE:
            #Evaluate all the Pressate ("current" Collectors) extracted for the ComboID:
            log.info("ComboID {}. Evaluating {} Pressate".format(comboid, len(timestamps)))
            print("ComboID {}. Evaluating {} Pressate".format(comboid, len(timestamps)))
            for i in range(len(currents)):
                #status update:
                pstr = "ComboID "+str(comboid)+": evaluating Pressata "+str(i+1)+"/"+str(len(currents))
                print(pstr, end = "                                          \r")
                #Evaluate current Pressata:
                wid = evaluate_full(log, currents[i], target, preprocessed=True, visual=False)
                if wid != 0:
                    cnt = cnt+1
                    #accumulate warnings:
                    sets_warnings.append((currents[i].riduttoreid, currents[i].timestamp, wid))
                    #log:
                    log.warning("ComboID: {}. Timestamp {}: warning found. To be flagged with WID #{}.".format(comboid, currents[i].timestamp, wid))
                else:
                    log.debug("ComboID: {}. Timestamp {}: OK".format(comboid, currents[i].timestamp))
            

            #4) END STATISTICS:
            combo_end = time.time()
            tot_cnt = tot_cnt + cnt
            log.info("ComboID {}: training completed in {} seconds. Flagged {} Pressate out of {}.".format(comboid, round((combo_end-combo_start),2), cnt, len(timestamps)))
            print("\nComboID {}: training completed in {} seconds. Flagged {} Pressate out of {}.".format(comboid, round((combo_end-combo_start),2), cnt, len(timestamps)))


    #3) BULK STORE WARNINGS:
    #Bulk store all accumulated warnings to SQL DB:
    try:
        cursor.fast_executemany = True
        cursor.executemany("INSERT INTO Warnings (RiduttoreID, Timestamp, WarningID) VALUES (?, ?, ?)", sets_warnings)
        cnxn.commit()
        log.info("Stored all warnings found into DB.")
        print("Stored all warnings found into DB.")
    except:
        log.error("Insert error: warnings not stored to DB. Please relaunch Preprocessing.")
        print("Insert error: warnings not stored to DB. Please relaunch Preprocessing.")


    #END:
    db_disconnect(cnxn, cursor)
    end_time = time.time()    
    log.info("Epoch {}: Training COMPLETED in {} seconds! Flagged {} Pressate out of {}, with sigmas: MF {}, curve {}.".format(e, round((end_time-start_time),2), tot_cnt, tot_pressate, SIGMA_MF, SIGMA_CURVE))
    print("Epoch {}: Training COMPLETED in {} seconds! Flagged {} Pressate out of {}, with sigmas: MF {}, curve {}.\n".format(e, round((end_time-start_time),2), tot_cnt, tot_pressate, SIGMA_MF, SIGMA_CURVE))
    return 0
