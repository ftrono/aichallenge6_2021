import logging
import pandas as pd

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
        logger.error("ERROR: unable to reset "+tablename+" table.")
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


#reset Evaluated marks in Pressate table:
def reset_marks(dbt, remark=False):
    '''
    Modes:
    - all=True -> resets all marks to zero
    - all=False -> resets all marks to zero and marks again the timestamps for which a warning was found.
    '''
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    log = dbt['logging']

    #1) reset whole Evaluated column:
    log.info("Resetting Evaluated marks")
    try:
        cursor.execute("UPDATE Pressate SET Evaluated = DEFAULT")
        cnxn.commit()
        log.info("Evaluated marks reset.")
        print("Evaluated marks reset.")
    except:
        log.error("Error: Evaluated marks not reset.")
        print("Error: Evaluated marks not reset.")
    
    #2) remarking Timestamps with a Warning:
    if remark == True:
        log.info("Remarking the timestamps with a warning as Evaluated")
        query = "SELECT Pressate.Timestamp FROM Pressate INNER JOIN Warnings ON Pressate.Timestamp = Warnings.Timestamp"
        pressate_tomark = pd.read_sql(query, cnxn)
        pressate_tomark = pressate_tomark['Timestamp'].tolist()
        sets_tomark = [(1, int(p)) for p in pressate_tomark]
        
        #Bulk remark all timestamps with a Warning to SQL DB:
        try:
            cursor.fast_executemany = True
            cursor.executemany("UPDATE Pressate SET Evaluated = ? WHERE Timestamp = ?", sets_tomark)
            cnxn.commit()
            log.info("Stored Evaluated marks for Pressate with warnings into DB.")
            print("Stored Evaluated marks for Pressate with warnings into DB.")
        except:
            log.error("Insert error: Evaluated marks not stored to DB. Please retry later.")
            print("Insert error: Evaluated marks not stored to DB. Please retry later.")

    return 0


#generate tables:
def generate_tables(dbt):
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    logger=logging.getLogger('general')
    # query strings
    riduttori     = "CREATE TABLE Riduttori(RiduttoreID BIGINT NOT NULL PRIMARY KEY, Master TINYINT NOT NULL, Taglia CHAR(5) NOT NULL, Cd DECIMAL(5,3) NOT NULL, Stadi TINYINT NOT NULL, Rapporto TINYINT NOT NULL);"
    combos        = "CREATE TABLE Combos(ComboID CHAR(13) NOT NULL PRIMARY KEY, Taglia CHAR(5) NOT NULL, IdComp CHAR(5) NOT NULL, TargetMA DECIMAL(5, 2) NOT NULL, TargetMF DECIMAL(5,2) NOT NULL, StdMA DECIMAL(5,2) NOT NULL, StdMF DECIMAL(5, 2) NOT NULL, StdCurveAvg DECIMAL(5,2) NOT NULL)"
    combos_data   = "CREATE TABLE CombosData(ID INT NOT NULL IDENTITY PRIMARY KEY, ComboID CHAR(13) NOT NULL FOREIGN KEY REFERENCES Combos (ComboID) ON DELETE CASCADE ON UPDATE CASCADE, Forza DECIMAL(5, 2) NOT NULL, Altezza DECIMAL(5, 2) NOT NULL, Std DECIMAL(5, 2) NOT NULL)"
    pressate      = "CREATE TABLE Pressate(Timestamp BIGINT NOT NULL PRIMARY KEY, RiduttoreID BIGINT NOT NULL FOREIGN KEY REFERENCES Riduttori (RiduttoreID) ON DELETE CASCADE ON UPDATE CASCADE, ComboID CHAR(13) NOT NULL FOREIGN KEY REFERENCES Combos (ComboID), Stazione CHAR(2) NOT NULL, MaxForza DECIMAL(5, 2) NOT NULL, MaxAltezza DECIMAL(5, 2) NOT NULL, Evaluated BIT NOT NULL DEFAULT 0)"
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
    logger.info("Start max values population in table Pressate")
    cursor.execute('SELECT Timestamp, MAX(Forza) as MaxF, MAX(Altezza) as MaxA FROM PressateData GROUP BY TIMESTAMP')
    sets_max = []
    for row in cursor.fetchall():
        sets_max.append((float(row[1]),float(row[2]),int(row[0])))
    #Bulk store all accumulated MaxForza and MaxAltezza to SQL DB:
    try:
        cursor.fast_executemany = True
        cursor.executemany('UPDATE Pressate SET MaxForza = ? , MaxAltezza =? WHERE Timestamp = ?', sets_max)
        cnxn.commit()
        logger.info("Success: stored MaxForza and MaxAltezza for all Pressate into DB.")
    except:
        logger.error("Insert error: MaxForza and MaxAltezza not stored to DB. Please relaunch populate_max().") 
    return 0
