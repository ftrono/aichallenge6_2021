from access_db import query_bycombo, query_tgtvectors
from stats import evaluate
from utils import normalize, interpolate_curve, visualize
from stats import ideal_curve, stdev_curve, max_targets

sigmac = 3
sigmaf = 1

#LAUNCH ALGORITHM DEMO:

#HELPER FUNCTIONS:
#normalize and interpolate all curves in combo:
def nni_combo(combo, altezza_combo):
    for series in combo.series:
        newh, newf = interpolate_curve(altezza_combo, series.altezza, series.forza)
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
    
    forza_combo = ideal_curve(batch_forces)
    std_curve = stdev_curve(batch_forces, sigmac)
    max_force, std_mf = max_targets(batch_max, sigmaf)

    return forza_combo, std_curve, max_force, std_mf


#DEMO:

#LAUNCH DEMO:
def demo(taglia, id_comp):
    #1) PREPROCESSING:
    print("Phase 1 - Preprocessing...")
    #get orig curves:
    combo = query_bycombo(taglia,id_comp)
    #get target vector for the combo:
    _, _, altezza_combo = query_tgtvectors(taglia, id_comp)
    #normalize and interpolate curves in all combo:
    combo = nni_combo(combo, altezza_combo)
    
    #2) TRAIN:
    print("Phase 2 - Training...")
    #get the 4 key Target Parameters:
    forza_combo, std_curve, max_force, std_mf = bs_demo(combo, sigmac, sigmaf)
    print("Avg std_dev for curve: {}". format(std_curve))

    #3) EVALUATE:
    print("Phase 3 - Testing...")
    #test on new curve:
    frz = combo.series[0].forza
    mfrz = combo.series[0].max_forza
    print("Current max_forza: {}, Target max_forza: {}, Acceptable delta: +-{}".format(mfrz, max_force, std_mf))

    cnt = evaluate(mfrz, frz, forza_combo, std_curve, max_force, std_mf)
    
    #VISUALIZE CURVES:
    visualize(forza_combo, std_curve, altezza_combo, frz)

    return cnt


#MAIN:
#combos tested:
#"MP080", "a0206"
#"MP060", "a0007"
#"MP080", "a0211"
#"MP080", "a0215"
demo("MP080", "a0206")

