"""Prove the composer differentiates years that share a dasha lord.

The failure this guards: 1987-2037 is one continuous Rahu Mahadasha, so naive
prose would be identical across ~50 years. This runs the REAL activation
extraction for consecutive years inside that Mahadasha and asserts the composed
output differs.
"""
import datetime
import json
import os
import sys

sys.path.insert(0, '/home/swarna-sekhar-dhar/projects/tantra/docs/kundali')
import composer as CP
import data_2026 as D

OUT = '/home/swarna-sekhar-dhar/projects/tantra/docs/kundali/out'
tl = json.load(open(os.path.join(OUT, 'risk_timeline.json'), encoding='utf-8'))

# natal structure from the production dataset
natals = {}
ds = json.load(open(os.path.join(OUT, 'kundali_data.json'), encoding='utf-8'))
lordship = {}
for p in ds['planets']:
    if p['body'] == 'Ascendant':
        continue
    natals.setdefault(p['house_whole_sign'], []).append(p['body'])
import kundali_core as K
ASC = K.sign_of(ds['ascendant']['longitude_sidereal'])
for h_ in range(1, 13):
    lordship[h_] = K.SIGN_LORDS[(ASC + h_ - 1) % 12]

natals['_lordship'] = {h_: lordship[h_] for h_ in range(1, 13)}
# map each planet to the house it occupies, for the lord-placement lookup
natals['_lord_house'] = {p['body']: p['house_whole_sign']
                         for p in ds['planets'] if p['body'] != 'Ascendant'}

SAMPLES = {}
print("=" * 78)
print("ACTIVATION EXTRACTION ACROSS CONSECUTIVE YEARS (same Rahu Mahadasha)")
print("=" * 78)
print(f"{'Year':<7}{'MD':<9}{'AD':<9}{'PD':<9}{'Activated houses':<40}{'Total score':>11}")
print("-" * 78)
for row in tl['years']:
    if row['year'] not in (1987, 1988, 1989, 1990, 1994, 1997, 2000, 2002):
        continue
    tr = {}
    for g in ('saturn', 'jupiter', 'rahu', 'ketu'):
        info = row['transit'][g]
        tr[g.capitalize()] = {'house': info['house'], 'aspects': info['aspects']}
    acc = CP.activation_phrase(natals, tr,
                               (row['mahadasha'], row['antardasha'],
                                row['pratyantardasha']))
    houses = sorted(acc)
    total = sum(v['score'] for v in acc.values())
    print(f"{row['year']:<7}{row['mahadasha']:<9}{row['antardasha']:<9}"
          f"{row['pratyantardasha']:<9}"
          f"{str(houses):<40}{total:>11}")
    # houses this antardasha lord occupies OR rules - the union the composer
    # needs. Passing only occupancy made every graha claim to hold nothing.
    ad = row['antardasha']
    ad_houses = sorted({natals['_lord_house'][ad]} |
                       {hh for hh, ld in lordship.items() if ld == ad})
    phase_lines = CP.compose_phase(ad, ad_houses, 'AD')
    house_lines = {}
    for hh in houses:
        house_lines[hh] = CP.compose_house(hh, acc, natals, lordship)[:3]
    SAMPLES[row['year']] = {'phase': phase_lines, 'houses': house_lines}

print()
print("=" * 78)
print("NON-BOILERPLATE SELF-TEST")
print("=" * 78)
ok, msg = CP.assert_not_boilerplate(SAMPLES)
print(f"  first-pair check: {'PASS' if ok else 'FAIL'} — {msg}")

# stronger test: EVERY consecutive pair must differ
flat = {y: json.dumps(v, sort_keys=True) for y, v in SAMPLES.items()}
keys = sorted(flat)
dups = []
for i in range(len(keys) - 1):
    if flat[keys[i]] == flat[keys[i + 1]]:
        dups.append((keys[i], keys[i + 1]))
print(f"  consecutive-pair check: {'PASS' if not dups else 'FAIL'}")
if dups:
    for a, b in dups:
        print(f"     identical: {a} == {b}")

# show an actual divergence so this is evidence, not assertion
ys = sorted(SAMPLES)
print()
print("  Example — AD-phase text for two different years:")
for y in (ys[0], ys[-1]):
    md = tl_rows = next(r for r in tl['years'] if r['year'] == y)
    print(f"    {y} ({md['mahadasha']}/{md['antardasha']}/{md['pratyantardasha']}):")
    for line in SAMPLES[y]['phase']:
        print(f"      {line}")

print()
print("  Example — H6 activation text, two years:")
for y in (ys[0], ys[-1]):
    if 6 in SAMPLES[y]['houses']:
        md = next(r for r in tl['years'] if r['year'] == y)
        print(f"    {y}:")
        for line in SAMPLES[y]['houses'][6][:3]:
            print(f"      {line}")

assert not dups, "consecutive years produced identical prose"
print()
print("RESULT: composer differentiates years that share a dasha lord.")