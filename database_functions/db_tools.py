from db_connect import db_connect, db_disconnect

#KEY DB FUNCTIONS:
# - drop_all()
# - generate_tables()
# - populate_max()

#remove ALL tables:
def drop_all():
    cnxn, cursor = db_connect()

    tables = ['Warnings', 'WarningDesc', 'CombosData', 'PressateData', 'Pressate', 'Combos', 'Riduttori']
    for t in tables:
        cursor.execute('DROP TABLE ?', t)
        cnxn.commit()
    
    db_disconnect(cnxn, cursor)
    print("All tables removed from database.")
    return 0


#generate tables:
def generate_tables():
    # open connection
    cnxn, cursor = db_connect()

    # query strings
    riduttori     = "CREATE TABLE Riduttori(RiduttoreID BIGINT NOT NULL PRIMARY KEY, Master BIT NOT NULL, Taglia CHAR(5) NOT NULL, Cd TINYINT NOT NULL, Stadi BIT NOT NULL, Rapporto TINYINT NOT NULL);"
    combos        = "CREATE TABLE Combos(ComboID CHAR(10) NOT NULL PRIMARY KEY, Taglia CHAR(5) NOT NULL, IdComp CHAR(5) NOT NULL, TargetMA DECIMAL(5, 2) NOT NULL, TargetMF DECIMAL(5,2) NOT NULL, StdMA DECIMAL(5,2) NOT NULL, StdMF DECIMAL(5, 2) NOT NULL, StdCurve DECIMAL(5,2) NOT NULL)"
    combos_data   = "CREATE TABLE CombosData(ID INT NOT NULL IDENTITY PRIMARY KEY, ComboID CHAR(10) NOT NULL FOREIGN KEY REFERENCES Combos (ComboID) ON DELETE CASCADE ON UPDATE CASCADE, Forza DECIMAL(5, 2) NOT NULL, Altezza DECIMAL(5, 2) NOT NULL)"
    pressate      = "CREATE TABLE Pressate(Timestamp BIGINT NOT NULL PRIMARY KEY, RiduttoreID BIGINT NOT NULL FOREIGN KEY REFERENCES Riduttori (RiduttoreID) ON DELETE CASCADE ON UPDATE CASCADE, ComboID CHAR(10) NOT NULL FOREIGN KEY REFERENCES Combos (ComboID), Stazione CHAR(2) NOT NULL, MaxForza DECIMAL(5, 2) NOT NULL, MaxAltezza DECIMAL(5, 2) NOT NULL)"
    pressate_data = "CREATE TABLE PressateData(ID INT NOT NULL IDENTITY PRIMARY KEY, Timestamp BIGINT NOT NULL FOREIGN KEY REFERENCES Pressate (Timestamp) ON DELETE CASCADE ON UPDATE CASCADE, Forza DECIMAL(5,2) NOT NULL, Altezza DECIMAL(5, 2) NOT NULL)"
    warning_desc  = "CREATE TABLE WarningDesc(WarningID INT NOT NULL IDENTITY PRIMARY KEY, Description NTEXT NOT NULL)"
    warnings      = "CREATE TABLE Warnings(ID INT NOT NULL IDENTITY PRIMARY KEY, Timestamp BIGINT NOT NULL FOREIGN KEY REFERENCES Pressate (Timestamp) ON DELETE CASCADE ON UPDATE CASCADE, WarningID INT NOT NULL FOREIGN KEY REFERENCES WarningDesc (WarningID) ON DELETE CASCADE ON UPDATE CASCADE)"

    # execute queries
    queries = [riduttori, combos, combos_data, pressate, pressate_data, warning_desc, warnings]
    for q in queries:
        cursor.execute(q)
        cnxn.commit()

    #close cursor and connection
    db_disconnect(cnxn, cursor)
    return 0


#Populate MaxForza and MaxAltezza fields in Pressate table:
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
    generate_tables()
    populate_max()
