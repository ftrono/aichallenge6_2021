from db_tools import drop_all, generate_tables, populate_max
from insert_data import insert_data
import sys
sys.path.insert(0, './')
from training.training_tools import set_targets_max

#CREATE DB (DROP & REPOPULATE ALL TABLES):
def create_db(drop=False):
    if drop == True:
        try:
            drop_all()
        except:
            print("Drop warning: DB already empty.")

    print("Generating new DB...")
    #Generate database:
    generate_tables()
    insert_data()
    populate_max()
    set_targets_max(mtype='altezza')
    set_targets_max(mtype='forza')

    print("DB created.")
    return 0

#MAIN:
create_db(drop=True)
