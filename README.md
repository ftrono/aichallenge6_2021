# AI challenge - Team 6
# Premessa:
Gli script presenti in questa repository sono stati ideati per essere eseguiti su un sistema operativo **linux** e sono testati su Ubuntu 18.04 LTS  
### Prerequisiti:  
* Python 3.3 o superiore   
* mongod (https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/)  
* pymongo drivers (```pip3 install pymongo```)  
### Suggerimenti:  
* MongoDB Compass

---

# Indice:
1) Operazioni e comandi ricorrenti
2) Comandi e guida GitHub


---

# 1) OPERAZIONI RICORRENTI

## PUNTO 0) (SOLO PER WSL) AVVIARE FILE DESKTOP config.xlaunch (OGNI VOLTA):
Avviare il file ***config.xlaunch*** salvato sul desktop, lancerà l’X-Server con la configurazione giusta (vale solo per WSL su Windows 10, non per Ubuntu/Mac).


## PUNTO A) AVVIARE SERVER MONGODB (OGNI VOLTA):
Usate i comandi (se Init):
* ```sudo service mongod start``` per avviare il server MongoDB
* ```sudo service mongod status``` per verificare che sia effettivamente attivo

Se systemd, o per ulteriori comandi disponibili, vedere qui:
* https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/


## PUNTO B) AVVIARE APP GRAFICA COMPASS (OGNI VOLTA):
Usate il comando:
* ```mongodb-compass```

Connettere Compass a localhost inserendo:
* ***mongodb://localhost:27017/***


## PUNTO C) PER IMPORTARE IL DUMP DEL DB (SOLO IN CASO DI NUOVI DUMP):
* Decomprimere lo zip in una cartella (es. Home di Ubuntu)
* Da bash, cd nella cartella dove lo decomprimiamo e lanciare ```mongorestore dump/```
* Lanciare Compass (punto B in alto), apparirà il DB *novotic* e lì dentro la collection *test1*


---

**Altre info di configurazione sono disponibili in questa folder Drive: https://drive.google.com/drive/folders/1lOZpjl8pjfPhmlcCdAh9lYgR5AYi0LUy**

---


# 2) COMANDI E GUIDA GITHUB
# Getting started
Per prima cosa clonare la repository in locale con  
```git clone https://github.com/aichallenge6/main.git```  
Suggerisco di usare visual studio code dato che integra i comandi git...  
## Impostazione delle variabili git
Se non sono già state impostate nel pc usare i seguenti comandi per impostarle:  
```git config --global user.email "email associata a github"```  
```git config --global user.name "username github"```  
Suggerisco di usare GitHub CLI per salvare le credenziali nel pc senza dover fare l'accesso ogni volta (anche perchè da un po' github non consente più di fare l'accesso solo con username e password), di seguito la guida per farlo: https://docs.github.com/en/get-started/getting-started-with-git/caching-your-github-credentials-in-git
## Da terminale
I comandi principali  da eseguire dentro la cartella local della repository sono:  
```git pull```   
per scaricare la versione aggiornata della repo che c'è su github, fatelo sempre prima di iniziare a lavorare sennò rischiamo di avere un sacco di conflitti da risolvere ogni volta che si fa un push    

```git add nome_file``` o ```git add .```   
per aggiungere al prossimo commit o un singolo file o tutti i file che sono stati modificati  
  
```git commit -m "messaggio"```  
fa il commit con descrizione "messaggio", scriveteli decentemente per favore che così se facciamo casino sappiamo dove è il problema (reference: https://reflectoring.io/meaningful-commit-messages/) 


```git push```  
fa l'upload dell'ultimo commit sulla repo di github, fatelo ogni volta che finite di lavorare su qualcosa (ovviamente prima bisogna fare add e commit)  
  
### Comando che spero non servirà mai:  
```git checkout```  
da usare nel caso ci siano conflitti per salvare il lavoro locale e fare il pull da remoto, in questo modo o cambiamenti apportati rimangono salvati in locale e si possono recuperare (ovviamnte a quasto punto il pull prende la repo così come è su github e eventuali cambiamenti sono da rifare)

