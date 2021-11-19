import sys, logging,os
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.db_tools import reset_table
from database_functions.extract_data import extract_data
from training.flag_warnings import flag_rid, flag_ma
from training.train_vectors import train_vectors
from training.training_tools import set_target_max
from database_functions.db_connect import db_connect, db_disconnect
from evaluation.eval_tools import evaluate_full

#TRAINING FUNCTIONS:
# - preprocessing()
# - train()


#1) Preprocessing: learn TargetMA and StdMA, exclude wrong pressate by MA and dt, calculate target h vectors:
def preprocessing():
    # Connect
    cnxn, cursor = db_connect()

    # Set logger:
    log=logging.getLogger('preprocessing')
    hdl=logging.FileHandler('./logs/preprocessing.log',mode='w')
    hdl.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    log.setLevel(logging.INFO)
    log.addHandler(hdl)

    #logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    log.info("Preprocessing STARTED.")
    print("Preprocessing STARTED.")

    #DB tools:
    dbt = {'cnxn': cnxn, 'cursor': cursor, 'logging': log}

    #0) reset Warnings table:
    reset_table(dbt, tablename="Warnings")
    log.info("Warnings table reset.")

    #1) set TargetMA and StdMA for all combos:
    set_target_max(dbt, mtype='altezza')
    log.info("Trained TargetMA and StdMA for all combos.")

    #2) Dataset cleaning: flag wrong curves by MA:
    flag_ma(dbt)
    log.info("Flagged all Pressate not reaching TargetMA for their combo, with sigma = {}.".format(SIGMA_MA))
    #flag_rid(dbt)
    #log.info("Flagged all Riduttori with incorrect number of pressate, with sigma = {}.".format(SIGMA_RID))

    # Disconnect
    db_disconnect(cnxn, cursor)
    log.info("Preprocessing COMPLETE!")
    print("Preprocessing COMPLETE!")
    return 0


#2) Training: learn target parameters for Combos and loop evaluate all timestamps in the DB:
def train():
    # Connect
    cnxn, cursor = db_connect()
    
    # Set logger:
    log=logging.getLogger('training')
    hdl=logging.FileHandler('./logs/training.log',mode='w')
    hdl.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    log.setLevel(logging.INFO)
    log.addHandler(hdl)
    
    #logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    log.info("Training STARTED")
    print("Training STARTED")

    #DB tools:
    dbt = {'cnxn': cnxn, 'cursor': cursor, 'logging': log}
    #vars:
    combos = {}

    #1) Reset CombosData table:
    reset_table(dbt, tablename="CombosData")
    log.info("CombosData table reset")

    #2) Extract all comboids:
    cursor.execute("SELECT ComboID, TargetMA FROM Combos")
    for tup in cursor.fetchall():
        #format: combos_ma[comboid] = target_ma (store for later)
        combos[tup[0]] = float(tup[1])
    log.info("Total number of Combos in DB: {}".format(len(combos)))
    print("Total number of Combos in DB: {}".format(len(combos)))

    #3) EPOCHS: parameters training:
    for e in range(EPOCHS):
        print("STARTED epoch #{}".format(e+1))
        log.info("STARTED epoch #{}".format(e+1))

        #1) Set TargetMF and StdMF (for all combos):
        set_target_max(dbt, mtype='forza')
        log.info("Epoch #{}: trained TargetMF and StdMF for all combos".format(e+1))

        #2) Train target Forza curves and Std_curve for all combos:
        for comboid in combos:
            cnt = 0
            timestamps = []
            target_ma = combos[comboid]

            #1) extract all timestamps with that ComboID and with NO warnings:
            cursor.execute("SELECT Pressate.Timestamp FROM Pressate WHERE Pressate.ComboID = ? AND NOT EXISTS (SELECT Warnings.Timestamp FROM Warnings WHERE Warnings.Timestamp = Pressate.Timestamp)", comboid)
            for tup in cursor.fetchall():
                timestamps.append(tup[0])
            
            if len(timestamps) < MIN_PRESSATE:
                log.info("Epoch #{}: ComboID skipped {}, number of Pressate lower than {}".format((e+1), comboid, len(timestamps)))
            else:
                #train
                log.info("Epoch #{}: training {} Pressate for ComboID {}".format((e+1), len(timestamps), comboid))

                #2) learn the current Combo vectors:
                log.info("Epoch #{}: learning the target Altezza, Forza & Stdev vectors for ComboID {}".format((e+1), comboid))
                train_vectors(dbt, comboid, target_ma, timestamps)

                #3) extract all learnt data for target ComboID:
                log.info("Epoch #{}: extracting all learned parameters for ComboID {}".format((e+1), comboid))
                target = extract_data(dbt, stype='target', comboid=comboid)

                #4) evaluate all the timestamps extracted for the ComboID:
                log.info("Epoch #{}: evaluating {} Pressate for ComboID {}".format((e+1), len(timestamps), comboid))
                print("Epoch #{}: evaluating {} Pressate for ComboID {}".format((e+1), len(timestamps), comboid))
                for i in range(len(timestamps)):
                    #status update:
                    pstr = "Epoch #"+str(e+1)+", ComboID "+str(comboid)+": evaluating Pressata "+str(i+1)+"/"+str(len(timestamps))
                    print(pstr, end = "               \r")
                    #extract data for current Pressata:
                    current = extract_data(dbt, stype='current', timestamp=timestamps[i])
                    #Evaluate current Pressata:
                    ret = evaluate_full(dbt, current, target, preprocessed=True, visual=False)
                    #if flag:
                    if ret == -1:
                        cnt = cnt+1
                    else:
                        log.debug("Evaluated Pressata timestamp {} as correct. Evaluation result: {}".format(timestamps[i], ret))
                
            #epoch completed for the current ComboID
            log.info("COMPLETED EPOCH #{}: evaluated all Pressate for ComboID {}. Flagged {} new Pressate, with sigmas: MF {}, curve {}".format((e+1), comboid, cnt, SIGMA_MF, SIGMA_CURVE))

            #Need stop mechanism.
    
    log.info("Training COMPLETE!")
    print("\nTraining COMPLETE!")
    # Disconnect
    db_disconnect(cnxn, cursor)
    return 0


#MAIN:
if __name__ == '__main__':
    preprocessing()
    train()
