import pandas as pd

#CENTRALIZED DATA EXTRACTOR:
# - (helper) class Collector(id)
# - extract_data()


#container class:
class Collector:
    def __init__(self):
        self.riduttoreid = 0
        self.timestamp = 0
        self.comboid = ''
        self.ma = 0
        self.mf = 0
        self.std_ma = 0
        self.std_mf = 0
        self.std_curve_avg = 0
        self.altezza = []
        self.forza = []
        self.std = []


#Extract data from DB:
def extract_data(dbt, stype='current', timestamp=None, comboid=None):
    '''
    Function that extracts from the DB all the needed parameters and values for the evaluation.

    Parameters:
    -------------------
    input:
    - dbt (dict) -> dict with cnxn, cursor and logging objects
    - stype (str) -> must be either 'current' (to extract data for the current Pressata) or 'target' (to extract target data for a ComboID)
    - timestamp (int - needed if stype="current") -> timestamp of the pressata under analysis
    - comboid (str - needed if stype="target") -> ComboID of the Combo under analysis
    
    output:
    - current or target (Collector) -> 1 of 2 Collector objects (depending on "stype") storing provisionally all the parameters and values needed: one for the current pressata under analysis, the other for the target reference combo.
    '''
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logging = dbt['logging']
    
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
        logging.debug("Extracting data for Pressata {}".format(timestamp))

        #EXTRACT DATA FOR CURRENT TIMESTAMP:
        try:
            query = "SELECT ComboID, MaxForza, MaxAltezza, RiduttoreID FROM Pressate WHERE Timestamp="+str(timestamp)
            df = pd.read_sql(query, cnxn)
        except:
            return -1
        #comboid:
        comboid = str(df['ComboID'][0])
        current.comboid = comboid
        #extract data:
        current.mf = float(df['MaxForza'][0])
        current.ma = float(df['MaxAltezza'][0])
        current.riduttoreid = int(df['RiduttoreID'][0])

        #EXTRACT ORIGINAL CURVES FOR CURRENT TIMESTAMP:
        query = "SELECT Forza, Altezza FROM PressateData WHERE Timestamp="+str(timestamp)
        #store to Pandas dataframe
        df = pd.read_sql(query, cnxn)
        #extract data:
        current.forza = list(df['Forza'].to_numpy())
        current.altezza = list(df['Altezza'].to_numpy())
        logging.debug("Extraction complete")
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
        logging.debug("Extracting target data for ComboID {}".format(comboid))

        #EXTRACT TARGET COMBO DATA:
        query = "SELECT TargetMA, TargetMF, StdMA, StdMF, StdCurveAvg FROM Combos WHERE ComboID='"+str(comboid)+"'"
        df = pd.read_sql(query, cnxn)
        #extract data:
        target.ma = float(df['TargetMA'][0])
        target.mf = float(df['TargetMF'][0])
        target.std_ma = float(df['StdMA'][0])
        target.std_mf = float(df['StdMF'][0])
        target.std_curve_avg = float(df['StdCurveAvg'][0])

        #EXTRACT TARGET CURVES FOR THE COMBO:
        query = "SELECT Forza, Altezza, Std FROM CombosData WHERE ComboID='"+str(comboid)+"'"
        #store to Pandas dataframe
        df = pd.read_sql(query, cnxn)
        #extract data:
        target.forza = list(df['Forza'].to_numpy())
        target.altezza = list(df['Altezza'].to_numpy())
        target.std = list(df['Std'].to_numpy())
        logging.debug("Extraction complete")
        return target 
