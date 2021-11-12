import pyodbc

#CONNECTION / DISCONNECTION FUNCTIONS TO DB:

# use preferred connection method and parameters ---------------------------------
driver = '{ODBC Driver 17 for SQL Server}'
database = 'NovoticAI'
server = '127.0.0.1' 
username = 'sa' 
password = 'AIchallenge6'
con_string = 'DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
#---------------------------------------------------------------------------------

#DB utils:
def db_connect(con_string):
    conn = pyodbc.connect(con_string)
    cursor = conn.cursor()
    return conn, cursor

def db_disconnect(conn, cursor):
    cursor.close()
    conn.close()

#Sample use:
#conn, cursor = db_connect(con_string)
#db_disconnect(conn, cursor)
