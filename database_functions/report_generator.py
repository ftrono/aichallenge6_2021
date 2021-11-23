from database_functions.db_connect import db_connect, db_disconnect
from export.export_to_csv import save_table_csv
import pandas as pd

# connect
conn, cursor = db_connect()

query = ("SELECT Pressate.RiduttoreID, Pressate.ComboID, Pressate.MaxForza, Pressate.MaxAltezza, Warnings.WarningID FROM (Pressate INNER JOIN Warning ON Warnings.RiduttoreID = Pressate.RiduttoreID)")




# disconnect
db_connect(conn, cursor)
