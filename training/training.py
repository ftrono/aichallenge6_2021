import sys
sys.path.insert(0, './')
from database_functions.db_tools import reset_warnings
from training.flag_warnings import flag_dtimes, flag_ma
from training.training_tools import train_max, train_curves
from database_functions.db_connect import db_connect, db_disconnect
from evaluation.evaluation import evaluate

#TRAINING FUNCTIONS:
# - preprocessing(sigma_ma, sigma_dt)
# - train(epochs, sigma_ma, sigma_mf, sigma_curve, verbose)


#1) Preprocessing: learn TargetMA and StdMA, exclude wrong pressate by MA and dt, calculate target h vectors:
def preprocessing(sigma_ma=1, sigma_dt=1):
    print("Preprocessing started.")

    #0) reset Warnings table:
    reset_warnings()

    #1) train TargetMA and StdMA for all combos:
    train_max(mtype='altezza')

    #2) Dataset cleaning: flag wrong curves by MA and delta timestamps:
    flag_ma(sigma_ma=sigma_ma)
    #flag_dtimes(sigma_dt=sigma_dt)

    #3) Target height vectors calculation for all combos:
    #target_vector_generation()

    print("Preprocessing complete!")
    return 0


#2) Training: learn target parameters for Combos and loop evaluate all timestamps in the DB:
def train(epochs=1, sigma_ma=1, sigma_mf=1, sigma_curve=1, verbose=True):
    # Connect
    conn, cursor = db_connect()
    timestamps = []

    if verbose == True:
        printout = True

    print("Training started.")
    
    #Parameters training:
    for e in epochs:
        print("Started epoch #{}.".format(e))

        #1) Train TargetMF, StdMF, target Forza curves and Std_curve for all combos:
        train_max(mtype='forza')
        train_curves()

        #2) extract all timestamps in the DB with NO warnings:
        cursor.execute("SELECT Pressate.Timestamp FROM Pressate WHERE NOT EXISTS (SELECT Warnings.Timestamp FROM Warnings WHERE Warnings.Timestamp = Pressate.Timestamp)")
        for tup in cursor.fetchall():
            timestamps.append(tup[0])

        #3) evaluate all the timestamps extracted:
        for timestamp in timestamps:
            evaluate(timestamp, visual=False, printout=printout, sigma_ma=sigma_ma, sigma_mf=sigma_mf, sigma_curve=sigma_curve)

        #Need stop mechanism.
    
    print("Training complete!")

    # Disconnect
    db_disconnect(conn, cursor)

    return 0


#MAIN:
train(epochs=1, sigma_ma=1, sigma_mf=1, sigma_curve=1, verbose=True)
