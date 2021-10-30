from access_db import query_bycombo, query_tgtvectors
from stats import evaluate
from utils import interpolate_curve, plot_curves
from stats import ideal_curve, threshold_variance, max_force_threshold

#LAUNCH ALGORITHM DEMO:

#HELPER FUNCTIONS:
#normalize and interpolate all curves in combo:
def nni_combo(combo, tgt_h):
    for series in combo.series:
        newh, newf = interpolate_curve(tgt_h, series.altezza, series.forza)
        series.altezza = newh
        series.forza = newf
    return combo


#COPY of bs (ONLY for DEMO):
def bs_demo(combo, train_len = None):

    batch_forces = []
    batch_max = []
    
    if not train_len:
        train_len = -1

    for series in combo.series[0:train_len]:
        batch_forces.append(series.forza)
        batch_max.append(series.max_forza)
    
    curva_ideale = ideal_curve(batch_forces)
    avg_var = threshold_variance(batch_forces)
    max_force,threshold = max_force_threshold(batch_max)

    return curva_ideale,avg_var,max_force,threshold

#______________________________________________
#DEMO:
#______________________________________________

#LAUNCH DEMO:
def demo(taglia, idcomp, valpcg = None):
    #1) PREPROCESSING:
    print("Phase 1 - Preprocessing...")
    #get orig curves:
    combo = query_bycombo(taglia,idcomp)
    #get target vector for the combo:
    _, _, tgt_h = query_tgtvectors(taglia, idcomp)
    #normalize and interpolate curves in all combo:
    combo = nni_combo(combo, tgt_h)
    
    #2) TRAIN:
    print("Phase 2 - Training...")
    #define validation split:
    if valpcg:
        train_len = round(valpcg * len(combo.series), 0)
    else:
        train_len = -1
    #get the 4 key Target Parameters:
    curva_ideale, avg_var, max_force, threshold = bs_demo(combo, train_len)
    print("Avg variance for curve: {}". format(avg_var))

    #3) EVALUATE:
    print("Phase 3 - Testing...")
    #test on new curve:
    frz = combo.series[0].forza
    mfrz = combo.series[0].max_forza
    print("Current max_forza: {}, Target max_forza: {}, Accettable delta: +-{}".format(mfrz, max_force, threshold))

    cnt = evaluate(mfrz, frz, curva_ideale, avg_var, max_force, threshold)
    
    #VISUALIZE CURVES:
    plot_curves(curva_ideale, avg_var, tgt_h, frz)

    return cnt

#MAIN:
demo("MP080", "a0206")

