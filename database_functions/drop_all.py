import pyodbc
from db_connect import db_connect, db_disconnect

def drop_all():
    # open connection
    cnxn, cursor = db_connect()

    cursor.execute('DROP TABLE Warnings')
    cnxn.commit()
    cursor.execute('DROP TABLE WarningDesc')
    cnxn.commit()
    cursor.execute('DROP TABLE CombosData')
    cnxn.commit()
    cursor.execute('DROP TABLE PressateData')
    cnxn.commit()
    cursor.execute('DROP TABLE Pressate')
    cnxn.commit()
    cursor.execute('DROP TABLE Combos')
    cnxn.commit()
    cursor.execute('DROP TABLE Riduttori')
    cnxn.commit()

    #close cursor and connection
    db_disconnect(cnxn, cursor)

    print("All tables removed from database.")
    return 0

#MAIN:
if __name__ == '__main__':
    drop_all()
