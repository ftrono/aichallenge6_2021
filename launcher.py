import sys
sys.path.insert(0, './')
from globals import *
#from database_functions.create_db import create_db
from training.training import preprocessing, train
from evaluation.evaluation import call_evaluate

#____________________________________________________________
#LAUNCHER

#Novotic Srl
#HIT Industrial AI Challenge - Team 6
#____________________________________________________________


#0) Reset & recreate DB:
#create_db(drop=True, limit=1000)

#1) Preprocess:
preprocessing()

#2) Train:
train()

#3) Evaluate:
#Sample timestamp: 1584106142
# timestamp = input("Evaluate: insert timestamp here -> ")
# call_evaluate(timestamp, visual=True, save=True)

