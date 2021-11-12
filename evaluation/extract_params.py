import sys
sys.path.insert(0, './')
from database_functions.db_connect import db_connect, db_disconnect
import pandas as pd

#container class:
class Collector:
    def __init__(self, id):
        self.id = id
        self.ma = 0
        self.mf = 0
        self.std_ma = 0
        self.std_mf = 0
        self.std_curve = 0
        self.altezza = []
        self.forza = []


#extract:
def extract_params(timestamp):
    # open connection
    cnxn, cursor = db_connect()
    
    #1) CURRENT PRESSATA:
    #init collector:
    current = Collector(timestamp)

    #EXTRACT DATA FOR CURRENT TIMESTAMP:
    query = "SELECT ComboID, MaxForza, MaxAltezza FROM Pressate WHERE Timestamp="+str(timestamp)
    df = pd.read_sql(query, cnxn)
    #comboid:
    combo_id = str(df['ComboID'][0])
    #extract data:
    current.mf = float(df['MaxForza'][0])
    current.ma = float(df['MaxAltezza'][0])

    #EXTRACT ORIGINAL CURVES FOR CURRENT TIMESTAMP:
    query = "SELECT Forza, Altezza FROM PressateData WHERE Timestamp="+str(timestamp)
    #store to Pandas dataframe
    df = pd.read_sql(query, cnxn)
    #extract data:
    current.forza = list(df['Forza'].to_numpy())
    current.altezza = list(df['Altezza'].to_numpy())


    #2) TARGET COMBOID:
    #init collector:
    target = Collector(combo_id)

    #EXTRACT TARGET COMBO DATA:
    query = "SELECT TargetMA, TargetMF, StdMA, StdMF, StdCurve FROM Combos WHERE ComboID='"+str(combo_id)+"'"
    df = pd.read_sql(query, cnxn)
    #extract data:
    target.ma = float(df['TargetMA'][0])
    target.mf = float(df['TargetMF'][0])
    target.std_ma = float(df['StdMA'][0])
    target.std_mf = float(df['StdMF'][0])
    target.std_curve = float(df['StdCurve'][0])

    #EXTRACT TARGET CURVES FOR THE COMBO:
    query = "SELECT Forza, Altezza FROM CombosData WHERE ComboID='"+str(combo_id)+"'"
    #store to Pandas dataframe
    df = pd.read_sql(query, cnxn)
    #extract data:
    target.forza = list(df['Forza'].to_numpy())
    target.altezza = list(df['Altezza'].to_numpy())

    #close cursor and connection
    db_disconnect(cnxn, cursor)

    return current, target 


#MAIN:
timestamp = 1584106169
current, target = extract_params(1584106169)

print("Current:")
print(vars(current).items())
print("\nTarget:")
print(vars(target).items())
