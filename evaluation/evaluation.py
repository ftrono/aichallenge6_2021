import sys, logging,os
sys.path.insert(0, os.getcwd())
from globals import *
from database_functions.db_connect import db_connect, db_disconnect
from database_functions.extract_data import extract_data
from evaluation.eval_tools import evaluate_full
from export.curves_plotting import export_curves


#PART III) EVALUATE

#CALLER:
def call_evaluate(timestamp, flag=False, visual=WINDOW, save=SAVE_PNG):
    '''
    Standalone evaluation function caller. It:
    - initializes DB connection and logger
    - extracts the data for the current Pressata (current) and the target ComboID (target), both as Collector objects
    - calls the evaluate function (evaluate_full())

    Parameters:
    -------------------
    input:
    - timestamp (int) -> timestamp of the Pressata to analyze
    - visual (bool) -> visualize the curves plot in a window
    - save (bool) -> saves the curves plot as png file
    '''
    # Connect
    cnxn, cursor = db_connect()

    # Set logger:
    log=logging.getLogger('evaluate')
    hdl=logging.FileHandler('./logs/evaluate.log',mode='a')
    hdl.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    log.setLevel(logging.INFO)
    log.addHandler(hdl)

    #logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    #DB tools:
    dbt = {'cnxn': cnxn, 'cursor': cursor, 'logging': log}

    #QUERY:
    #call extract_params, which return 2 objects with all needed params 
    #(one for the current pressata, the other for the target combo):
    current = extract_data(dbt, stype='current', timestamp=timestamp)
    if current == -1:
        print("ERROR: timestamp {} not found.".format(timestamp))
        db_disconnect(cnxn, cursor)
        return -1
    
    target = extract_data(dbt, stype='target', comboid=current.comboid)

    #Call:
    wid = evaluate_full(log, current, target, preprocessed=False, visual=visual, save=save, verbose=True)
    if SAVE_CSV == True:
        export_curves(dbt=dbt, current=current, target=target, wid=wid)
    if wid != 0 and flag == True:
        #Store warning found to SQL DB:
        try:
            cursor.execute("INSERT INTO Warnings (RiduttoreID, Timestamp, WarningID) VALUES (?, ?, ?)", current.riduttoreid, current.timestamp, wid)
            cnxn.commit()
            log.info("Timestamp: {}. Stored warning found into DB.".format(current.timestamp))
        except:
            log.error("Timestamp: {}. Insert error: warning not stored to DB. Please retry.".format(current.timestamp))
            print("Timestamp: {}. Insert error: warning not stored to DB. Please retry.".format(current.timestamp))

    # Disconnect
    db_disconnect(cnxn, cursor)
    return 0


#MAIN:
if __name__ == '__main__':
    #Sample timestamps: 1584106142, 1584348510, 1584348501, 1584349549
    timestamp = input("Evaluate: insert timestamp here -> ")
    call_evaluate(timestamp, visual=True, save=False)
