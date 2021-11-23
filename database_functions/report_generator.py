from database_functions.db_connect import db_connect, db_disconnect
from export.export_to_csv import save_table_csv
import pandas as pd

# connect
conn, cursor = db_connect()

query = ("SELECT Pressate.RiduttoreID, Pressate.ComboID, Pressate.MaxForza, Pressate.MaxAltezza, Warnings.WarningID FROM (Pressate INNER JOIN Warnings ON Warnings.RiduttoreID = Pressate.RiduttoreID)")
# save query as dataframe
df = pd.read_sql(query, conn)
# 1. raggruppare per riduttore
# 2. creare csv (per ciascun riduttore)
# 3. inserire dati raggruppati per combo
# 4. | Combo | ... | Warning | Warning_description |
#    -----------------------------------------------
#    |       | ... |         |                     |
#    |       | ... |         |                     |
#    |       | ... |         |                     |
print(df)



# disconnect
db_disconnect(conn, cursor)
