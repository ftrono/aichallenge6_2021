#____________________________________________________________
#GLOBALS

#Novotic Srl
#HIT Industrial AI Challenge - Team 6
#____________________________________________________________


#SETUP:
EPOCHS = 1
MIN_ALTEZZA = 120
MIN_ORIG_ROWS = 100
MIN_PRESSATE = 2

#CHECKS:
#1) TargetMA:
CHECK_MA = False
SIGMA_MA = 2

#2) TargetMF:
SIGMA_MF = 2
FLAT_THRESHOLD_PERC = 0.5

#3) Ideal curve (points check):
SIGMA_CURVE = 2
MIN_POINTS_PERC = 0.05

#VISUAL OUTPUT:
SAVE_PNG = False
SAVE_CSV = False
OUTPUT_PATH = "./output"
PNG_SIZE = (1024, 576)
