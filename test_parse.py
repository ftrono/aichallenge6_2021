import datetime
from classes import Riduttore, Pressata
import csv
import datetime

def name_parser(name):
    tempcode=name[0:14]
    id=name[14:19]
    stazione=name[21:23]
    date_time=datetime.datetime(int(name[24:28]), int(name[29:31]), int(name[32:34]),int(name[35:37]),int(name[38:40]),int(name[41:43]))
    timestamp=datetime.datetime.timestamp(date_time)
    return tempcode,id,stazione,timestamp
    
produzione=dict()
with open('./Summary.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file,delimiter=';') # read csv as dictionary
    line_count = 0
    for row in csv_reader: # iterate over rows in summary
        if line_count > 0 and line_count<2:
            if not (row["Tempcode"] in produzione): # check if riduttore has already been saved
                produzione[row["Tempcode"]]=Riduttore(row["Tempcode"],row["Master"],row["Taglia"],row["Stadi"],row["Rapporto"],row["CD"]) # generate new istance of riduttore
            with open(row["CSVpath"]) as pressata_csv_file:
                tmp = csv.DictReader(pressata_csv_file,delimiter=';')
                t_line_count=0
                for t_row in tmp:
                    if t_line_count==0:
                        pressata=Pressata(t_row[0],"bho") # TO aggiungere componente quando sarà disponibile
                    else:
                        pressata.add_value(t_row[5])
                produzione[row["Tempcode"]].add_step(pressata) 
        

#20200313112012a0206__a1_2020_03_13_14_27_32.csv