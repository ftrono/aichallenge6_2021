# AI challenge - Team 6
# Premessa:
Gli script presenti in questa repository sono stati ideati per essere eseguiti su un sistema operativo **linux** e sono testati su Ubuntu 18.04 LTS  
### Prerequisiti:  
* Python 3.3 o superiore   
* Microsoft (MS) SQL Server (https://docs.microsoft.com/en-us/sql/linux/quickstart-install-connect-ubuntu?view=sql-server-ver15)  
* *pyodbc* drivers (```pip3 install pyodbc``` o ```pip install pyodbc```)  
### Suggerimenti:  
* Installare MS SQL Server direttamente su Ubuntu o in WSL (guida step by step -> https://docs.google.com/document/d/1Hg8LUDYuBbO3p3FYNTM139w2DzV25sPZxpKnWhFTuPc/edit )

---

# Indice:
* Operazioni e comandi ricorrenti
* Comandi e guida GitHub


---

# 1) OPERAZIONI RICORRENTI

## 1. (DA BASH) AVVIARE SERVIZIO MSSQL SERVER (OGNI VOLTA):
**A) Da Ubuntu:**
* START: ```sudo service mssql-server start```
* STOP: ```sudo service mssql-server start```
* CHECK STATUS: ```systemctl status mssql-server --no-pager```

**B) Da WSL:**
* Al posto dei comandi sopra, utilizzare TUTTO questo comando invece (è tutto una sola riga): ```sudo -b -u mssql /opt/mssql/bin/sqlservr -c -d/var/opt/mssql/data/master.mdf -l/var/opt/mssql/data/mastlog.ldf -e/var/opt/mssql/log/errorlog -x >/dev/null```




## 2. PARAMETRI CONNESSIONE:
**NOTA**: alla prima connessione è necessario creare un DB vuoto, chiamato *NovoticAI*, in cui importeremo i dump. Sequire le istruzioni qui (punto 3) usando **GLI STESSI** nomi per DB, username e passwords indicati -> https://docs.google.com/document/d/1Hg8LUDYuBbO3p3FYNTM139w2DzV25sPZxpKnWhFTuPc/edit

Dopo la prima connessione, i parametri ricorrenti di connessione al DB in localhost sono i seguenti:
* **DA VSCODE:** hostname ```127.0.0.1```, username ```SA```, password ```AIchallenge6```. Mettere ```NovoticAI``` sia come nome DB che come nome profilo.
* **DA PYODBC:** driver ```{ODBC Driver 17 for SQL Server}```, server ```127.0.0.1```, database ```NovoticAI```, username ```sa```, password ```AIchallenge6```
* * **DA BASH:** (solo per creare DB la prima volta o per rare eventualità) ```sqlcmd -S 127.0.0.1 -U SA -P AIchallenge6```

Guida documentazione Pyodbc per utilizzo e query da Python:
* https://github.com/mkleehammer/pyodbc/wiki


## 3. PER IMPORTARE IL DUMP DEL DB (SOLO IN CASO DI NUOVI DUMP):
* TBD


## 4. PER CHIAMARE LE QUERY:
* Non useremo classi.
* Scrivere le query direttamente nella cartella *“queries”* creando **più file *.sql* separati (uno per query)**.
* **In ogni file Python**: aprire e chiudere le connessioni al DB chiamando le funzioni ```db_connect()``` (all'inizio del file) and ```db_disconnect(conn, cursor)``` (alla fine del file) presenti nel file *db_connect.py*. La ```db_connect()``` ritorna 2 oggetti: una connessione *conn* e un cursore *cursor*.
* Ogni volta che si chiama una query in Python, vanno lanciati 2 comandi: **1)** ```cursor.execute(query)```, che esegue la query nella RAM; **2)** ```cursor.commit()```, che esegue la query nel DB. **NOTA: LE QUERY NON VENGONO ESEGUITE SENZA CURSOR.COMMIT()!!!
* **Per chiamare le query nelle funzioni python**: chiamare i file *.sql* dove avete scritto la query di riferimento ed eseguire con:
    ```with open('./queries/<filename>.sql', mode='r') as query:
        cursor.execute(query)
        cursor.commit()```


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
I comandi principali da eseguire dentro la cartella local della repository sono:  
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
da usare nel caso ci siano conflitti per salvare il lavoro locale e fare il pull da remoto, in questo modo i cambiamenti apportati rimangono salvati in locale e si possono recuperare (ovviamente a questo punto il pull prende la repo così come è su github e eventuali cambiamenti sono da rifare).

