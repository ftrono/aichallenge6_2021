#KEY DB FUNCTIONS:
# - reset_warnings()
# - drop_all()
# - generate_tables()
# - populate_max()

#reset Warnings table:
def reset_warnings(cnxn, cursor):
    cursor.execute("TRUNCATE TABLE Warnings")
    cnxn.commit()
    print("Table Warnings successfully reset.")
    return 0


#remove ALL tables:
def drop_all(cnxn,cursor,logging):
    error=False
    tables = ['Warnings', 'WarningDesc', 'CombosData', 'PressateData', 'Pressate', 'Combos', 'Riduttori']
    for t in tables:
        try:
            query = 'DROP TABLE '+ t
            cursor.execute(query)
            cnxn.commit()
        except:
            logging.error("Unable to drop table "+t)
            error=True
    if not error:
        logging.info("Dropped all tables")
    return 0


#generate tables:
def generate_tables(cnxn,cursor,logging):
    # query strings
    riduttori     = "CREATE TABLE Riduttori(RiduttoreID BIGINT NOT NULL PRIMARY KEY, Master BIT NOT NULL, Taglia CHAR(5) NOT NULL, Cd TINYINT NOT NULL, Stadi BIT NOT NULL, Rapporto TINYINT NOT NULL);"
    combos        = "CREATE TABLE Combos(ComboID CHAR(10) NOT NULL PRIMARY KEY, Taglia CHAR(5) NOT NULL, IdComp CHAR(5) NOT NULL, TargetMA DECIMAL(5, 2) NOT NULL, TargetMF DECIMAL(5,2) NOT NULL, StdMA DECIMAL(5,2) NOT NULL, StdMF DECIMAL(5, 2) NOT NULL, StdCurve DECIMAL(5,2) NOT NULL)"
    combos_data   = "CREATE TABLE CombosData(ID INT NOT NULL IDENTITY PRIMARY KEY, ComboID CHAR(10) NOT NULL FOREIGN KEY REFERENCES Combos (ComboID) ON DELETE CASCADE ON UPDATE CASCADE, Forza DECIMAL(5, 2) NOT NULL, Altezza DECIMAL(5, 2) NOT NULL)"
    pressate      = "CREATE TABLE Pressate(Timestamp BIGINT NOT NULL PRIMARY KEY, RiduttoreID BIGINT NOT NULL FOREIGN KEY REFERENCES Riduttori (RiduttoreID) ON DELETE CASCADE ON UPDATE CASCADE, ComboID CHAR(10) NOT NULL FOREIGN KEY REFERENCES Combos (ComboID), Stazione CHAR(2) NOT NULL, MaxForza DECIMAL(5, 2) NOT NULL, MaxAltezza DECIMAL(5, 2) NOT NULL)"
    pressate_data = "CREATE TABLE PressateData(ID INT NOT NULL IDENTITY PRIMARY KEY, Timestamp BIGINT NOT NULL FOREIGN KEY REFERENCES Pressate (Timestamp) ON DELETE CASCADE ON UPDATE CASCADE, Forza DECIMAL(5,2) NOT NULL, Altezza DECIMAL(5, 2) NOT NULL)"
    warning_desc  = "CREATE TABLE WarningDesc(WarningID INT NOT NULL IDENTITY PRIMARY KEY, Description NTEXT NOT NULL)"
    warnings      = "CREATE TABLE Warnings(ID INT NOT NULL IDENTITY PRIMARY KEY, RiduttoreID BIGINT NOT NULL FOREIGN KEY REFERENCES Riduttori (RiduttoreID) ON DELETE CASCADE ON UPDATE CASCADE, Timestamp BIGINT FOREIGN KEY REFERENCES Pressate (Timestamp), WarningID INT NOT NULL FOREIGN KEY REFERENCES WarningDesc (WarningID) ON DELETE CASCADE ON UPDATE CASCADE)"

    # execute queries
    queries = [riduttori, combos, combos_data, pressate, pressate_data, warning_desc, warnings]
    error=False
    for q in queries:
        try:
            cursor.execute(q)
            cnxn.commit()
        except:
            logging.error("IN "+q)
            error=True
    if not error:
        logging.info("Created all tables")
    return 0


#Populate MaxForza and MaxAltezza fields in Pressate table:
def populate_max(cnxn,cursor,logging):
    n=175494
    ins=0
    logging.info("Start max values population in table Pressate")
    cursor.execute('SELECT Timestamp, MAX(Forza) as MaxF, MAX(Altezza) as MaxA FROM PressateData GROUP BY TIMESTAMP')
    for row in cursor.fetchall():
        cursor.execute('UPDATE Pressate SET MaxForza = ? , MaxAltezza =? WHERE Timestamp = ?',row[1],row[2],row[0])
        ins+=1
        logging.debug("Update: %s/%s"%(str(ins),str(n)))        
    cursor.commit()
    logging.info("Max values populated")
    return 0


#MAIN:
if __name__ == '__main__':
    #drop_all()
    #generate_tables()
    #populate_max()
    reset_warnings()
