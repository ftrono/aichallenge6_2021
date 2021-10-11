# TODO: add type check to data https://stackoverflow.com/questions/9305751/how-to-force-ensure-class-attributes-are-a-specific-type

class Pressata:
    def __init__ (self, id, stazione, timestamp): # creator
        # fields
        self.id        = id
        self.stazione  = stazione
        self.timestamp = timestamp
        self.serie     = []
        self.warning   = False
    
    def add_value(self, val):
        self.serie.append(val) # append value to serie
    
    def trigger_warn(self):
        self.warning=True # throw warning

    def print(self):
        print("\tID: {}\n\tStazione: {}\n\tTimestamp: {}\n\tWarning: {}\n\tSerie: {}".format(self.id,self.stazione,self.timestamp,self.warning,self.serie))


    


class Riduttore:
    def __init__(self, id, master, taglia, stadi, rapporto, cd):
        # fields
        self.ID       = id
        self.master   = master
        self.taglia   = taglia
        self.stadi    = stadi
        self.rapporto = rapporto
        self.cd       = cd
        self.steps    = []
        self.warnings = False
    
    def add_step(self, step):
        self.steps.append(step) # add pressata to seteps serie

    def trigger_warn(self):
        self.warnings=True

    def print(self):
        print("ID: {}\nMaster: {}\nTaglia: {}\nStadi: {}\nRapporto: {}\nCD: {}\nWarnings: {}\nPressate:".format(str(self.ID),str(self.master),self.taglia,str(self.stadi),str(self.rapporto),str(self.cd),str(self.warnings)))
        for pressata in self.steps:
            pressata.print()
            print("---")
        print() 

    def show_warn(self):
        if self.warnings==False:
            print("Non ci sono segnalazioni per il riduttore: ",self.id)
        else:
            # iterate over steps and check for true warning flag, if found print step ID
            pass

    


