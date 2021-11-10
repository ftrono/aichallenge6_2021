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
  * *visualize(forza_combo, std_curve, altezza_combo, cur_forza)*
* Per plottare una singola curva:
  * *plot_single(id, x, y, <span>**</span>title)*

D) Interpolazione e normalizzazione:
* *normalize(y_data, plot=False)*
* *interpolate_curve(altezza_combo, altezza, forza)*


**STATS.PY**

A) Calcolo curva forza ideale:
* *ideal_curve(in_curves)*

B) Calcolo average std per curva forza:
* *stdev_curve(in_curves, sigma=1)*

C) Calcolo target max_forza (o max_altezza) e std_MF (o std_MA):
* *max_targets(max_values, sigma=1)*

D) Calcolo parametri per singola combo (taglia, id_comp):
* *batch_standardize(taglia, id_comp, sigmac=1, sigmaf=1)*

E) Funzione di valutazione nuova curva:
* *evaluate(cur_mf, cur_forza, forza_combo, std_curve, target_mf, std_mf)*

