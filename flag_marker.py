from access_db import query_bycombo
import numpy as np
import statistics

#FLAG MARKER (ALTEZZA & DELTA TIMESTAMP)
#NOTE:this function is in BETA, currently based on combos (useless).
#It will be adapted to the structure and flags of the new DB.


#HELPER FUNCTIONS:
#1) Mark warning according to max_altezza (primo giro):
def mark_altezza(combo, sigmah=1):
    #set targets for combo:
    mh_list = [s.max_altezza for s in combo.series]
    #print(max(mh_list))
    combo.max_altezza = max(mh_list)
    combo.mh_threshold = statistics.stdev(mh_list)*sigmah

    #analyze each series:
    for series in combo.series:
        #check max_altezza: set warning if max_altezza out of bounds:
        if (series.max_altezza < (combo.max_altezza - combo.mh_threshold)) or (series.max_altezza > (combo.max_altezza + combo.mh_threshold)):
            #mark current pressata:
            series.warning = True
            #ALSO WRITE TO DB (WIP).

    return combo


#2) Get global target for delta timestamp (secondo giro):
def get_global_dt(combo):
    #vars:
    rid_list = [s.riduttore for s in combo.series]
    dt_list = []
    riduttori = {}
    
    #2A) extract series for every riduttore in the combo:
    for rid in rid_list:
        #get list of series belonging to a riduttore:
        ripr = combo.get_fromriduttore(rid)
        #if more than 2 ripressate:
        if len(ripr) > 2:
            for i in range(len(ripr)):
                #from second pressata:
                if (i != 0):
                    #get delta timestamp (in seconds):
                    dt = np.diff([ripr[i-1].timestamp, ripr[i].timestamp])
                    #store only if higher than 2 seconds (avoid duplicate files):
                    if dt > 2:
                        dt_list.append(dt[0])
                    
        #store mean within each riduttore:
        mean_dt = statistics.mean(dt_list)
        riduttori[rid] = mean_dt #(mean_dt, dt_list)
        #reset:
        dt_list = []

    #2B) get global target for riduttori's means:
    avgs = {}
    #frequency count:
    for mn in riduttori.values():
        if mn not in avgs.keys():
            avgs[mn] = 1
        else:
            avgs[mn] = avgs[mn]+1
    
    #get 1st frequency per count (nbest):
    global_dt = sorted(avgs.items(), key=lambda item: item[1], reverse=True)[0][0]
    print(global_dt)

    return global_dt


#DATABASE ANALYSIS:
def flag_marker(taglia, idcomp, sigmah=1, sigmadt=0.3):
    #query:
    combo = query_bycombo(taglia, idcomp)

    #1) MARK WARNINGS FOR MAX_ALTEZZA:
    combo = mark_altezza(combo, sigmah=1)

    #2) DELTA TIMESTAMPS:
    global_dt = get_global_dt(combo)
    acc_var = round(global_dt*sigmadt,0)
    print(global_dt, acc_var)

    #3) Mark all pressate (terzo giro):
    rid_list = [s.riduttore for s in combo.series]
    riduttori = {}

    for rid in rid_list:
        ripr = combo.get_fromriduttore(rid)
        if len(ripr) > 2:
            for i in range(len(ripr)):
                if (i != 0):
                    #get delta timestamp:
                    dt = np.diff([ripr[i-1].timestamp, ripr[i].timestamp])
                    #if dt out of bounds:
                    if (dt < (global_dt-acc_var)) or (dt > (global_dt+acc_var)):
                        #mark previous pressata:
                        ripr[i-1].warning = True
                        #MARK RIDUTTORE HERE TOO (need DB update).
    
    return combo


#MAIN:
#"MP080", "a0206"
#"LC120", "a0210"
cb = flag_marker("MP080", "a0215")
rid_list = [s.riduttore for s in cb.series]
dl = []
dz = {}

for rid in rid_list:
    ripr = cb.get_fromriduttore(rid)
    if len(ripr) > 2:
        for i in range(len(ripr)):
            dl.append(ripr[i].warning)
    dz[rid] = dl
    dl = []

print(dz)

