import sys, logging
sys.path.insert(0, './')
from globals import *
from database_functions.db_connect import db_connect, db_disconnect
from database_functions.extract_data import extract_data
from eval_tools import evaluate_full


#PART III) EVALUATE

#CALLER:
def call_evaluate(timestamp, visual=WINDOW, save=SAVE_PNG):
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
    target = extract_data(dbt, stype='target', comboid=current.comboid)

    #Call:
    evaluate_full(dbt, current, target, preprocessed=False, visual=visual, save=save, verbose=True)

    # Disconnect
    db_disconnect(cnxn, cursor)
    return 0


#MAIN:
if __name__ == '__main__':
    #Sample timestamp: 1584106142, 1584348510, 1584348501, 1584349549
    timestamp = input("Evaluate: insert timestamp here -> ")
    call_evaluate(timestamp, visual=True, save=False)
