import json
import sys
from collections import Counter

fichier = sys.argv[1] if len(sys.argv) > 1 else 'reports/flaml_60s.log'
essais = []

with open(fichier, encoding='utf-8') as f:
    for ligne in f:
        ligne = ligne.strip()
        if ligne.startswith('{'):
            try:
                e = json.loads(ligne)
                if 'learner' in e and e.get('validation_loss') is not None:
                    essais.append(e)
            except json.JSONDecodeError:
                continue

print(len(essais), 'essais journalises dans', fichier)

print(
    'essais par famille:',
    dict(Counter(e['learner'] for e in essais))
)

if not essais:
    print("Aucun essai exploitable trouve dans le fichier log.")
    sys.exit(0)

# Meilleur essai de chaque famille
meilleurs = {}

for e in essais:
    famille = e['learner']
    if (
        famille not in meilleurs
        or e['validation_loss'] < meilleurs[famille]['validation_loss']
    ):
        meilleurs[famille] = e

print('\nMeilleur F1 de validation par famille (F1 = 1 - perte) :')

for famille, e in sorted(
    meilleurs.items(),
    key=lambda kv: kv[1]['validation_loss']
):
    print(
        f"  {famille:15s} "
        f"F1 val = {1 - e['validation_loss']:.4f} "
        f"(trouve apres {e.get('wall_clock_time', 0):.1f} s)"
    )

# Essai gagnant
gagnant = min(essais, key=lambda e: e['validation_loss'])

print('\nEssai gagnant :', gagnant['learner'])
print('Configuration :', gagnant.get('config'))