import datetime 

cell = "16.03.20 09:49:02"

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

print(parse_date(cell))
