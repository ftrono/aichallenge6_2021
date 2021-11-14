from drop_all import drop_all
from generate_tables import generate_tables
from insert_data import insert_data
from populate_max import populate_max
import sys
sys.path.insert(0, './')
from training.set_targets import set_targets_ma, set_targets_mf

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
    set_targets_ma()
    set_targets_mf()

    print("DB created.")
    return 0

#MAIN:
create_db(drop=True)
