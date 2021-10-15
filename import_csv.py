import csv
import time
from utils import name_parser, mongo_connect, mongo_disconnect
from classes import Riduttore, Pressata

start_time = time.time()
produzione=dict()
with open('./Summary.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file,delimiter=',') # read csv as dictionary
    line_count = 0 # initialize line counter
    f = open("log.txt", "w") # open log file to store exceptions
    for row in csv_reader: # iterate over rows in summary
        if line_count > 0: # skip first row (colum names)
            if not (row["Tempcode"] in produzione): # check if riduttore has already been saved
                produzione[row["Tempcode"]]=Riduttore(row["Tempcode"],row["Master"],row["Taglia"],row["Stadi"],row["Rapporto"],row["CD"]) # generate new istance of riduttore
            with open(row["CSVpath"].replace('\\','/')) as pressata_csv_file: # open pressata csv (need to replace \ with normal /)
                tmp = csv.reader(pressata_csv_file,delimiter=';') # read csv as csv (each row is an array)
                t_line_count=0 # initialize secondary row counter
                for t_row in tmp: # iterate over rows in pressata csv
                    if t_line_count==0: 
                        tempcode,id,stazione,timestamp=name_parser(row["CSVname"]) # get informations form file name
                        pressata=Pressata(id,stazione,timestamp) # generate instance of pressata
                    elif t_line_count>1: # skip first 2 rows
                        try: 
                            pressata.add_value(t_row[2].replace(',','.'),t_row[3].replace(',','.')) # add value to serie in pressata
                        except: # handle exception due to malformed rows
                            print(str(row["CSVpath"])+" Unable to add value at line "+str(t_line_count+1) + " " + str(t_row))
                            f.write(str(row["CSVpath"])+" Unable to add value at line "+str(t_line_count+1)+" " + str(t_row)+"\n")
                    t_line_count+=1
                produzione[row["Tempcode"]].add_step(pressata) # add pressata to instance of riduttore
        line_count+=1   
    f.close() 
    print("Import process completed")

    db,client=mongo_connect()
    for document in produzione.values():
        result=db.test2.insert_one(document.to_json())
        print('Inserted document {}'.format(result.inserted_id))
    mongo_disconnect(client)
print("--- %s seconds ---" % (time.time() - start_time)) # print execution time 



# for key in produzione.keys():
#     produzione[key].print()
        
#mongodb://localhost:27017/


