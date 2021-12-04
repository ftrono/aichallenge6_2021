#____________________________________________________________
#GLOBALS

#Novotic Srl
#HIT Industrial AI Challenge - Team 6
#____________________________________________________________


#SETUP:
EPOCHS = 1
MIN_ALTEZZA = 100
MIN_PRESSATE = 2

#CHECKS:
#1) TargetMA:
CHECK_MA = False
SIGMA_MA = 2

#2) TargetMF:
CHECK_MF = True
SIGMA_MF = 2
FLAT_THRESHOLD_PERC = 0.5

#3) Ideal curve (points check):
SIGMA_CURVE = 2
MIN_POINTS_PERC = 0.05
USE_AVG = False

#VISUAL OUTPUT:
SAVE_PNG = False
PNG_SIZE = (1024, 576)
SAVE_CSV = False
WINDOW = False
OUTPUT_PATH = "./output"
