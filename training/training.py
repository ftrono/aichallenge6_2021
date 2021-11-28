import sys, logging, os, time, statistics
import pandas as pd
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.db_connect import db_connect, db_disconnect
from database_functions.db_tools import reset_table
from database_functions.extract_data import Collector
from training.training_tools import compute_rate, generate_hvec, slice_curves, interpolate_curve, ideal_curve, stdev_curve
from evaluation.eval_tools import evaluate_anomalous, evaluate_full
from export.curves_plotting import export_curves

#TRAINING:
#Complete population of the Combos, CombosData and Warnings tables.
# - set TargetMF and StdMF for every ComboID;
# - learn target curves (altezza_combo, forza_combo and points_std) for every ComboID;
# - evaluate all Pressate in the DB and flag those not reaching TargetMF (with a sigma) and with curves out of bounds.


def train(epoch=0, resume=False):
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

    #Note: resume training can be used only for one epoch!
    if resume == True:
        e = str(epoch+1)+"_res"
        logname = './logs/training_resume.log'
    else:
        e = epoch+1
        logname = './logs/training_epoch'+str(e)+'.log'

    #INIT:
    # Set logger:
    log=logging.getLogger('training')
    hdl=logging.FileHandler(logname,mode='w')
    hdl.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    log.setLevel(logging.DEBUG)
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
    c_trained = []
    tot_cnt = 0
    db_errors = []
    warn_error = False

    #0) Training mode: full or resume:
    if resume == False:
        #reset learned CombosData table:
        reset_table(dbt, tablename="CombosData")
        log.info("CombosData table reset")


    #1) Extract ALL needed tables into memory (only timestamps with no warnings):
    #Pressate:
    log.info("Extracting tables from SQL DB...")
    query = "SELECT Pressate.Timestamp, Pressate.RiduttoreID, Pressate.ComboID, Pressate.MaxForza, Pressate.MaxAltezza FROM Pressate WHERE NOT EXISTS (SELECT Warnings.Timestamp FROM Warnings WHERE Warnings.Timestamp = Pressate.Timestamp)"
    Pressate = pd.read_sql(query, cnxn)
    tot_pressate = len(Pressate['Timestamp'].tolist())
    log.info("Extracted table 1/3 (Pressate)")

    #PressateData:
    query = "SELECT PressateData.Timestamp, Pressate.ComboID, PressateData.Forza, PressateData.Altezza FROM PressateData INNER JOIN Pressate ON PressateData.Timestamp = Pressate.Timestamp WHERE NOT EXISTS (SELECT Warnings.Timestamp FROM Warnings WHERE Warnings.Timestamp = PressateData.Timestamp)"
    PressateData = pd.read_sql(query, cnxn)
    log.info("Extracted table 2/3 (PressateData)")

    #Combos:
    if resume == False:
        query = "SELECT ComboID, TargetMA, StdMA FROM Combos"
    else:
        query = "SELECT ComboID, TargetMA, StdMA, TargetMF, StdMF, StdCurveAvg FROM Combos"
    Combos = pd.read_sql(query, cnxn)
    log.info("Extracted table 3/3 (Combos)")
    #list of ComboIDs:
    combos_list = Combos['ComboID'].tolist()

    #CombosData (only if resume):
    if resume == True:
        #extract already learned curves:
        query = "SELECT * FROM CombosData"
        CombosData = pd.read_sql(query, cnxn)
        c_trained = CombosData['ComboID'].unique().tolist()
        log.info("Extracted additional table for resume training (CombosData)")

    res = len(combos_list)-len(c_trained)
    log.info("Total number of Combos to train: {}/{}".format(res, len(combos_list)))
    print("Total number of Combos to train: {}/{}".format(res, len(combos_list)))


    #2) For each ComboID:
    for comboid in combos_list:
        #training accumulation lists:
        currents = []
        batch_heights = []
        batch_forces = []
        cnt = 0
        combo_start = time.time()
        query = 'ComboID == "'+comboid+'"'

        #extract portion of Pressate table only with the current ComboID:
        log.info("NEW ComboID: {}. Initializing data for training...".format(comboid))
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


            #1) INIT:
            #init target Collector:
            target = Collector()
            target.comboid = str(comboid)
            Combo = Combos.query(query)
            target.ma = float(Combo['TargetMA'].iloc[0])
            target.std_ma = float(Combo['StdMA'].iloc[0])
            #convert TargetMA to max acceptable TargetMA (for training):
            target.ma = target.ma + target.std_ma*SIGMA_MA

            #extract curves of interest for the Combo:
            log.debug("ComboID: {}: Extracting original curves...".format(comboid))

            #a. from PressateData:
            PressateComboData = PressateData.query(query)
            #remove this portion from the original Pressate table (to save memory):
            rows = PressateComboData.index.values.tolist()
            PressateData.drop(rows, inplace=True)

            #b. from CombosData (only if ComboID already trained):
            if resume == True and comboid in c_trained:
                ComboData = CombosData.query(query)
                #remove this portion from the original CombosData table (to save memory):
                rows = ComboData.index.values.tolist()
                CombosData.drop(rows, inplace=True)


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
            log.debug("ComboID: {}: Collectors ready".format(comboid))
            
            #clean memory:
            del Pressata
            del PressataData


            #ii) Learn the target Forza parameters and target height vector for the Combo:
            if resume == True and comboid in c_trained:
                #get already learned Forza parameters and target h vectors:
                target.mf = float(Combo['TargetMF'].iloc[0])
                target.std_mf = float(Combo['StdMF'].iloc[0])
                target.altezza = ComboData['Altezza'].tolist()
                log.debug("ComboID {}. Prelearned target Altezza curve extracted".format(comboid))
            else:
                #learn:
                # TargetMF and StdMF:
                target.mf = float(PressateCombo['MaxForza'].mean())
                try:
                    target.std_mf = float(PressateCombo['MaxForza'].std()) + 1
                except:
                    target.std_mf = 1
                log.debug("ComboID {}. TargetMF and StdMF generated".format(comboid))

                # h vector:
                sample_rate = compute_rate(batch_heights)
                target.altezza = generate_hvec(sample_rate, MIN_ALTEZZA, target.ma)
                #error check:
                if len(target.altezza) <= 3:
                    log.error("ComboID skipped {}, the learned target Altezza vector is shorter than 3 points.".format(comboid))
                    print("ComboID skipped {}, the learned target Altezza vector is shorter than 3 points.".format(comboid))
                    #skip to next Combo:
                    continue
                #else: go on:
                log.debug("ComboID: {}: Learned target Altezza vector".format(comboid))
                del batch_heights


            #iii) Slice & interpolate original curves:
            max_l = 0
            for current in currents:
                #1. slice portions of interest of original curves:
                current.altezza, current.forza = slice_curves(target.altezza, current.altezza, current.forza)
                #2. check anomalous sliced curve:
                wid = evaluate_anomalous(log, current, target, sliced=True)
                if wid != 0:
                    cnt = cnt+1
                    #accumulate warnings (WID 2: anomalous height curve):
                    sets_warnings.append((current.riduttoreid, current.timestamp, wid))
                else:
                    #update checker var:
                    cur_l = len(current.altezza)
                    if cur_l > max_l:
                        max_l = cur_l

                    #3. interpolate force curve:
                    current.forza = interpolate_curve(target.altezza, current.altezza, current.forza)
                    batch_forces.append(current.forza)
            log.debug("ComboID: {}: Sliced and interpolated original curves in all Collectors".format(comboid))

            #check if can proceed:
            if max_l <= 3:
                log.error("ComboID skipped {}, all sliced vectors are shorter than 3 points.".format(comboid))
                print("ComboID skipped {}, all sliced vectors are shorter than 3 points.".format(comboid))
                #skip to next Combo:
                continue
            

            #iv) Learn the target Forza curve, Std_curve and StdCurveAvg for the Combo:
            if resume == True and comboid in c_trained:
                #use already learned data:
                target.forza = ComboData['Forza'].tolist()
                target.std = ComboData['Std'].tolist()
                target.std_curve_avg = float(Combo['StdCurveAvg'].iloc[0])
                log.debug("ComboID {}. Prelearned target Forza curve and std_curve extracted".format(comboid))
            else:
                #learn:
                #target Forza curve, Std_curve and StdCurveAvg:
                target.forza = ideal_curve(batch_forces)
                target.std = stdev_curve(batch_forces)
                target.std_curve_avg = float(statistics.mean(target.std))
                del batch_forces
                log.debug("ComboID {}. Target Forza curve, Std_curve and StdCurveAvg generated".format(comboid))

                #accumulate every index in target lists:
                for i in range(len(target.altezza)):
                    sets_curves.append((comboid, float(target.altezza[i]), float(target.forza[i]), float(target.std[i])))


                #BULK STORE ALL LEARNED PARAMETERS AND CURVES TO SQL DB (if not stored yet):
                #Store TargetMF, StdMF and StdCurveAvg:
                try:
                    cursor.execute("UPDATE Combos SET TargetMF = ?, StdMF = ?, StdCurveAvg = ? WHERE ComboID = ?", float(target.mf), float(target.std_mf), float(target.std_curve_avg), comboid)
                    cnxn.commit()
                    log.info("ComboID {}: Successfully stored TargetMF, StdMF and StdCurveAvg into DB.".format(comboid))
                    print("ComboID {}: Successfully stored TargetMF, StdMF and StdCurveAvg into DB.".format(comboid))
                except:
                    db_errors.append(comboid)
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
                    if comboid not in db_errors:
                        db_errors.append(comboid)
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
                #if timestamp was not flagged with WID 2 after slicing (so, it was successfully interpolated):
                if len(currents[i].forza) == len(target.altezza):
                    #evaluate current Pressata:
                    wid = evaluate_full(log, currents[i], target, preprocessed=True, visual=False)
                    if SAVE_CSV == True:
                        export_curves(dbt=dbt, current=currents[i], target=target, wid=wid)
                    if wid != 0:
                        cnt = cnt+1
                        #accumulate warnings (either WID 3 - MaxForza or WID 4 - Curve):
                        sets_warnings.append((currents[i].riduttoreid, currents[i].timestamp, wid))
            

            #4) END STATISTICS:
            combo_end = time.time()
            tot_cnt = tot_cnt + cnt
            log.info("ComboID {}: training completed in {} seconds. Found {} Pressate to be flagged out of {}.".format(comboid, round((combo_end-combo_start),2), cnt, len(timestamps)))
            print("\nComboID {}: training completed in {} seconds. Found {} Pressate to be flagged out of {}.".format(comboid, round((combo_end-combo_start),2), cnt, len(timestamps)))


    #3) BULK STORE WARNINGS:
    #Bulk store all accumulated warnings to SQL DB:
    try:
        cursor.fast_executemany = True
        cursor.executemany("INSERT INTO Warnings (RiduttoreID, Timestamp, WarningID) VALUES (?, ?, ?)", sets_warnings)
        cnxn.commit()
        log.info("Stored all warnings found into DB.")
        print("Stored all warnings found into DB.")
    except:
        warn_error = True
        log.error("Insert error: warnings not stored to DB. Please retry later.")
        print("Insert error: warnings not stored to DB. Please retry later.")


    #END:
    db_disconnect(cnxn, cursor)
    end_time = time.time()
    missed = len(combos_list) - len(db_errors)

    if warn_error == False:
        log.info("Epoch {}: Training COMPLETED in {} seconds. Parameters stored in DB for {} combos out of {}. Flagged {} Pressate out of {}, with sigmas: MF {}, curve {}.".format(e, round((end_time-start_time),2), missed, len(combos_list), tot_cnt, tot_pressate, SIGMA_MF, SIGMA_CURVE))
        print("Epoch {}: Training COMPLETED in {} seconds. Parameters stored in DB for {} combos out of {}. Flagged {} Pressate out of {}, with sigmas: MF {}, curve {}.\n".format(e, round((end_time-start_time),2), missed, len(combos_list), tot_cnt, tot_pressate, SIGMA_MF, SIGMA_CURVE))
        
        if len(db_errors) == 0:
            return 0
        else:
            log.info("Epoch {}: Parameters not stored for the following combos:".format(e))
            log.info(db_errors)
            return -1

    else:
        log.info("Epoch {}: Training COMPLETED in {} seconds. Parameters stored in DB for {} combos out of {}. Warnings NOT stored to DB. Found {} Pressate to be flagged out of {}, with sigmas: MF {}, curve {}.".format(e, round((end_time-start_time),2), missed, len(combos_list), tot_cnt, tot_pressate, SIGMA_MF, SIGMA_CURVE))
        print("Epoch {}: Training COMPLETED in {} seconds. Parameters stored in DB for {} combos out of {}. Warnings NOT stored to DB. Found {} Pressate to be flagged out of {}, with sigmas: MF {}, curve {}.\n".format(e, round((end_time-start_time),2), missed, len(combos_list), tot_cnt, tot_pressate, SIGMA_MF, SIGMA_CURVE))

        if len(db_errors) != 0:
            log.info("Epoch {}: Parameters not stored for the following combos:".format(e))
            log.info(db_errors)
        return -1
