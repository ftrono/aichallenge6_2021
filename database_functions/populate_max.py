import os
from db_connect import db_connect, db_disconnect

#Populate MaxForza and MaxAltezza fields in Pressate table

def populate_max():
    # open connection
    fields = ['Forza', 'Altezza']
    cnxn, cursor = db_connect()
    temp = {}

    for s in fields:
        #query data:
        cursor.execute('SELECT Timestamp, MAX('+s+') as Max'+s+' FROM PressateData GROUP BY TIMESTAMP')
        for row in cursor.fetchall():
            temp[row[0]] = float(row[1])
        cursor.commit()
        #set data:
        for k in temp.keys():
            cursor.execute('UPDATE Pressate SET Max'+s+' = ? WHERE Timestamp = ?', temp[k], k)
            cursor.commit()
        #reset:
        temp = {}

    #close cursor and connection
    db_disconnect(cnxn, cursor)
    return 0

#MAIN:
if __name__ == '__main__':
    populate_max()
