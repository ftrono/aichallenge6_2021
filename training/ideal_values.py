import set_targets
from utils import write_warning
from database_functions.db_connect import db_connect, db_disconnect
from utils import interpolate_curve
from stats import batch_standardize

conn, cursor = db_connect()

def align_tables(l1, l2):
    """
    This function will basically add the elements of Forza and Altezza from table
    PRESSATE_DATA to the element of PRESSATE where the timestamp is the same  
    """
    new_list = []
    timestamps=[]
    for e in l2:
        timestamps.append(e[0])
    for e in l1:
        index = timestamps.index(e[0])
        forza = l2[index][1]
        altezza = l2[index][2]
        new_list.append([e, forza, altezza])
    return new_list


cursor.execute("SELECT Timestamp, ComboID, MaxForza, MaxAltezza FROM Pressate")
press = cursor.fetchall()

cursor.execute("SELECT DISTINCT Timestamp FROM Warnings")
warn = cursor.fetchall()

cursor.execute("SELECT Timestamp, Forza, Altezza FROM PressateData")
pressate_data = cursor.fetchall()

pressate = align_tables(press, pressate_data)

"""
This dictionary will have as keys the combo_ID and as element a list of list where the 
inner list will be made of the timestamp, max_forza and max_altezza and the list of forza
and altezza for each pressata that does not have the same timestamp as the one in the
WARNINGS table
"""
combos = dict()

#This list will collect all of the timestamps that have not a warning
#IT MAY BE USELESS!!!!!!!
correct_timestamp = []
for pressata in pressate: #iterate over all of the pressate from the table PRESSATE
    """
    Here pressata[0] is the Timestamp, pressata[1] is the ComboID, 
    pressata[2] is the Max_forza, pressata[3] the Max_altezza,
    pressata[4] and pressata[5] are the original curves of forza and altezza
    """

    if not(pressata[0] in warn): #check if the timestamp is not on the WARNING table
        correct_timestamp.append(pressata[0])
        #now add this pressata to the combos dictionary
        if pressata[1] in combos: #if there's already been a pressata with a particular
            #combo_ID then append this new one to its list
            combos[pressata[1]].append([pressata[0], pressata[2], pressata[3]])
        else: #if not create a new key for the dictionary where this pressata can be placed
            combos[pressata[1]] = [[pressata[0], pressata[2], pressata[3], pressata[4], pressata[5]]]
            """
            where we add already a list of list, so that each new quintuplet that will come
            won't be mixed with the previous ones
            """ 

cursor.execute("SELECT ComboID, Altezza FROM CombosData")
combo_altezza = cursor.fetchall()
list_combo = []
list_altezze = []
for e in combo_altezza:
    list_combo.append(e[0])
    list_altezze.append(e[1])
"""
I've done this for loop so that I'm certain that they'll keep the same index number
Maybe i'm stupid so if one of you guys is certain that doing two queries will keep the 
index for both then you can change it
"""

#Here loop over keys of the dictionary that are the combos id 
for key in combos:
    i = list_combo.index(key) #find the index to get the stamp for the interpolate
    list_pressate = combos[key] #get the list with all the pressate for a combo
    normalized_curves = []
    for pressata in list_pressate: #loop through all the pressate to interpolate
        normalized_curves.append(interpolate_curve(list_altezze[i], pressata[4], pressata[3]))
        #since interpolate_curve takes as input first the altezza and then the force they are inverted
    forza_combo, std_curve = batch_standardize(normalized_curves) 


    cursor.execute("UPDATE Combos SET StdCurve = ? WHERE ComboID = ?", std_curve, key)
    cursor.commit()
    cursor.execute("UPDATE CombosData SET Forza = ? WHERE ComboID = ?", forza_combo, key)
    cursor.commit()

db_disconnect(conn, cursor)