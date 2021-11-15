import sys
from matplotlib.pyplot import get
sys.path.insert(0, './')
from utils import write_warning
from database_functions.db_connect import db_connect, db_disconnect


def train(sigma):
    '''
    Function that check if MaxAltezza is out if the bounds. 
    Bounds = Target max altezza + - deviation.
    deviation = sigma * target max altezza

    Input:
    - Sigma: int

    Output:
    - Write on db if there is warning: warning 1

    ''' 
    conn, cursor = db_connect()

    #extract Timestamp, ComboID and MaxAltezza from Table Pressate and save in a list
    get_data = 'SELECT ComboID, Timestamp, MaxAltezza FROM Pressate'
    cursor.execute(get_data)
    list = cursor.fetchall()

    #extract ComboID, Target Max altezza and standard deviation max Altezza from Table Combos and save in a list (list_target)
    get_target = 'SELECT ComboID, TargetMA, StdMA FROM Combos'
    cursor.execute(get_target)
    list_target = cursor.fetchall()

    cursor.commit()

    #CHECK id Max Altezza is out of the bounds
    for e in list:
        for l in list_target:
            if e[0] == l[0]:
                dev = l[1]*sigma
                if (e[2] > (l[1]+ dev)) or (e[2] < (l[1]- dev)):
                    write_warning(e[1],1)
    # Disconnect
    db_disconnect(conn, cursor)

    

#MAIN:
if __name__ == '__main__':
    train(1)
