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
#a. Full training (accepts any number of epochs):
for epoch in range(EPOCHS):
    train(epoch, resume=False)

#b. Resume training (NOTE: only for one epoch!):
# Use this option ONLY if previous training was interrupted at some point
# or if received some DB insert errors in prior training:
#train(resume=True)


# #3) Evaluate:
# #Sample timestamps: 1584106142, 1584348510, 1584348501, 1584349549, 1584369231
#timestamp = input("Evaluate: insert timestamp here -> ")
#call_evaluate(timestamp, flag=False, visual=True, save=True)

