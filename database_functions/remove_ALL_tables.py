import pyodbc

# use preferred connection method and parameters ---------------------------------
dsn = 'sqlserverdatasource'
user = 'SA'
password = 'MainPas012'
database = 'NovoticAI'
con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn, user, password, database)

#---------------------------------------------------------------------------------

# open connection
cnxn = pyodbc.connect(con_string)


cursor = cnxn.cursor()

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




# close cursor and connection
cursor.close()
cnxn.close()

print("All tables removed from database", database)