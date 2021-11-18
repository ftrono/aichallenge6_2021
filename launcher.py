import sys
sys.path.insert(0, './')
from database_functions.create_db import create_db
from training.training import preprocessing, train
from evaluation.evaluation import call_evaluate

#____________________________________________________________
#LAUNCHER

#Novotic Srl
#HIT Industrial AI Challenge - Team 6
#____________________________________________________________


#0) Reset & recreate DB:
create_db(drop=True,limit=1000)

#1) Preprocess:
preprocessing(sigma_ma=1, sigma_dt=1)

#2) Train:
train(epochs=1, sigma_mf=1, sigma_curve=1, use_avg=False, minpressate=2, minpoints=5, savepng=True)


#3) Evaluate:
#Sample timestamp: 1584106142
timestamp = input("Insert timestamp here: ")
call_evaluate(timestamp, sigma_ma=1, sigma_mf=1, sigma_curve=1, minpoints=5, use_avg=False, visual=True, save=False)

