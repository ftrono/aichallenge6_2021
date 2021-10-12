# TODO: add type check to data https://stackoverflow.com/questions/9305751/how-to-force-ensure-class-attributes-are-a-specific-type

class Item:
    def __init__(self,height,force):
        self.height = height
        self.force  = force

    def to_json(self):
        item={
            'height': self.height,
            'force' : self.force
        }  
        return item   

class Pressata:
    def __init__ (self, id, stazione, timestamp): # creator
        # fields
        self.id         = id
        self.stazione   = stazione
        self.timestamp  = timestamp
        self.warning    = False
        self.ripressato = False
        self.serie      = []
    
    def add_value(self, val):
        self.serie.append(val) # append value to serie
    
    def trigger_warn(self):
        self.warning=True # throw warning

    def _print(self):
        print("\tID: {}\n\tStazione: {}\n\tTimestamp: {}\n\tWarning: {}\n\tSerie: {}".format(self.id,self.stazione,self.timestamp,self.warning,self.serie))

    def to_json(self):
        pressure=[]
        for item in self.serie:
            pressure.append(item.to_json())
        pressata={
            'id'         : self.id,
            'stazione'   : self.stazione,
            'timestamp'  : self.timestamp,
            'warning'    : self.warning,
            'ripressato' : self.ripressato,
            'serie'      : pressure
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
        self.steps.append(step) # add pressata to seteps serie

    def trigger_warn(self):
        self.warnings=True

    def _print(self):
        print("ID: {}\nMaster: {}\nTaglia: {}\nStadi: {}\nRapporto: {}\nCD: {}\nWarnings: {}\nPressate:".format(str(self.ID),str(self.master),self.taglia,str(self.stadi),str(self.rapporto),str(self.cd),str(self.warnings)))
        for pressata in self.steps:
            pressata._print()
            print("----")
        print() 

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
        
   

    


