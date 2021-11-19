from globals import *
from training.training import preprocessing, train
from evaluation.evaluation import call_evaluate

#____________________________________________________________
#LAUNCHER

#Novotic Srl
#HIT Industrial AI Challenge - Team 6
#____________________________________________________________


#1) Preprocess:
preprocessing()

#2) Train:
train()

#3) Evaluate:
#Sample timestamp: 1584106142
#timestamp = input("Evaluate: insert timestamp here -> ")
#call_evaluate(timestamp, visual=True, save=True)

