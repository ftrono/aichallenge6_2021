from db_connect import db_connect, db_disconnect
import pyodbc


# open connection
cnxn, cursor = db_connect()

# query strings
riduttori     = "CREATE TABLE Riduttori(RiduttoreID BIGINT NOT NULL PRIMARY KEY, Master BIT NOT NULL, Taglia CHAR(5) NOT NULL, Cd TINYINT NOT NULL, Stadi BIT NOT NULL, Rapporto TINYINT NOT NULL);"
combos        = "CREATE TABLE Combos(ComboID CHAR(10) NOT NULL PRIMARY KEY, Taglia CHAR(5) NOT NULL, IdComp CHAR(5) NOT NULL, TargetMA DECIMAL(5) NOT NULL, TargetMF DECIMAL(5,2) NOT NULL, StdMA DECIMAL(5,2) NOT NULL, StdMF DECIMAL(5) NOT NULL, StdCurve DECIMAL(5,2) NOT NULL)"
combos_data   = "CREATE TABLE CombosData(ID INT NOT NULL IDENTITY PRIMARY KEY, ComboID CHAR(10) NOT NULL FOREIGN KEY REFERENCES Combos (ComboID) ON DELETE CASCADE ON UPDATE CASCADE, Forza DECIMAL(5) NOT NULL, Altezza DECIMAL(5) NOT NULL)"
pressate      = "CREATE TABLE Pressate(Timestamp BIGINT NOT NULL PRIMARY KEY, RiduttoreID BIGINT NOT NULL FOREIGN KEY REFERENCES Riduttori (RiduttoreID) ON DELETE CASCADE ON UPDATE CASCADE, ComboID CHAR(10) NOT NULL FOREIGN KEY REFERENCES Combos (ComboID), Stazione CHAR(2) NOT NULL, MaxForza DECIMAL(5) NOT NULL, MaxAltezza DECIMAL(5) NOT NULL)"
pressate_data = "CREATE TABLE PressateData(ID INT NOT NULL IDENTITY PRIMARY KEY, Timestamp BIGINT NOT NULL FOREIGN KEY REFERENCES Pressate (Timestamp) ON DELETE CASCADE ON UPDATE CASCADE, Forza DECIMAL(5,2) NOT NULL, Altezza DECIMAL(5,2) NOT NULL)"
warning_desc  = "CREATE TABLE WarningDesc(WarningID INT NOT NULL IDENTITY PRIMARY KEY, Description NTEXT NOT NULL)"
warnings      = "CREATE TABLE Warnings(ID INT NOT NULL IDENTITY PRIMARY KEY, Timestamp BIGINT NOT NULL FOREIGN KEY REFERENCES Pressate (Timestamp) ON DELETE CASCADE ON UPDATE CASCADE, WarningID INT NOT NULL FOREIGN KEY REFERENCES WarningDesc (WarningID) ON DELETE CASCADE ON UPDATE CASCADE)"


# execute queries
cursor.execute(riduttori)
cnxn.commit()
cursor.execute(combos)
cnxn.commit() 
cursor.execute(combos_data)
cnxn.commit()
cursor.execute(pressate)
cnxn.commit()
cursor.execute(pressate_data)
cnxn.commit()
cursor.execute(warning_desc)
cnxn.commit()
cursor.execute(warnings)
cnxn.commit()

#close cursor and connection
db_disconnect(cnxn, cursor)
