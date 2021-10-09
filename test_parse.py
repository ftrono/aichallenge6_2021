import datetime

def name_parser(name):
    tempcode=name[0:14]
    id=name[14:19]
    stazione=name[21:23]
    date_time=datetime.datetime(int(name[24:28]), int(name[29:31]), int(name[32:34]),int(name[35:37]),int(name[38:40]),int(name[41:43]))
    timestamp=datetime.datetime.timestamp(date_time)
    return tempcode,id,stazione,timestamp


name_parser('20200313112012a0206__a1_2020_03_13_14_27_32.csv')

print(name_parser('20200313112012a0206__a1_2020_03_13_14_27_32.csv'))

#20200313112012a0206__a1_2020_03_13_14_27_32.csv