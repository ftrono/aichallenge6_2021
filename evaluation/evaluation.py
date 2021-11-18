import sys, logging
sys.path.insert(0, './')
from database_functions.db_connect import db_connect, db_disconnect
from database_functions.extract_data import extract_data
from eval_tools import evaluate_full


#PART III) EVALUATE

#CALLER:
def call_evaluate(timestamp, sigma_ma=1, sigma_mf=1, sigma_curve=1, minpoints=0, use_avg=False, visual=False, save=False):
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

    #sigmas:
    sigmas = {'sigma_ma': sigma_ma, 'sigma_mf': sigma_mf, 'sigma_curve': sigma_curve}

    #QUERY:
    #call extract_params, which return 2 objects with all needed params 
    #(one for the current pressata, the other for the target combo):
    current = extract_data(dbt, stype='current', timestamp=timestamp)
    target = extract_data(dbt, stype='target', comboid=current.comboid)

    #Call:
    evaluate_full(dbt, current, target, sigmas, minpoints=minpoints, use_avg=use_avg, preprocessed=False, visual=visual, save=save)

    # Disconnect
    db_disconnect(cnxn, cursor)
    return 0


#MAIN:
if __name__ == '__main__':
    #Sample timestamp: 1584106142
    timestamp = input("Insert timestamp here: ")
    call_evaluate(timestamp, sigma_ma=1, sigma_mf=1, sigma_curve=1, minpoints=5, use_avg=False, visual=True, save=False)
