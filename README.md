# AI challenge - Team 6
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

