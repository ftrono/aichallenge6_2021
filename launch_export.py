from globals import *
from export.curves_plotting import plot_original
from export.export_tools import warnings_stats

#EXPORT LAUNCHER:
print("EXPORT LAUNCHER")
print("Please insert one of the following numbers:")
print("0 -> Plot side by side original, sliced & interpolated force curve for a timestamp as png")
print("1 -> Export to csv Warnings statistics and extended table with all info")
print("2 -> Export as csv a full table from the DB")
launch = input("Insert number to launch here -> ")
launch = int(launch)


#1) Plot side by side original, sliced & interpolated force curve for a timestamp as png:
if launch == 0:
    timestamp = input("Export original: insert timestamp here -> ")
    plot_original(timestamp)

#2) Export to csv Warnings statistics and extended table with all info:
elif launch == 1:
    warnings_stats()

#3) Export as csv a full table from the DB:
elif launch == 2:
    tablename = input("Export DB Table: insert table name here -> ")
    plot_original(tablename)

else:
    print("ERROR: number not in scope. Please relaunch")
