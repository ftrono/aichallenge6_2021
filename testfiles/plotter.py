import pandas as pd
import matplotlib.pyplot as plt

DIR = './testfiles/exp'

Curve = pd.read_csv(f"{DIR}/csv.csv")
Curve.drop(columns='Index', inplace=True)
print(Curve)
inf = 510
upp = 640

fig, ax = plt.subplots(1,1, constrained_layout=True)
ax.plot(Curve['Target_Altezza'][inf:upp], Curve['Current_Forza'][inf:upp], color='black')
ax.plot(Curve['Target_Altezza'][inf:upp], Curve['Upper_Boundary'][inf:upp], color='gray', linestyle='--', linewidth=1)
ax.plot(Curve['Target_Altezza'][inf:upp], Curve['Lower_Boundary'][inf:upp], color='gray', linestyle='--', linewidth=1)
ax.set_xlabel("Displacement (mm)")
ax.set_ylabel("Force (kN)")
fig.savefig(f"{DIR}/curve.png", format='png')

