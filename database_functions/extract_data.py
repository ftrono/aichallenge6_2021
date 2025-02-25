import pandas as pd
import sqlalchemy as sa

#CENTRALIZED DATA EXTRACTOR:
# - (helper) class Collector(id)
# - extract_data()


#container class:
class Collector:
    def __init__(self):
        self.riduttoreid = 0
        self.timestamp = 0
        self.comboid = ''
        self.evaluated = 0
        self.ma = 0
        self.mf = 0
        self.std_ma = 0
        self.std_mf = 0
        self.std_curve_avg = 0
        self.altezza = []
        self.forza = []
        self.std = []
        self.boundup = []
        self.boundlow = []
        self.stazione = ''
        self.master = 0
        self.rapporto = 0
        self.stadi = 0
        self.cd = 0


#Extract data from DB:
def extract_data(engine, stype='current', timestamp=None, comboid=None):
    '''
    Function that extracts from the DB all the needed parameters and values for the evaluation.

    Parameters:
    -------------------
    input:
    - dbt (dict) -> dict with cnxn and cursor objects
    - stype (str) -> must be either 'current' (to extract data for the current Pressata) or 'target' (to extract target data for a ComboID)
    - timestamp (int - needed if stype="current") -> timestamp of the pressata under analysis
    - comboid (str - needed if stype="target") -> ComboID of the Combo under analysis
    
    output:
    - current or target (Collector) -> 1 of 2 Collector objects (depending on "stype") storing provisionally all the parameters and values needed: one for the current pressata under analysis, the other for the target reference combo.
    '''
    
    # cursor = dbt['cursor']
    # cnxn = dbt['cnxn']
    
    
    #args check:
    if (stype != 'current') and (stype != 'target'):
        print("ERROR: stype must be either 'current' or 'target'!")
        raise

    #a) extract key data for current Pressata:
    elif stype == 'current':
        if not timestamp:
            print("ERROR: missing input Timestamp.")
            return -1
        #1) CURRENT PRESSATA:
        #init collector:
        current = Collector()
        current.timestamp = timestamp

        #EXTRACT DATA FOR CURRENT TIMESTAMP:
        try:
            with engine.begin() as conn:
                query = sa.text("SELECT Pressate.ComboID, Pressate.MaxForza, Pressate.MaxAltezza, Pressate.RiduttoreID, Pressate.Evaluated, Pressate.Stazione, Riduttori.Master, Riduttori.Rapporto, Riduttori.Stadi, Riduttori.Cd FROM Pressate INNER JOIN Riduttori on Pressate.RiduttoreID = Riduttori.RiduttoreID WHERE Timestamp="+str(timestamp))
                df = pd.read_sql(query, conn)
        except:
            return -1

        #check if data found:
        if df.empty==True:
            print("ERROR: no data.")
            return -1
            
        #comboid:
        comboid = str(df['ComboID'][0])
        current.comboid = comboid
        #extract data:
        current.mf = float(df['MaxForza'][0])
        current.ma = float(df['MaxAltezza'][0])
        current.riduttoreid = int(df['RiduttoreID'][0])
        current.evaluated = int(df['Evaluated'][0])
        #full info extraction:
        current.stazione = str(df['Stazione'].iloc[0])
        current.master = int(df['Master'].iloc[0])
        current.rapporto = int(df['Rapporto'].iloc[0])
        current.stadi = int(df['Stadi'].iloc[0])
        current.cd = float(df['Cd'].iloc[0])

        #EXTRACT ORIGINAL CURVES FOR CURRENT TIMESTAMP:

        with engine.begin() as conn:
            query = sa.text("SELECT Forza, Altezza FROM PressateData WHERE Timestamp="+str(timestamp))
            df = pd.read_sql(query, conn)
        #extract data:
        current.forza = list(df['Forza'].to_numpy())
        current.altezza = list(df['Altezza'].to_numpy())
        return current

    #b) extract key data for target ComboID:
    else:
        if not comboid:
            print("ERROR: missing input ComboID.")
            return -1
        #2) TARGET COMBOID:
        #init collector:
        target = Collector()
        target.comboid = comboid

        #EXTRACT TARGET COMBO DATA:
        try:
            with engine.begin() as conn:
                query = sa.text("SELECT TargetMA, TargetMF, StdMA, StdMF, StdCurveAvg FROM Combos WHERE ComboID='"+str(comboid)+"'")
                df = pd.read_sql(query, conn)
        except:
            return -1

        #check if data found:
        if df.empty==True:
            print("ERROR: no data.")
            return -1

        #extract data:
        target.ma = float(df['TargetMA'][0])
        target.mf = float(df['TargetMF'][0])
        target.std_ma = float(df['StdMA'][0])
        target.std_mf = float(df['StdMF'][0])
        target.std_curve_avg = float(df['StdCurveAvg'][0])

        #EXTRACT TARGET CURVES FOR THE COMBO:
        with engine.begin() as conn:
            query = sa.text("SELECT Forza, Altezza, Std FROM CombosData WHERE ComboID='"+str(comboid)+"'")
            df = pd.read_sql(query, conn)
        #extract data:
        target.forza = list(df['Forza'].to_numpy())
        target.altezza = list(df['Altezza'].to_numpy())
        target.std = list(df['Std'].to_numpy())
        return target 
