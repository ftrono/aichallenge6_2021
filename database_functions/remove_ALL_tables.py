import pyodbc

# use preferred connection method and parameters ---------------------------------
driver = '{ODBC Driver 17 for SQL Server}'
server = 'localhost'
database = 'NovoticAI'
username = 'sa'
password = 'AIchallenge6'

con_string = 'DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
#---------------------------------------------------------------------------------

# open connection
cnxn = pyodbc.connect(con_string)
print("Connected to", server)

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