from database_functions.db_tools import drop_all, generate_tables, populate_max
from database_functions.db_connect import db_connect, db_disconnect
from database_functions.insert_data import insert_data
import logging


#CREATE DB (DROP & REPOPULATE ALL TABLES):
def create_db(drop=False,limit=1000000):

    #init:
    status_log=logging.getLogger('status')
    general_log=logging.getLogger('general')
    updates_log=logging.getLogger('updates')
    hdlr1=logging.FileHandler('status.log',mode='w')
    hdlr2=logging.FileHandler('./logs/insert.log',mode='w')
    hdlr3=logging.FileHandler('updates.log',mode='w')
    hdlr1.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    hdlr2.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    hdlr3.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    general_log.setLevel(logging.DEBUG)
    status_log.setLevel(logging.INFO)
    updates_log.setLevel(logging.INFO)
    status_log.addHandler(hdlr1)
    general_log.addHandler(hdlr2)
    updates_log.addHandler(hdlr3)
    general_log.info("DB connection OPENED")
    cnxn, cursor = db_connect()

    #DB tools:
    dbt = {'cnxn': cnxn, 'cursor': cursor}
    
    if drop == True:
        drop_all(dbt)

    #Generate database:
    updates_log.info("Generating tables...")
    generate_tables(dbt)
    updates_log.info("Import process started")
    _, etime = insert_data(dbt,limit)
    updates_log.info(f"Import completed! in {etime} seconds")
    updates_log.info("Started populating max")
    populate_max(dbt)
    updates_log.info("Completed db population")
    db_disconnect(cnxn, cursor)
    general_log.info("DB connection CLOSED")
    general_log.info("PROCESS COMPLETED!")
    updates_log.info("Process concluded!")
    return 0

#MAIN:
if __name__ == '__main__':
    create_db(drop=False,limit=1000000)
