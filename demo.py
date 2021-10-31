from access_db import query_bycombo, query_tgtvectors
from stats import evaluate
from utils import normalize, interpolate_curve, plot_curves
from stats import ideal_curve, threshold_variance, max_force_threshold

sigmac = 3
sigmaf = 1

#LAUNCH ALGORITHM DEMO:

#HELPER FUNCTIONS:
#normalize and interpolate all curves in combo:
def nni_combo(combo, tgt_h):
    for series in combo.series:
        newh, newf = interpolate_curve(tgt_h, series.altezza, series.forza)
        newf = normalize(newf)
        series.altezza = newh
        series.forza = newf
    return combo


#COPY of bs (ONLY for DEMO):
def bs_demo(combo, sigmac, sigmaf):

    batch_forces = []
    batch_max = []

    for series in combo.series:
        batch_forces.append(series.forza)
        batch_max.append(series.max_forza)
    
    curva_ideale = ideal_curve(batch_forces)
    avg_var = threshold_variance(batch_forces, sigmac)
    max_force, mf_threshold = max_force_threshold(batch_max, sigmaf)

    return curva_ideale, avg_var, max_force, mf_threshold


#DEMO:

#LAUNCH DEMO:
def demo(taglia, idcomp):
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
    #get the 4 key Target Parameters:
    curva_ideale, avg_var, max_force, mf_threshold = bs_demo(combo, sigmac, sigmaf)
    print("Avg variance for curve: {}". format(avg_var))

    #3) EVALUATE:
    print("Phase 3 - Testing...")
    #test on new curve:
    frz = combo.series[0].forza
    mfrz = combo.series[0].max_forza
    print("Current max_forza: {}, Target max_forza: {}, Acceptable delta: +-{}".format(mfrz, max_force, mf_threshold))

    cnt = evaluate(mfrz, frz, curva_ideale, avg_var, max_force, mf_threshold)
    
    #VISUALIZE CURVES:
    plot_curves(curva_ideale, avg_var, tgt_h, frz)

    return cnt


#MAIN:
#combos tested:
#"MP080", "a0206"
#"MP060", "a0007"
#"MP080", "a0211"
#"MP080", "a0215"
demo("MP080", "a0206")

