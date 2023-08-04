import pyodbc, os, configparser

#CONNECTION / DISCONNECTION FUNCTIONS TO DB


#open connection:
def db_connect():
    config = configparser.ConfigParser()

    #read the config file:
    config.read(os.getcwd()+"/database_functions/db_credentials.ini")
    db = config['DB']

    #build conn string:
    # if db.get('auth') != '':
    #     # use azure AD
    #     con_string = 'DRIVER=%s;SERVER=%s;DATABASE=%s;UID=%s;PWD=%s;Authentication=%s;ENCRYPT=%s' % (db.get('driver'), db.get('server'), db.get('database'), db.get('user'), db.get('password'), db.get('auth'), db.get('encrypt'))
    # el
    if db.get('dsn') != '':
        #use dsn:
        con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;ENCRYPT=%s' % (db.get('dsn'), db.get('user'), db.get('password'), db.get('database'), db.get('encrypt')) 
    else:
        #no dsn: use driver & server:
        con_string = 'DRIVER=%s;SERVER=%s;DATABASE=%s;UID=%s;PWD=%s;ENCRYPT=%s;' % (db.get('driver'), db.get('server'), db.get('database'), db.get('user'), db.get('password'), db.get('encrypt'))
        
    #open connection:
    conn = pyodbc.connect(con_string)
    cursor = conn.cursor()
    return conn, cursor


#close connection:
def db_disconnect(conn, cursor):
    cursor.close()
    conn.close()



#SAMPLE USE:
#conn, cursor = db_connect()
#db_disconnect(conn, cursor)
