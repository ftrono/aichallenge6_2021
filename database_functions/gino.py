from db_connect import db_connect, db_disconnect

cnxn, cursor = db_connect()

cursor.execute("UPDATE WarningDesc SET Description = 'Pressata: max_altezza out of bounds' WHERE WarningID = ?", 1)
cursor.execute("UPDATE WarningDesc SET Description = 'Riduttore: incorrect number of pressate' WHERE WarningID = ?", 2)
cursor.execute("UPDATE WarningDesc SET Description = 'Pressata: max_forza out of bounds' WHERE WarningID = ?", 3)
cursor.execute("UPDATE WarningDesc SET Description = 'Pressata: force curve out of bounds' WHERE WarningID = ?", 4)
cursor.commit()
print("WarningDesc populated")

db_disconnect(cnxn, cursor)
