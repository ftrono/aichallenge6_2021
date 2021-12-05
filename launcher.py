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

# 2) Train:
#First epoch:
'''
- resume option:
    use True ONLY if previous training was interrupted at some point or if received some DB insert errors in prior training.
'''
train(resume=False)

#Next epochs (accepts any number of epochs. No resume):
if EPOCHS > 1:
    for epoch in range(1, EPOCHS):
        train(epoch)

#3) Evaluate:
#Sample timestamps: 1584106142, 1584348510, 1584348501, 1584349549, 1584369231, 1590414268, 1603464095, 1603455160
timestamp = input("Evaluate: insert timestamp here -> ")
call_evaluate(timestamp, png=True, csv=True)
