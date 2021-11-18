from db_tools import drop_all, generate_tables, populate_max
from db_connect import db_connect, db_disconnect
from insert_data import insert_data
import logging


#CREATE DB (DROP & REPOPULATE ALL TABLES):
def create_db(drop=False):
    #logging.basicConfig(level=logging.INFO, filename='./logs/insert.log', filemode='w', format='%(asctime)s %(levelname)s %(message)s')
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    logging.info("DB connection OPENED")
    cnxn, cursor = db_connect()

    #DB tools:
    dbt = {'cnxn': cnxn, 'cursor': cursor, 'logging': logging}
    
    if drop == True:
        drop_all(dbt)

    #Generate database:
    generate_tables(dbt)
    insert_data(dbt)
    populate_max(dbt)

    db_disconnect(cnxn, cursor)
    logging.info("DB connection CLOSED")
    logging.info("PROCESS COMPLETED!")
    return 0

#MAIN:
create_db(drop=False)
