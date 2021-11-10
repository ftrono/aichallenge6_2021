# Documentazione AI Challenge -> Teams 6:  **Novotic**
 
**INDICE FUNZIONI CONTENUTE NEI FILES:**
___


**UTILS.PY**

A) Connessione a DB:
* Parametri globali di connessione
* *db_connect()*
* *db_disconnect(csr, conn)*

B) CSV name parser:
* *name_parser(name)*

C) Visualizzazione grafica curve:
* Per visualizzare grafico completo con curva ideale, boundaries e curva corrente:
  * *plot_curves(curva_ideale, avg_var, tgt_h, cur_forza)*
* Per plottare una singola curva:
  * *plot_series(id, x, y, <span>**</span>title)*

D) Interpolazione e normalizzazione:
* *normalize(y_data, plot=False)*
* *interpolate_curve(tgt_h, altezza, forza)*


**STATS.PY**

A) Calcolo curva forza ideale:
* *ideal_curve(input)*

B) Calcolo average std per curva forza:
* *threshold_variance(input, sigma=1)*

C) Calcolo target max_forza e std_MF:
* *max_force_threshold(max_values, sigma=1)*

D) Calcolo parametri per singola combo (taglia, idcomp):
* *batch_standardize(taglia,idcomp, sigmac=1, sigmaf=1)*

E) Funzione di valutazione nuova curva:
* *evaluate(max_forza, forza, curva_ideale, avg_var, mf_tgt, mf_threshold)*

