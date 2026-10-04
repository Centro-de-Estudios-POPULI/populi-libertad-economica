"""
maddison_poblacion.py — deriva data/poblacion_maddison.json (población en miles por país y año, 2000-2022)
de data/mpd2023.xlsx (Maddison Project Database 2023, hoja «Full data»; el Excel no va en git).
La usa generate_charts.py para el promedio mundial ponderado por población.

    python maddison_poblacion.py
"""
import json
import pandas as pd

df = pd.read_excel('data/mpd2023.xlsx', 'Full data')
df = df[(df['year'] >= 2000) & df['pop'].notna()]
pob = {}
for r in df.itertuples():
    pob.setdefault(r.countrycode, {})[str(int(r.year))] = round(float(r.pop), 3)
with open('data/poblacion_maddison.json', 'w', encoding='utf-8') as f:
    json.dump(dict(sorted(pob.items())), f, ensure_ascii=False, separators=(',', ':'))
print(f'data/poblacion_maddison.json: {len(pob)} países')
