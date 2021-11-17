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
    
    if drop == True:
        drop_all(cnxn,cursor,logging)

    #Generate database:
    generate_tables(cnxn,cursor,logging)

    insert_data(cnxn,cursor,logging)

    populate_max(cnxn,cursor,logging)

    db_disconnect(cnxn, cursor)
    logging.info("DB connection CLOSED")
    logging.info("PROCESS COMPLETED!")
    return 0

#MAIN:
create_db(drop=True)
