from globals import *
from training.preprocessing import preprocessing
from training.training import train
from evaluation.evaluation import call_evaluate

#____________________________________________________________
#LAUNCHER

#Novotic Srl
#HIT Industrial AI Challenge - Team 6
#____________________________________________________________


#1) Preprocess:
preprocessing()

# #2) Train:
#2) EPOCHS:
for epoch in range(EPOCHS):
    train(epoch)

# #3) Evaluate:
# #Sample timestamps: 1584106142, 1584348510, 1584348501, 1584349549, 1584369231
#timestamp = input("Evaluate: insert timestamp here -> ")
#call_evaluate(timestamp, visual=True, save=True)

