from classes import Riduttore, Pressata
import csv

produzione=dict()
with open('Summary.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count > 0:
            if not (row["Tempcode"] in produzione):
                produzione[row["Tempcode"]]=Riduttore(row["Tempcode"],row["Master"],row["Taglia"],row["Stadi"],row["Rapporto"],row["CD"])
            with open(row["CSVpath"]) as tmp:
                t_line_count=0
                for t_row in tmp:
                    if t_line_count==0:
                        pressata=Pressata(t_row[0],"bho") # TO aggiungere componente quando sarà disponibile
                    elif t_line_count>1:
                        pressata.add_value(t_row[5])
                produzione[row["Tempcode"]].add_step(pressata)        
        
