# AI challenge - Team 6 :octocat:
# Premessa:
Gli script presenti in questa repository sono stati ideati per essere eseguiti su un sistema operativo **linux** e sono testati su Ubuntu 18.04 LTS  
### Prerequisiti:  
* Python 3.3 o superiore   
* [Microsoft (MS) SQL Server](https://docs.microsoft.com/en-us/sql/linux/quickstart-install-connect-ubuntu?view=sql-server-ver15)  
* *pyodbc* drivers (```pip3 install pyodbc``` o ```pip install pyodbc```)  
### Suggerimenti:  
* Installare MS SQL Server direttamente su Ubuntu o in WSL ([guida step by step](https://docs.google.com/document/d/1Hg8LUDYuBbO3p3FYNTM139w2DzV25sPZxpKnWhFTuPc/edit))

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


## 2. PRIMA CONNESSIONE & PARAMETRI LOCALI:
**CONFIGURAZIONE:**
* Importare nella cartella *database_functions* il file **db_credentials.ini** disponibile [qui](https://drive.google.com/drive/u/1/folders/1lFm7PQQA9tgsBYPt7f2rMdNAAO9c__fD) (modificarlo solo se i parametri personali sono diversi).

**PARAMETRI COMUNI:**
* **DA PYODBC:** driver ```{ODBC Driver 18 for SQL Server}```, server ```127.0.0.1```, database ```NovoticAI```, username ```sa```, password ```AIchallenge6```, encrypt ```no```
* **DA VSCODE (estensione):** in hostname, inserire la stringa ```SERVER=127.0.0.1;DATABASE=NovoticAI;ENCRYPT=no;UID=sa;PWD=AIchallenge6``` e poi usare ```NovoticAI``` come nome profilo.
* **DA BASH:** *(solo per creare DB la prima volta o per rare eventualità)* ```sqlcmd -S 127.0.0.1 -U SA -P AIchallenge6``` **NOTA**: alla prima connessione è necessario creare un DB vuoto, chiamato *NovoticAI*, in cui importeremo i dump. Sequire le istruzioni [qui](https://docs.google.com/document/d/1Hg8LUDYuBbO3p3FYNTM139w2DzV25sPZxpKnWhFTuPc/edit) (punto 3) usando GLI STESSI nomi per DB, username e passwords indicati.


## 3. APRIRE E CHIUDERE LE CONNESSIONI AL DB:
* NOTA: Solo nella macrofunzione della vostra parte: aprire e chiudere le connessioni al DB chiamando:
    ```
    import sys
    sys.path.insert(0, './')
    from db_connect import db_connect, db_disconnect
    
    # (all'inizio del file) open connection:
    conn, cursor = db_connect()
    
    # (alla fine del file) close cursor and connection:
    db_disconnect(conn, cursor)
    
    ```
* Per importare i moduli della repo, usare:
    ```
    import sys, os
    sys.path.insert(0, os.getcwd())
    from <subfolder>.<module> import <functions>
    ```
* Se una sottofunzione deve fare una query (meglio di no), passargli conn e cursor. NOTA: meglio usare Pandas invece.
* Ogni volta che si chiama una query in Python, vanno lanciati 2 comandi: **1)** ```cursor.execute(query)```, che prepara la query; **2)** ```cursor.commit()```, che aggiorna effettivamente il DB. **OPPURE (meglio): usare Pandas!
* [Guida documentazione Pyodbc](https://github.com/mkleehammer/pyodbc/wiki) per utilizzo e query da Python.


## 4) PER LANCIARE LE FUNZIONI NELL'ALGORITMO DI TRAINING / EVALUATION (nota: non vale per l'export):
* Usare SOLO il file Launcher. Tenere scommentata solo la funzione da lanciare.


## 5) PANDAS:

Per i SELECT consigliamo di scaricare tutte le tabelle SQL utili, già filtrate in senso largo (in modo da non doverle chiamare da capo), una sola volta e solo nella macrofunzione della vostra parte. 

Invece di usare *cursor.execute()*, usare direttamente i **[Dataframe di Pandas](https://pandas.pydata.org/docs/reference/frame.html)**. In questo modo, la query viene automaticamente eseguita e convertita in una tabella Dataframe da cui si possono leggere e gestire i dati. Le colonne possono anche essere convertite in liste.
```
import pandas as pd

# IMPORTARE DA SQL IN UN DATAFRAME:
query = "SELECT ........"
df = pd.read_sql(query, conn)
# (si usa al posto di execute e commit!)
```
Conviene chiamare i dataframe con gli stessi nomi delle tabelle SQL (o con nomi chiari), in modo che si capisca cosa sono!

Esempi pratici di utilizzo:

**Import da SQL a Pandas:**

```
# scrivete una query sql onnicomprensiva con tutte le colonne che vi servono: 
querysql = "SELECT Timestamp, ComboID, MaxAltezza FROM Pressate"

# eseguire la query in questo modo creando un dataframe di nome Pressate:
Pressate = pd.read_sql(querysql, cnxn) 

# per visualizzare il dataframe:
print(Pressate)

# Per accedere a una colonna invece basta chiamarla con la sua intestazione (la stessa della tabella SQL!):
# es. Pressate['Timestamp']
```
    
**Query in Pandas:**

Si possono fare le STESSE cose di SQL! Solo con una sintassi diversa.

Ad ogni query, Pandas crea una sottotabella (separata) della tabella:
```
# Ho modi diversi per eseguire una query, a seconda se voglio filtrare per una stringa o per un numero:

# a) query se una colonna ha stringhe:
# es. voglio creare una sottotabella del dataframe Pressate in cui ci sono solo le Pressate con il ComboID "p0001MP080":

#stringa:
query = 'ComboID == "p0001MP080"'
# stringa alternativa (con variabile):
gino = 'p0001MP080'
query = 'ComboID == "'+str(gino)+'"'

# eseguo la query Pandas nel dataframe, ottenendo una sottotabella che chiamo PressateCombo
PressateCombo = Pressate.query(query)
print(PressateCombo)


# b) query se una colonna ha numeri invece di stringhe:
# es. voglio creare una sottotabella del dataframe Pressate in cui c'è solo la pressata con un timestamp (che è un int):
timestamp = 1585567478
# notare come cambia la sintassi:
Pressata = Pressate[Pressate['Timestamp'] == timestamp]

```
OUT:
```
Pressate:
      Timestamp     ComboID  MaxAltezza
0    1584106101  p0038MP080      206.95
1    1584106118  p0007MP080      200.05
2    1584106142  a0207MP080      189.35
3    1584106237  p0001MP080      160.79
4    1584106258  p0008MP080      156.16
..          ...         ...         ...
983  1585573900  p0004MP105      166.04
984  1585573951  p0004MP105      166.04
985  1585573979  p0004MP105      166.04
986  1585574002  p0004MP105      166.04
987  1585574477  a0211MP105      270.57

[988 rows x 3 columns]


PressateCombo:
      Timestamp     ComboID  MaxAltezza
3    1584106237  p0001MP080      160.79
9    1584106518  p0001MP080      160.80
16   1584106927  p0001MP080      160.80
65   1584347409  p0001MP080      160.80
79   1584348491  p0001MP080      160.80
91   1584348627  p0001MP080      160.80
103  1584348763  p0001MP080      160.79
115  1584349542  p0001MP080      160.80
128  1584349667  p0001MP080      160.79
144  1584349802  p0001MP080      160.79
165  1584353423  p0001MP080      160.79
166  1584353424  p0001MP080      160.79

```

**Notare come cambia la lista di indici alla prima colonna della sottotabella!** E' importante ricordarsi che gli indici di una sottotabella possono NON essere consecutivi a causa del filtro (seguono le righe originali).

Per questo motivo, per accedere a una riga si possono usare 2 modi:
```
# Per accedere a una riga:
# a) .iloc[...] -> restituisce la posizione reale della riga a prescindere dal suo indice post-filtro: 
max_altezza = float(PressateCombo['MaxAltezza'].iloc[0])
# OUT: 160.79

# b) .loc[...] -> restituisce la posizione della riga secondo il suo indice originale (che, per la prima riga all'esempio in alto, NON è 0 ma è 3!!!!!!!): 
max_altezza = float(PressateCombo['MaxAltezza'].loc[3])
# OUT: 160.79
```
Metodi utili:
```
# Convertire intere colonne in liste:
timestamps = Pressate['Timestamp'].tolist()

# Convertire intere colonne in liste ma solo con gli elementi distinti (equivale al DISTINCT di SQL):
combo_list = Pressate['ComboID'].unique().tolist()

# FARE IL JOIN TRA TABELLE (supponiamo esista un secondo dataframe chiamato Warnings):
# es. inner join con tabella Warnings (NOTA: crea sottotabella con tutte le colonne ma SOLO LE RIGHE COMUNI!!!)
Commons = Pressate.merge(Warnings, on=["Timestamp"])
print(Commons)

# Ottenere l'indice di posizione di una riga:
row = Pressate.index
# o una lista con tutti gli indici di una colonna (che, appunto, possono non essere consecutivi):
rows = Pressate.index.values.tolist()

# Cancellare una riga (o una lista di righe) dalla tabella:
Pressate.drop(rows, inplace=True)

```
**GUIDE UTILI:**
* Queries: https://www.geeksforgeeks.org/python-filtering-data-with-pandas-query-method/
* Joins: https://www.shanelynn.ie/merge-join-dataframes-python-pandas-index-1/
* Per il resto: Google.

---

**Altre info di configurazione sono disponibili in questa [folder](https://drive.google.com/drive/folders/1lOZpjl8pjfPhmlcCdAh9lYgR5AYi0LUy) Drive.**

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

