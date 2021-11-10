import csv
import time
import logging
from utils import name_parser
import pyodbc

logging.basicConfig(level=logging.DEBUG)
logging.debug("START")
# use preferred connection method and parameters ---------------------------------
dsn = 'sqlserverdatasource'
user = 'SA'
password = 'MainPas012'
database = 'NovoticAI'
con_string = 'DSN=%s;UID=%s;PWD=%s;DATABASE=%s;' % (dsn, user, password, database)
#---------------------------------------------------------------------------------

# open connection
cnxn = pyodbc.connect(con_string)
cursor = cnxn.cursor() 
logging.debug("Connected to DB")



start_time = time.time()
produzione=dict()
with open('./Summary.csv', mode='r') as summary:
    # read csv as dictionary
    summary_reader = csv.DictReader(summary,delimiter=',') 
    line_count = 0 # initialize line counter

    # iterate over rows in summary
    for row in summary_reader:
        if line_count > 0: # skip first row (colum names)
            prev_key=""
            if prev_key!=row["Tempcode"]: # check if riduttore has already been saved
                cursor.execute("INSERT INTO Riduttori VALUES (" + row["Tempcode"] + "," + row["Master"] + "," + row["Taglia"] + "," + row["CD"] + "," + row["Stadi"] + "," + row["Rapporto"] + ")")
                cnxn.commit()
            with open(row["CSVpath"].replace('\\','/')) as pressata_csv_file: # open pressata csv (need to replace \ with normal /)
                tmp = csv.reader(pressata_csv_file,delimiter=';') # read csv as csv (each row is an array)
                t_line_count=0 # initialize secondary row counter
                for t_row in tmp: # iterate over rows in pressata csv
                    if t_line_count==0: 
                        tempcode,id,stazione,timestamp=name_parser(row["CSVname"]) # get informations form file name
                        cursor.execute("INSERT INTO Pressate VALUES (" + timestamp + "," + row["Tempcode"] + "," + row["Master"] + "," + row["Taglia"] + "," + row["CD"] + "," + row["Stadi"] + "," + row["Rapporto"] + ")")
                        cnxn.commit()
                        pressata=Pressata(id,stazione,timestamp) # generate instance of pressata
                    elif t_line_count>2: # skip first 3 rows
                        try: 
                            pressata.add_value(t_row[2].replace(',','.'),t_row[3].replace(',','.')) # add value to serie in pressata
                        except: # handle exception due to malformed rows
                            #print(str(row["CSVpath"])+" Unable to add value at line "+str(t_line_count+1) + " " + str(t_row))
                            f.write(str(row["CSVpath"])+" Unable to add value at line "+str(t_line_count+1)+" " + str(t_row)+"\n")
                    t_line_count+=1
                try:
                    pressata.set_max_values()
                except:
                    print(str(row["CSVpath"])+" Unable to compute maximum values vectors are empty")
                    f.write(str(row["CSVpath"])+" Unable to compute maximum values vectors are empty\n")
                    cmd='rm /home/azureadmin/main/' + str(row["CSVpath"]).replace('\\','/')
                    #os.system(cmd)
                produzione[row["Tempcode"]].add_step(pressata) # add pressata to instance of riduttore
        line_count+=1   
    f.close() 
    print("Import from csv completed.")
    print("Connecting...")
    db,client=mongo_connect()
    print("Connection enstablished.\nStarting DB population...")
    for document in produzione.values():
        result=db.test2.insert_one(document.to_json())
        #print('Inserted document {}'.format(result.inserted_id))
    mongo_disconnect(client)
print("Process completed in: %s seconds" % (time.time() - start_time)) # print execution time 



