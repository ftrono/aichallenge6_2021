from globals import *
from export.curves_plotting import plot_original
from export.export_tools import warnings_stats
from evaluation.evaluation import call_evaluate

#EXPORT LAUNCHER:
print("EXPORT LAUNCHER")
print("Please insert one of the following numbers:")
print("0 -> Evaluate a timestamp and extract png & csv")
print("1 -> Plot side by side original, sliced & interpolated force curve for a timestamp as png")
print("2 -> Export to csv Warnings statistics and extended table with all info")
print("3 -> Export as csv a full table from the DB")
launch = input("Insert number to launch here -> ")
launch = int(launch)


#0) Evaluate a timestamp and extract png & csv:
#Sample timestamps: 1613487226, 1613576433
if launch == 0:
    timestamp = input("Evaluate: insert timestamp here -> ")
    call_evaluate(timestamp, png=True, csv=True)

#1) Plot side by side original, sliced & interpolated force curve for a timestamp as png:
elif launch == 1:
    timestamp = input("Export original: insert timestamp here -> ")
    plot_original(timestamp)

#2) Export to csv Warnings statistics and extended table with all info:
elif launch == 2:
    warnings_stats()

#3) Export as csv a full table from the DB:
elif launch == 3:
    tablename = input("Export DB Table: insert table name here -> ")
    plot_original(tablename)

else:
    print("ERROR: number not in scope. Please relaunch")
