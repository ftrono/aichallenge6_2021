import sys
sys.path.insert(0, './')
from database_functions.db_tools import reset_warnings
from training.flag_warnings import flag_dtimes, flag_ma
from training.training_tools import train_max, train_curves


#TRAINING FUNCTION:
def train(epochs):
    print("Training started.")

    #1) train TargetMA, TargetMF, StdMA, StdMF for all combos:
    train_max(mtype='altezza')
    train_max(mtype='forza')

    for e in epochs:
        print("Started epoch #{}.".format(e))
        #0) reset Warnings table:
        reset_warnings()

        #2) Dataset cleaning: flag wrong curves by MA and delta timestamps:
        flag_ma(sigma_ma=1)
        #flag_dtimes()

        #3) Target height vectors calculation for all combos:
        #target_vector_generation()

        #4) Train target Forza curves and Std_curve for all combos:
        train_curves()

    print("Training complete!")
    return 0

#MAIN:
train(epochs = 1)
