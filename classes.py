# TODO: add type check to data https://stackoverflow.com/questions/9305751/how-to-force-ensure-class-attributes-are-a-specific-type

class Pressata:
    def __init__ (self, id, componente):
        self.ID         = id
        self.componente = componente
        self.serie      = []
    
    def add_value(self, val):
        self.serie.append(val)

class Riduttore:
    def __init__(self, id, master, taglia, stadi, rapporto, cd):
        self.ID       = id
        self.master   = master
        self.taglia   = taglia
        self.stadi    = stadi
        self.rapporto = rapporto
        self.cd       = cd
        self.steps    = []
        self.warnings = False
    
    def add_step(self, step):
        self.steps.append(step)

    def trigger_warn(self):
        self.warnings=True

    def show_warn(self):
        if self.warnings==False:
            print("Non ci sono segnalazioni per il riduttore: ",self.id)
        else:
            # iterate over steps and check for true warning flag, if found print step ID
            pass


