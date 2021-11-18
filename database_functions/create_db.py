from db_tools import drop_all, generate_tables, populate_max
from db_connect import db_connect, db_disconnect
from insert_data import insert_data
import logging #,telegram_send



#CREATE DB (DROP & REPOPULATE ALL TABLES):
def create_db(drop=False,limit=1000000):
    status_log=logging.getLogger('status')
    general_log=logging.getLogger('general')
    hdlr1=logging.FileHandler('status.log',mode='w')
    hdlr2=logging.FileHandler('./logs/insert.log',mode='w')
    hdlr2.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    general_log.setLevel(logging.DEBUG)
    status_log.setLevel(logging.INFO)
    status_log.addHandler(hdlr1)
    general_log.addHandler(hdlr2)
    general_log.info("DB connection OPENED")
    cnxn, cursor = db_connect()

    #DB tools:
    dbt = {'cnxn': cnxn, 'cursor': cursor}
    
    if drop == True:
        drop_all(dbt)

    #Generate database:
    generate_tables(dbt)
    #telegram_send.send(messages=["Import process started"])
    insert_data(dbt,limit)
    #telegram_send.send(messages=["Started populating max"])
    populate_max(dbt)
    #telegram_send.send(messages=["Completed db population"])
    db_disconnect(cnxn, cursor)
    general_log.info("DB connection CLOSED")
    general_log.info("PROCESS COMPLETED!")
    #telegram_send.send(messages=["Process stopped"])
    return 0

#MAIN:
if __name__ == '__main__':
    create_db(drop=True,limit=1000)
