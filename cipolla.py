import pandas as pd
import sys, os
sys.path.insert(0, os.getcwd())
from database_functions.db_connect import db_connect,db_disconnect
cnxn, cursor = db_connect()
query = "SELECT Timestamp,Altezza FROM PressateData"
Pressate = pd.read_sql(query, cnxn)
print("QUERATO")
timestamps = Pressate['Timestamp'].unique().tolist()
timestamps = [int(t) for t in timestamps]
for timestamp in timestamps:
    #Pressata = Pressate.query('Timestamp == ' + str(timestamp))
    Pressata=Pressate[Pressate['Timestamp'] == timestamp]
    #print(Pressata)
    #print(Pressata['Altezza'].iloc[0])
    if float(Pressata['Altezza'].iloc[0])>float(Pressata['Altezza'].iloc[1]):
        print(timestamp)

db_disconnect(cnxn,cursor)