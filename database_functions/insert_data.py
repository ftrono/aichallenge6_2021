import csv, time, datetime, os

#Herper functions:
def name_parser(name): # take as input the file name
    # get information from file name
    id=name[14:19]
    stazione=name[21:23]
    date_time=datetime.datetime(int(name[24:28]), int(name[29:31]), int(name[32:34]),int(name[35:37]),int(name[38:40]),int(name[41:43])) # convert string to date obj
    timestamp=datetime.datetime.timestamp(date_time) # convert date object to timestamp
    return id,stazione,timestamp

def parse_date(cell):
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
def insert_data(cnxn,cursor,logging):
    n_rid=0
    n_pres=0
    n_combo=0
    n_pres_data=0
    e_rid=0
    e_pres=0
    e_combo=0
    e_pres_data=0
    fp = open('status.txt', 'w')
    
    logging.info("STARTED DATA INSERT")

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
    logging.info("WarningDesc populated")

    with open(os.getcwd()+"/database_functions/Summary.csv", mode='r') as summary:
        # read csv as dictionary
        summary_reader = csv.DictReader(summary,delimiter=',') 
        line_count = 0 # initialize line counter
        rows = list(summary_reader)
        totalrows = len(rows)

    #2) DATASET IMPORT:
    comboIDs=[]
    with open(os.getcwd()+"/database_functions/Summary.csv", mode='r') as summary:
        logging.debug("Opened summary.csv")
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
                        
                        # Query insert riduttore
                        try:
                            n_rid+=1
                            query="INSERT INTO Riduttori (RiduttoreID,Master,Taglia,Cd,Stadi,Rapporto) VALUES (" + RiduttoreID + "," + Master + ",'" + Taglia + "'," + Cd + "," + Stadi + "," + Rapporto + ")"
                            cursor.execute(query)
                            logging.debug("Inserted Riduttore "+RiduttoreID)
                        except:
                            logging.error("Unable to insert riduttore " + RiduttoreID + " duplicate key")
                            e_rid+=1

                    with open(os.getcwd()+"/database_functions/"+row["CSVpath"].replace('\\','/')) as pressata_csv_file: # open pressata csv (need to replace \ with normal /)
                        pressata = csv.reader(pressata_csv_file,delimiter=';') # read csv as csv (each row is an array)
                        t_line_count=0 # initialize secondary row counter
                        header=True
                        dataList=[]
                        for p_row in pressata: # iterate over rows in pressata csv
                            if (t_line_count==0 or t_line_count==1) and header:
                                try:
                                    if p_row[1]!='Date':
                                        Timestamp=parse_date(p_row[1])
                                        try:
                                            IdComp,Stazione,Timestamp=name_parser(row["CSVname"]) # get informations form file name
                                            
                                            ComboID=IdComp+Taglia
                                            if ComboID not in comboIDs:
                                                try:
                                                    n_combo+=1
                                                    cursor.execute("INSERT INTO Combos (ComboID,Taglia,IdComp,TargetMA,TargetMF,StdMA,StdMF,StdCurve) VALUES ('" + ComboID + "','" + Taglia + "','" + IdComp + "',0,0,0,0,0);")    
                                                    comboIDs.append(ComboID)
                                                    logging.debug("Inserted Combo "+ComboID)
                                                except:
                                                    logging.error("Unable to insert Combo "+ComboID)
                                                    e_combo+=1
                                            try: 
                                                header=False
                                                n_pres+=1      
                                                cursor.execute("INSERT INTO Pressate (Timestamp,RiduttoreID,ComboID,Stazione,MaxForza,MaxAltezza) VALUES (" + str(Timestamp) + "," + RiduttoreID + ",'" + ComboID + "','" + Stazione + "',0,0);")
                                                logging.debug("Inserted pressata " + str(row["CSVname"]))
                                            except:
                                                e_pres+=1
                                                logging.error("Unable to add pressata " + str(row["CSVname"]) + " duplicate timestamp")
                                        except:
                                            logging.error("Unknown error at "+str(row["CSVname"]))
                                except:
                                    logging.warning(str(row["CSVname"])+" Wrong (header) date cell "+str(Timestamp)+" at line "+str(t_line_count))
                                #logging.debug("Timestamp: {}, {}".format(Timestamp, row["CSVpath"]))
                            elif t_line_count>2: # skip first 3 rows
                                if header:
                                    logging.warning("Pressata %s not inserted but data are available"%(row["CSVname"])) 
                                else: 
                                    try:
                                        n_pres_data+=1
                                        Forza   = p_row[3].replace(',','.')
                                        Altezza = p_row[2].replace(',','.')
                                        try: 
                                            dataList.append("(" + str(Timestamp) + "," + str(Forza) + "," + str(Altezza) + ")")
                                        except:
                                            e_pres_data+=1
                                            logging.warning(str(row["CSVname"])+"Unable to append values at line "+str(t_line_count)) 
                                    except:
                                        e_pres_data+=1
                                        logging.warning(str(row["CSVname"]) + "Malformed line " + str(t_line_count))
                            t_line_count+=1
                        if not header:
                            try:
                                cursor.execute("INSERT INTO PressateData (Timestamp,Forza,Altezza) VALUES "+','.join(dataList))
                                logging.debug("Inserted data for pressata " + str(row["CSVname"]))
                            except:
                                logging.error("Unable to insert data from pressata:"+str(row["CSVname"]))
            cnxn.commit()
            line_count+=1
            #whenever you want to write
            fp.seek(0)
            fp.write("[Import CSV] Inserted %s\%s pressate"%(str(line_count),str(totalrows)))
            fp.flush()
            #journal.write("[Import CSV] Inserted %s\%s pressate"%(str(line_count),str(totalrows)))
    logging.info("INSERT COMPLETED IN: %s seconds" % (time.time() - start_time))
    #when you're done
    fp.close()
    report = open(os.getcwd()+"/logs/insert_report.txt", 'w')
    report.write("IMPORT CSV REPORT\n\nProcess started at: %s\nProcess completed at: %s\nElapsed time: %s seconds\nInserted riduttori: %s/%s\nInserted combos: %s/%s\nInserted pressate: %s/%s\nInserted data from pressate: %s/%s"%(str(time.ctime(int(start_time))),str(time.ctime(int(time.time()))),str(time.time()-start_time),str(n_rid-e_rid),str(n_rid),str(n_combo-e_combo),str(n_combo),str(n_pres-e_pres),str(n_pres),str(n_pres_data-e_pres_data),str(n_pres_data)))
    return 0

#MAIN:
if __name__ == '__main__':
    insert_data()
