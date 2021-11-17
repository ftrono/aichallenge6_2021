import sys, logging
sys.path.insert(0, './')
from database_functions.db_tools import reset_table
from database_functions.extract_data import extract_data
from flag_warnings import flag_dtimes, flag_ma
from target_vectors import train_vectors
from training_tools import set_target_max
from database_functions.db_connect import db_connect, db_disconnect
from evaluation.eval_tools import evaluate_full

#TRAINING FUNCTIONS:
# - preprocessing(sigma_ma, sigma_dt)
# - train(epochs, sigma_ma, sigma_mf, sigma_curve)


#1) Preprocessing: learn TargetMA and StdMA, exclude wrong pressate by MA and dt, calculate target h vectors:
def preprocessing(sigma_ma=1, sigma_dt=1):
    # Connect
    cnxn, cursor = db_connect()
    #logging.basicConfig(level=logging.INFO, filename='./logs/preprocess.log', filemode='w', format='%(asctime)s %(levelname)s %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info("Preprocessing STARTED.")

    #DB tools:
    dbt = {'cnxn': cnxn, 'cursor': cursor, 'logging': logging}

    #0) reset Warnings table:
    reset_table(dbt, tablename="Warnings")
    logging.info("Warnings table reset.")

    #1) set TargetMA and StdMA for all combos:
    set_target_max(dbt, mtype='altezza')
    logging.info("Trained TargetMA and StdMA for all combos.")

    #2) Dataset cleaning: flag wrong curves by MA:
    flag_ma(dbt, sigma_ma)
    logging.info("Flagged all Pressate not reaching TargetMA for their combo, with sigma = {}.".format(sigma_ma))
    #flag_dtimes(dbt, sigma_dt)
    #logging.info("Flagged all Riduttori with incorrect number of pressate, with sigma = {}.".format(sigma_dt))

    # Disconnect
    db_disconnect(cnxn, cursor)
    logging.info("Preprocessing COMPLETE!")
    return 0


#2) Training: learn target parameters for Combos and loop evaluate all timestamps in the DB:
def train(epochs=1, sigma_mf=1, sigma_curve=1):
    # Connect
    cnxn, cursor = db_connect()
    #logging.basicConfig(level=logging.INFO, filename='./logs/training.log', filemode='w', format='%(asctime)s %(levelname)s %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logging.info("Training STARTED")

    #DB tools:
    dbt = {'cnxn': cnxn, 'cursor': cursor, 'logging': logging}
    #vars:
    sigmas = {'sigma_mf': sigma_mf, 'sigma_curve': sigma_curve}
    combos = {}

    #1) Reset CombosData table:
    reset_table(dbt, tablename="CombosData")
    logging.info("CombosData table reset")

    #2) Extract all comboids:
    cursor.execute("SELECT ComboID, TargetMA FROM Combos")
    for tup in cursor.fetchall():
        #format: combos_ma[comboid] = target_ma (store for later)
        combos[tup[0]] = float(tup[1])

    #3) EPOCHS: parameters training:
    for e in range(epochs):
        logging.info("STARTED epoch #{}".format(e+1))

        #1) Set TargetMF and StdMF (for all combos):
        set_target_max(dbt, mtype='forza')
        logging.info("Epoch #{}: trained TargetMF and StdMF for all combos".format(e+1))

        #2) Train target Forza curves and Std_curve for all combos:
        for comboid in combos:
            cnt = 0
            timestamps = []
            target_ma = combos[comboid]
            logging.info("Epoch #{}: training ComboID {}".format((e+1), comboid))

            #1) extract all timestamps with that ComboID and with NO warnings:
            cursor.execute("SELECT Pressate.Timestamp FROM Pressate WHERE Pressate.ComboID = ? AND NOT EXISTS (SELECT Warnings.Timestamp FROM Warnings WHERE Warnings.Timestamp = Pressate.Timestamp)", comboid)
            for tup in cursor.fetchall():
                timestamps.append(tup[0])

            #2) learn the current Combo vectors:
            logging.info("Epoch #{}: learning the target Altezza and Forza vectors for ComboID {}".format((e+1), comboid))
            train_vectors(dbt, comboid, target_ma, timestamps)

            #3) extract all learnt data for target ComboID:
            logging.info("Epoch #{}: extracting all learned parameters for ComboID {}".format((e+1), comboid))
            target = extract_data(dbt, stype='target', comboid=comboid)

            #4) evaluate all the timestamps extracted for the ComboID:
            logging.info("Epoch #{}: evaluating all Pressate for ComboID {}".format((e+1), comboid))
            for timestamp in timestamps:
                #extract data for current Pressata:
                current = extract_data(dbt, stype='current', timestamp=timestamp)
                #Evaluate current Pressata:
                ret = evaluate_full(dbt, current, target, sigmas, visual=False, preprocessed=True)
                #if flag:
                if ret == -1:
                    cnt = cnt+1
                else:
                    logging.debug("Evaluated Pressata timestamp {} as correct. Evaluation result: {}".format(timestamp, ret))
            
        #epoch completed for the current ComboID
        logging.info("COMPLETED EPOCH #{}: evaluated all Pressate for ComboID {}. Flagged {} new Pressate, with sigmas: MF {}, curve {}".format((e+1), comboid, cnt, sigma_mf, sigma_curve))

        #Need stop mechanism.
    
    logging.info("Training COMPLETE!")
    # Disconnect
    db_disconnect(cnxn, cursor)
    return 0


#MAIN:
preprocessing(sigma_ma=1, sigma_dt=1)
train(epochs=1, sigma_mf=1, sigma_curve=1)
