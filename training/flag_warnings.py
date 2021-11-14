import set_targets
from utils import write_warning
from database_functions.db_connect import db_connect, db_disconnect

# Connect
conn, cursor = db_connect()

# Pairwise Delta
def delta_timestamp(array):
    '''
    Performs pairwise delta of the elements contained into a list
    param: array: list of tuples in the form (RiduttoreID, Timestamp).
    return: list of pairwise deltas
    '''
    n = 0
    deltas = list()
    while n < (len(array)-1):
        m = n + 1
        while m < len(array):
            deltas.append(abs(array[n][0] - array[m][0]))
            m += 1
        n += 1
    return deltas






# Get unique comboIDs from table Pressata
cursor.execute("SELECT DISTINCT ComboID FROM Pressate")
comboIDs = cursor.fetchall()

for comb_id in comboIDs:
    cursor.execute("SELECT RiduttoreID, COUNT(Timestamp) FROM Pressate WHERE ComboID = ? GROUP BY RiduttoreID", comb_id[0])
    filtered_table = cursor.fetchall()  # list of tuples: (RiduttoreID, TimestampNum)

    for rid_id, tmstp_num in filtered_table:
        if tmstp_num > 3:
            cursor.execute("SELECT Timestamp FROM Pressate WHERE ComboID = ? AND RiduttoreID = ?", comb_id[0], rid_id)
            timestamps = cursor.fetchall()
            # Pairwise Delta
            deltas = delta_timestamp(timestamps)
            print(deltas)



# Disconnect
db_disconnect(conn, cursor)




