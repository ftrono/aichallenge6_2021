import csv, time, logging, datetime, os
from systemd import journal
from db_connect import db_connect, db_disconnect

#Herper functions:
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

#INSERT DATA:
def insert_data():
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s')
    logging.debug("START")

    # open connection
    cnxn, cursor = db_connect()
    logging.debug("Connected to DB")

    start_time = time.time()


    #1) POPULATE WARNING_DESC TABLE::
    desc =  ["'Max_altezza out of bounds'",
            "'Delta_timestamp out of bounds'",
            "'Max_forza out of bounds'",
            "'Force curve out of bounds'"]

    for d in range(len(desc)):
        query = "INSERT INTO WarningDesc ( Description) VALUES ("+desc[d]+")"
        cursor.execute(query)
        cursor.commit()

    with open(os.getcwd()+"/database_functions/Summary.csv", mode='r') as summary:
        # read csv as dictionary
        summary_reader = csv.DictReader(summary,delimiter=',') 
        line_count = 0 # initialize line counter
        rows = list(summary_reader)
        totalrows = len(rows)

    #2) DATASET IMPORT:
    status=open(os.getcwd()+'/status.log', "r+")
    comboIDs=[]
    with open(os.getcwd()+"/database_functions/Summary.csv", mode='r') as summary:
        # read csv as dictionary
        summary_reader = csv.DictReader(summary,delimiter=',') 
        line_count = 0 # initialize line counter
        # iterate over rows in summary
        prev_key=""
        for row in summary_reader:
            if line_count<0:
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
                                        comboIDs.append(ComboID)
                                    cursor.execute("INSERT INTO Pressate (Timestamp,RiduttoreID,ComboID,Stazione,MaxForza,MaxAltezza) VALUES (" + str(Timestamp) + "," + RiduttoreID + ",'" + ComboID + "','" + Stazione + "',0,0);")
                                    header=False
                                except:
                                    logging.debug("Wrong first row"+str(t_line_count))
                            elif t_line_count>2: # skip first 3 rows
                                try:
                                    Forza   = p_row[3].replace(',','.')
                                    Altezza = p_row[2].replace(',','.')
                                    try:
                                        cursor.execute("INSERT INTO PressateData (Timestamp,Forza,Altezza) VALUES (" + str(Timestamp) + "," + Forza + "," + Altezza + ");")
                                    except:
                                        logging.warning("Unable to insert "+row["CSVpath"]+" line "+str(t_line_count))   
                                except:
                                    logging.warning("Malformed row in " +row["CSVpath"]+" line "+str(t_line_count))
                            t_line_count+=1
            cnxn.commit()
            line_count+=1
            journal.write("[Import CSV] Inserted %s\%s pressate"%(str(line_count),str(totalrows)))
            
    #close cursor and connection
    db_disconnect(cnxn, cursor)
    logging.warning("Process completed in: %s seconds" % (time.time() - start_time))
    return 0

#MAIN:
if __name__ == '__main__':
    insert_data()
