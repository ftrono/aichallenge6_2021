import sys, logging
sys.path.insert(0, './')
from database_functions.db_connect import db_connect, db_disconnect
from database_functions.extract_data import extract_data
from evaluation.eval_tools import evaluate_full


#PART III) EVALUATE

#CALLER:
def call_evaluate(timestamp, sigma_ma=1, sigma_mf=1, sigma_curve=1):
    # Connect
    cnxn, cursor = db_connect()
    #logging.basicConfig(level=logging.INFO, filename='./logs/evaluate.log', filemode='a', format='%(asctime)s %(levelname)s %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    #DB tools:
    dbt = {'cnxn': cnxn, 'cursor': cursor, 'logging': logging}

    #sigmas:
    sigmas = {'sigma_ma': sigma_ma, 'sigma_mf': sigma_mf, 'sigma_curve': sigma_curve}

    #QUERY:
    #call extract_params, which return 2 objects with all needed params 
    #(one for the current pressata, the other for the target combo):
    current = extract_data(dbt, stype='current', timestamp=timestamp)
    target = extract_data(dbt, stype='target', comboid=current.comboid)

    #Call:
    evaluate_full(dbt, current, target, sigmas, visual=False, preprocessed=False)

    # Disconnect
    db_disconnect(cnxn, cursor)
    return 0


#MAIN:
if __name__ == '__main__':
    #Sample timestamp: 1584106169
    timestamp = input("Insert timestamp here: ")
    call_evaluate(timestamp, sigma_ma=1, sigma_mf=1, sigma_curve=1)
