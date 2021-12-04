import csv, time, datetime, os, logging
from datetime import timezone
#import telegram_send


#Helper functions:
def name_parser(name): # take as input the file name
    # get information from file name
    id=name[14:19]
    stazione=name[21:23]
    return id,stazione

def parse_date(cell):
    anno=int("20"+cell[6:8])
    mese=int(cell[3:5])
    giorno=int(cell[0:2])
    ora=int(cell[9:11])
    minuto=int(cell[12:14])
    secondo=int(cell[15:17])
    dt=datetime.datetime(anno,mese,giorno,ora,minuto,secondo) # convert string to date obj
    timestamp=dt.replace(tzinfo=timezone.utc).timestamp() # convert date object to timestamp
    return timestamp

def generate_ComboID(idComp,taglia,stazione,master,rapporto,stadi):
    p009_rap=[30,40,70,100]
    if idComp=='p0009' and stazione=='a1' and int(master)==2 and (int(rapporto) in p009_rap):
        return idComp+taglia+'i10'
    if idComp=='p0045' and stazione=='a1' and int(master)==2 and int(rapporto)==100:
        return idComp+taglia+'i10'
    if stazione=='a5':
        return idComp+taglia+'s0'+str(stadi)
    return idComp+taglia+'000'




#INSERT DATA:
def insert_data(dbt,limit=1000000):
    cursor = dbt['cursor']
    cnxn = dbt['cnxn']
    n_rid=0
    n_pres=0
    n_combo=0
    n_pres_data=0
    e_rid=0
    e_pres=0
    e_combo=0
    e_pres_data=0
    status_log=logging.getLogger('status')
    general_log=logging.getLogger('general')
    
    general_log.info("STARTED DATA INSERT")

    start_time = time.time()

    #1) POPULATE WARNING_DESC TABLE::
    desc =  ["'Pressata: max_altezza out of bounds'",
            "'Pressata: anomalous height curve'",
            "'Pressata: max_forza out of bounds'",
            "'Pressata: force curve out of bounds'",
            "'Riduttore: incorrect number of pressate'"]

    for d in range(len(desc)):
        query = "INSERT INTO WarningDesc (Description) VALUES ("+desc[d]+")"
        cursor.execute(query)
        cursor.commit()
    general_log.info("WarningDesc populated")

    with open(os.getcwd()+"/database_functions/Summary.csv", mode='r') as summary:
        # read csv as dictionary
        summary_reader = csv.DictReader(summary,delimiter=',') 
        line_count = 0 # initialize line counter
        rows = list(summary_reader)
        totalrows = len(rows)

    #2) DATASET IMPORT:
    comboIDs=[]
    with open(os.getcwd()+"/database_functions/Summary.csv", mode='r') as summary:
        general_log.debug(summary)
        # read csv as dictionary
        summary_reader = csv.DictReader(summary,delimiter=',') 
        line_count = 0 # initialize line counter
        # iterate over rows in summary
        prev_key=""
        for row in summary_reader:
            if line_count<limit:
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
                            general_log.debug("Inserted Riduttore "+RiduttoreID)
                        except:
                            general_log.error("Unable to insert riduttore " + RiduttoreID + " duplicate key")
                            e_rid+=1

                    with open(os.getcwd()+"/database_functions/"+row["CSVpath"].replace('\\','/')) as pressata_csv_file: # open pressata csv (need to replace \ with normal /)
                        pressata = csv.reader(pressata_csv_file,delimiter=';') # read csv as csv (each row is an array)
                        t_line_count=0 # initialize secondary row counter
                        header=True
                        dataList=[]
                        duplicate=False
                        for p_row in pressata: # iterate over rows in pressata csv
                            if (t_line_count==0 or t_line_count==1) and header:
                                try:
                                    if p_row[1]!='Date':
                                        Timestamp=parse_date(p_row[1])
                                        try:
                                            IdComp,Stazione=name_parser(row["CSVname"]) # get informations form file name
                                            ComboID=generate_ComboID(IdComp,Taglia,Stazione,Master,Rapporto,Stadi)
                                            if ComboID not in comboIDs:
                                                try:
                                                    n_combo+=1
                                                    cursor.execute("INSERT INTO Combos (ComboID,Taglia,IdComp,TargetMA,TargetMF,StdMA,StdMF,StdCurveAvg) VALUES ('" + ComboID + "','" + Taglia + "','" + IdComp + "',0,0,0,0,0);")    
                                                    comboIDs.append(ComboID)
                                                    general_log.debug("Inserted Combo "+ComboID)
                                                except:
                                                    general_log.error("Unable to insert Combo "+ComboID)
                                                    e_combo+=1
                                            try: 
                                                header=False
                                                n_pres+=1      
                                                cursor.execute("INSERT INTO Pressate (Timestamp,RiduttoreID,ComboID,Stazione,MaxForza,MaxAltezza) VALUES (" + str(Timestamp) + "," + RiduttoreID + ",'" + ComboID + "','" + Stazione + "',0,0);")
                                                general_log.debug("Inserted pressata " + str(row["CSVname"]))
                                            except:
                                                e_pres+=1
                                                general_log.error("Unable to add pressata " + str(row["CSVname"]) + " duplicate timestamp")
                                                duplicate=True
                                        except:
                                            general_log.error("Unknown error at "+str(row["CSVname"]))
                                except:
                                    general_log.warning(str(row["CSVname"])+" Wrong (header) date cell "+str(Timestamp)+" at line "+str(t_line_count))
                                #general_log.debug("Timestamp: {}, {}".format(Timestamp, row["CSVpath"]))
                            elif t_line_count>2 and not duplicate: # skip first 3 rows
                                if header:
                                    general_log.warning("Pressata %s not inserted but data are available"%(row["CSVname"])) 
                                else: 
                                    try:
                                        n_pres_data+=1
                                        Forza   = p_row[3].replace(',','.')
                                        Altezza = p_row[2].replace(',','.')
                                        try: 
                                            dataList.append("(" + str(Timestamp) + "," + str(Forza) + "," + str(Altezza) + ")")
                                        except:
                                            e_pres_data+=1
                                            general_log.warning(str(row["CSVname"])+"Unable to append values at line "+str(t_line_count)) 
                                    except:
                                        e_pres_data+=1
                                        general_log.warning(str(row["CSVname"]) + " Malformed row " + str(t_line_count))
                            t_line_count+=1
                        if not header and not duplicate:
                            try:
                                cursor.execute("INSERT INTO PressateData (Timestamp,Forza,Altezza) VALUES "+','.join(dataList))
                                general_log.debug("Inserted data for pressata " + str(row["CSVname"]))
                            except:
                                general_log.error("Unable to insert data from pressata:"+str(row["CSVname"]))
            cnxn.commit()
            line_count+=1
            #whenever you want to write
            #fp.seek(0)
            status_log.info("[Import CSV] Inserted %s\%s pressate"%(str(line_count),str(totalrows)))
            #fp.write("[Import CSV] Inserted %s\%s pressate\n"%(str(line_count),str(totalrows)))
            #fp.flush()
            #journal.write("[Import CSV] Inserted %s\%s pressate"%(str(line_count),str(totalrows)))
    general_log.info("INSERT COMPLETED IN: %s seconds" % (time.time() - start_time))
    #when you're done
    report = open(os.getcwd()+"/logs/insert_report.txt", 'w')
    report.write("IMPORT CSV REPORT\n\nProcess started at: %s\nProcess completed at: %s\nElapsed time: %s seconds\nInserted riduttori: %s/%s\nInserted combos: %s/%s\nInserted pressate: %s/%s\nInserted data from pressate: %s/%s"%(str(time.ctime(int(start_time))),str(time.ctime(int(time.time()))),str(time.time()-start_time),str(n_rid-e_rid),str(n_rid),str(n_combo-e_combo),str(n_combo),str(n_pres-e_pres),str(n_pres),str(n_pres_data-e_pres_data),str(n_pres_data)))
    #telegram_send.send(messages=["Import completed! in %s seconds"%(time.time() - start_time)])
    return 0

#MAIN:
if __name__ == '__main__':
    insert_data()
