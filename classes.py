# TODO: add type check to data https://stackoverflow.com/questions/9305751/how-to-force-ensure-class-attributes-are-a-specific-type

class Pressata:
    def __init__ (self, id, stazione, timestamp): # creator
        # fields
        self.id          = id
        self.stazione    = stazione
        self.timestamp   = timestamp
        self.warning     = False
        self.ripressato  = False
        self.max_forza   = 0
        self.max_altezza = 0
        self.altezza     = []
        self.forza       = []
    
    def add_value(self, height, force):
        self.altezza.append(float(height)) 
        self.forza.append(float(force))
    
    def trigger_warn(self):
        self.warning=True # throw warning

    def set_max_values(self):
        self.max_altezza = max(self.altezza)
        self.max_forza   = max(self.forza)

    # def _print(self):
    #     print("\tID: {}\n\tStazione: {}\n\tTimestamp: {}\n\tWarning: {}\n\tSerie: {}".format(self.id,self.stazione,self.timestamp,self.warning,self.serie))

    def to_json(self):
        pressata={
            'id'          : self.id,
            'stazione'    : self.stazione,
            'timestamp'   : self.timestamp,
            'max_altezza' : self.max_altezza,
            'max_forza'   : self.max_forza,
            'warning'     : self.warning,
            'ripressato'  : self.ripressato,
            'altezza'     : self.altezza,
            'forza'       : self.forza
        }
        return pressata

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
        self.steps.append(step) # add pressata to steps serie

    def trigger_warn(self):
        self.warnings=True

    # def _print(self):
    #     print("ID: {}\nMaster: {}\nTaglia: {}\nStadi: {}\nRapporto: {}\nCD: {}\nWarnings: {}\nPressate:".format(str(self.ID),str(self.master),self.taglia,str(self.stadi),str(self.rapporto),str(self.cd),str(self.warnings)))
    #     for pressata in self.steps:
    #         pressata._print()
    #         print("----")
    #     print() 

    def show_warn(self):
        if self.warnings==False:
            print("Non ci sono segnalazioni per il riduttore: ",self.id)
        else:
            # iterate over steps and check for true warning flag, if found print step ID
            pass
    
    def to_json(self):
        steps=[]
        for item in self.steps:
            steps.append(item.to_json())
        riduttore = {
            'ID'       : self.ID,
            'master'   : self.master,
            'taglia'   : self.taglia,
            'stadi'    : self.rapporto,
            'cd'       : self.cd,
            'warnings' : self.warnings,
            'steps'    : steps
        }
        return riduttore
        

class Series:
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.altezza = []
        self.forza = []  

    


