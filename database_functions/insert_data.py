import csv
import time
import logging
import datetime
import pyodbc
import os

#CSV name parser:
def name_parser(name): # take as input the file name
    # get information from file name
    tempcode=name[0:14]
    id=name[14:19]
    stazione=name[21:23]
    date_time=datetime.datetime(int(name[24:28]), int(name[29:31]), int(name[32:34]),int(name[35:37]),int(name[38:40]),int(name[41:43])) # convert string to date obj
    timestamp=datetime.datetime.timestamp(date_time) # convert date object to timestamp
    return tempcode,id,stazione,timestamp

def parse_date(cell,name):
    anno=int("20"+cell[6:8])
    mese=int(cell[3:5])
    giorno=int(cell[0:2])
    ora=int(cell[9:11])
    minuto=int(cell[12:14])
    secondo=int(cell[15:17])
    date_time=datetime.datetime(anno,mese,giorno,ora,minuto,secondo) # convert string to date obj
    timestamp=datetime.datetime.timestamp(date_time) # convert date object to timestamp
    return timestamp

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s')
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
comboIDs=[]
with open(os.getcwd()+"/database_functions/Summary.csv", mode='r') as summary:
    # read csv as dictionary
    summary_reader = csv.DictReader(summary,delimiter=',') 
    line_count = 0 # initialize line counter

    # iterate over rows in summary
    prev_key=""
    for row in summary_reader:
        if line_count<1000:
            if line_count > 0: # skip first row (colum names)
                if row["Tempcode"]!=prev_key: # check if riduttore has already been saved
                    prev_key=row["Tempcode"]
                    # Store fields
                    RiduttoreID = row["Tempcode"]
                    Master      = row["Master"]
                    Taglia      = row["Taglia"]
                    Cd          = row["CD"]
                    Stadi       = row["Stadi"]
                    Rapporto    = row["Rapporto"]
                    # Insert query
                    query="INSERT INTO Riduttori (RiduttoreID,Master,Taglia,Cd,Stadi,Rapporto) VALUES (" + RiduttoreID + "," + Master + ",'" + Taglia + "'," + Cd + "," + Stadi + "," + Rapporto + ")"
                    cursor.execute(query)
                    #cnxn.commit()
                    logging.debug("Inserted Riduttore "+RiduttoreID)

                with open(os.getcwd()+"/database_functions/"+row["CSVpath"].replace('\\','/')) as pressata_csv_file: # open pressata csv (need to replace \ with normal /)
                    tmp = csv.reader(pressata_csv_file,delimiter=';') # read csv as csv (each row is an array)
                    t_line_count=0 # initialize secondary row counter
                    header=True
                    for p_row in tmp: # iterate over rows in pressata csv
                        if t_line_count==0 or t_line_count==1 and header:
                            try: 
                                tempcode,IdComp,Stazione,Timestamp=name_parser(row["CSVname"]) # get informations form file name
                                Timestamp=parse_date(p_row[1],row["CSVname"])
                                ComboID=IdComp+Taglia
                                if ComboID not in comboIDs:
                                    cursor.execute("INSERT INTO Combos (ComboID,Taglia,IdComp,TargetMA,TargetMF,StdMA,StdMF,StdCurve) VALUES ('" + ComboID + "','" + Taglia + "','" + IdComp + "',0,0,0,0,0);")    
                                    #cnxn.commit()
                                    comboIDs.append(ComboID)
                                cursor.execute("INSERT INTO Pressate (Timestamp,RiduttoreID,ComboID,Stazione,MaxForza,MaxAltezza) VALUES (" + str(Timestamp) + "," + RiduttoreID + ",'" + ComboID + "','" + Stazione + "',0,0);")
                                #cnxn.commit()
                                header=False
                            except:
                                logging.debug("Wrong first row"+str(t_line_count))
                        elif t_line_count>2: # skip first 3 rows
                            try:
                                Forza   = p_row[3].replace(',','.')
                                Altezza = p_row[2].replace(',','.')
                                #try:
                                cursor.execute("INSERT INTO PressateData (Timestamp,Forza,Altezza) VALUES (" + str(Timestamp) + "," + Forza + "," + Altezza + ");")
                                #cnxn.commit()
                                #except:
                                #    logging.debug("Error in query "+row["CSVpath"]+" line "+str(t_line_count))   
                            except:
                                logging.warning("Malformed row in " +row["CSVpath"]+" line "+str(t_line_count))
                        t_line_count+=1
        line_count+=1   
        cnxn.commit()
#close cursors and connection
cursor.close() 
cnxn.close() 
logging.warning("Process completed in: %s seconds" % (time.time() - start_time))
