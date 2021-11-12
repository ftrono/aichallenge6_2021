import pyodbc

#CONNECTION / DISCONNECTION FUNCTIONS TO DB:

#CONNECT TO: True=PRODUCTION; False=LOCALHOST
production = False

#DB connection parameters:
driver = '{ODBC Driver 17 for SQL Server}'
database = 'NovoticAI'
if production == True:
    #Novotic DB server address:
    server = ''
    username = 'sa' 
    password = 'AIchallenge6'
    authstr = ';Authentication=#####' #insert ActiveDirectoryPassword
else:
    #localhost:
    server = '127.0.0.1' 
    username = 'sa' 
    password = 'AIchallenge6'
    authstr = '' #leave empty

#DB utils:
def db_connect():
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password+authstr)
    cursor = conn.cursor()
    return conn, cursor

def db_disconnect(conn, cursor):
    cursor.close()
    conn.close()

#Sample use:
#conn, cursor = db_connect()
#db_disconnect(conn, cursor)
