# Documentazione AI Challenge -> Teams 6:  **Novotic**
 
**INDICE FUNZIONI CONTENUTE NEI FILES:**
___


**DB_CONNECT.PY**

* Parametri globali di connessione
* *db_connect()*
* *db_disconnect(conn, cursor)*

___

**UTILS.PY**

A) CSV name parser:
* *name_parser(name)*

B) Visualizzazione grafica curve (grafico completo con curva ideale, boundaries e curva corrente):
  * *visualize(forza_combo, std_curve, altezza_combo, cur_forza)*

C) Interpolazione:
* *interpolate_curve(altezza_combo, altezza, forza)*

___

**STATS.PY**

A) Calcolo curva forza ideale:
* *ideal_curve(in_curves)*

B) Calcolo average std per curva forza:
* *stdev_curve(in_curves, sigma=1)*

C) Calcolo target max_forza (o max_altezza) e std_MF (o std_MA):
* *max_targets(max_values, sigma=1)*

D) Calcolo parametri per singola combo (taglia, id_comp):
* *batch_standardize(taglia, id_comp, sigmac=1, sigmaf=1)*

___

**EVALUATE.PY**

Funzione di valutazione nuova curva:
* *evaluate_curve(timestamp, visual)*

