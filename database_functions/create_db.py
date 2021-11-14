import sys
sys.path.insert(0, './')
from training.set_targets import set_targets_ma, set_targets_mf

#CREATE DB (DROP & REPOPULATE ALL TABLES):
def create_db(drop=False):
    if drop == True:
        exec(open("./database_functions/remove_ALL_tables.py").read())

    #Generate database:
    exec(open("./database_functions/generate_tables.py").read())
    exec(open("./database_functions/insert_data.py").read())
    exec(open("./database_functions/populate_max.py").read())
    set_targets_ma()
    set_targets_mf()

#MAIN:
create_db(drop=True)
