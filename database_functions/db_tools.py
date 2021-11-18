import logging
#KEY DB FUNCTIONS:
# - reset_table()
# - drop_all()
# - generate_tables()
# - populate_max()

#reset a specific table:
def reset_table(dbt, tablename):
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logger=logging.getLogger('general')
    try:
        query = "TRUNCATE TABLE "+tablename
        cursor.execute(query)
        cnxn.commit()
        print("Table "+tablename+" successfully reset.")
    except:
        logger.error("Unable to reset "+tablename+" table.")
    return 0


#remove ALL tables:
def drop_all(dbt):
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logger=logging.getLogger('general')
    error=False
    tables = ['Warnings', 'WarningDesc', 'CombosData', 'PressateData', 'Pressate', 'Combos', 'Riduttori']
    for t in tables:
        try:
            query = 'DROP TABLE '+ t
            cursor.execute(query)
            cnxn.commit()
        except:
            logger.error("Unable to drop table "+t)
            error=True
    if not error:
        logger.info("Dropped all tables")
    return 0


#generate tables:
def generate_tables(dbt):
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logger=logging.getLogger('general')
    # query strings
    riduttori     = "CREATE TABLE Riduttori(RiduttoreID BIGINT NOT NULL PRIMARY KEY, Master BIT NOT NULL, Taglia CHAR(5) NOT NULL, Cd TINYINT NOT NULL, Stadi BIT NOT NULL, Rapporto TINYINT NOT NULL);"
    combos        = "CREATE TABLE Combos(ComboID CHAR(10) NOT NULL PRIMARY KEY, Taglia CHAR(5) NOT NULL, IdComp CHAR(5) NOT NULL, TargetMA DECIMAL(5, 2) NOT NULL, TargetMF DECIMAL(5,2) NOT NULL, StdMA DECIMAL(5,2) NOT NULL, StdMF DECIMAL(5, 2) NOT NULL, StdCurveAvg DECIMAL(5,2) NOT NULL)"
    combos_data   = "CREATE TABLE CombosData(ID INT NOT NULL IDENTITY PRIMARY KEY, ComboID CHAR(10) NOT NULL FOREIGN KEY REFERENCES Combos (ComboID) ON DELETE CASCADE ON UPDATE CASCADE, Forza DECIMAL(5, 2) NOT NULL, Altezza DECIMAL(5, 2) NOT NULL, Std DECIMAL(5, 2) NOT NULL)"
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
            logger.error("IN "+q)
            error=True
    if not error:
        logger.info("Created all tables")
    return 0


#Populate MaxForza and MaxAltezza fields in Pressate table:
def populate_max(dbt):
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logger=logging.getLogger('general')
    n=175494
    ins=0
    logger.info("Start max values population in table Pressate")
    cursor.execute('SELECT Timestamp, MAX(Forza) as MaxF, MAX(Altezza) as MaxA FROM PressateData GROUP BY TIMESTAMP')
    for row in cursor.fetchall():
        cursor.execute('UPDATE Pressate SET MaxForza = ? , MaxAltezza =? WHERE Timestamp = ?',row[1],row[2],row[0])
        ins+=1
        logger.debug("Update: %s/%s"%(str(ins),str(n)))        
    cursor.commit()
    logger.info("Max values populated")
    return 0
