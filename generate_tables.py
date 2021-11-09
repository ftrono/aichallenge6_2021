import pyodbc
import textwrap

# use preferred connection method and parameters ---------------------------------
dsn = 'sqlserverdatasource'
user = 'SA'
password = 'MainPas012'
database = 'NovoticAI'
con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn, user, password, database)
#---------------------------------------------------------------------------------
cnxn = pyodbc.connect(con_string)

riduttori     = "CREATE TABLE Riduttori(RiduttoreID BIGINT NOT NULL PRIMARY KEY, Master BIT NOT NULL, Taglia VARCHAR(5), Cd TINYINT, Stadi BIT, Rapporto TINYINT);"
combos        = "CREATE TABLE Combos(ComboID CHAR(10) NOT NULL PRIMARY KEY, Taglia CHAR(5) NOT NULL, IdComp CHAR(5) NOT NULL, TargetMA DECIMAL(5) NOT NULL, TargetMF DECIMAL(5) NOT NULL, StdMA DECIMAL(5) NOT NULL, StdMF DECIMAL(5) NOT NULL, StdCurve DECIMAL(5) NOT NULL)"
combos_data   = "CREATE TABLE CombosData(ID INT NOT NULL IDENTITY PRIMARY KEY, ComboID CHAR(10) NOT NULL FOREIGN KEY REFERENCES Combos (ComboID) ON DELETE CASCADE ON UPDATE CASCADE, Forza DECIMAL(5) NOT NULL, Altezza DECIMAL(5) NOT NULL)"
pressate      = "CREATE TABLE Pressate(Timestamp BIGINT NOT NULL PRIMARY KEY, RiduttoreID BIGINT NOT NULL FOREIGN KEY REFERENCES Riduttori (RiduttoreID) ON DELETE CASCADE ON UPDATE CASCADE, ComboID CHAR(10) NOT NULL FOREIGN KEY REFERENCES Combos (ComboID), Stazione CHAR(2), MaxForza DECIMAL(5) NOT NULL, MaxAltezza DECIMAL(5) NOT NULL)"
pressate_data = "CREATE TABLE PressateData(ID INT NOT NULL IDENTITY PRIMARY KEY, Timestamp BIGINT NOT NULL FOREIGN KEY REFERENCES Pressate (Timestamp) ON DELETE CASCADE ON UPDATE CASCADE, Forza DECIMAL(5) NOT NULL, Altezza DECIMAL(5) NOT NULL)"
warning_desc  = "CREATE TABLE WarningDesc(WarningID INT NOT NULL IDENTITY PRIMARY KEY, Description NTEXT)"
warnings      = "CREATE TABLE Warnings(ID INT NOT NULL IDENTITY PRIMARY KEY, Timestamp BIGINT NOT NULL FOREIGN KEY REFERENCES Pressate (Timestamp) ON DELETE CASCADE ON UPDATE CASCADE, WarningID INT NOT NULL FOREIGN KEY REFERENCES WarningDesc (WarningID) ON DELETE CASCADE ON UPDATE CASCADE)"

cursor = cnxn.cursor() 

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


cursor.close() 
cnxn.close() 