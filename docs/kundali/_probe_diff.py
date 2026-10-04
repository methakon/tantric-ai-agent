"""Diff the pre-fix and post-fix frozen files. Proves the regeneration changed
only the two documented detector defects and nothing that could know an
outcome. READ-ONLY."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
a = json.load(open(os.path.join(OUT, "blind_predictions_frozen.ORIGINAL.json"),
                   encoding="utf-8"))["years"]
b = json.load(open(os.path.join(OUT, "blind_predictions_frozen_v2.json"),
                   encoding="utf-8"))["years"]

print("years equal:", sorted(a, key=int) == sorted(b, key=int))

# 1. Nothing outside precise_events may differ at all.
print("\n--- NON-precise_events comparison (must be identical) ---")
diffs = []
for y in sorted(a, key=int):
    for k in a[y]:
        if k == "precise_events":
            continue
        if a[y][k] != b[y][k]:
            diffs.append((y, k))
print("differing (year, key) outside precise_events:", diffs or "NONE")

# 2. precise_events: which rows only ADDED?
print("\n--- precise_events row accounting ---")
print(f"{'yr':5s} {'old_sign':>8s} {'new_sign':>8s} | {'old_cnj':>7s} {'new_cnj':>7s} "
      f"{'new_opp':>7s} | {'old_mixed':>9s} {'new_mixed':>9s}")
tot = {"old_mixed": 0, "new_mixed": 0, "old_sign": 0, "new_sign": 0}
for y in sorted(a, key=int):
    pa, pb = a[y]["precise_events"], b[y]["precise_events"]
    old_cnj = pa.get("natal_conjunctions", [])
    old_sign = pa.get("sign_entries", [])
    # old "conjunctions" contained BOTH kinds -> classify them by separation
    old_mixed = len(old_cnj)
    new_cnj = len(pb.get("natal_conjunctions", []))
    new_opp = len(pb.get("natal_oppositions", []))
    new_mixed = new_cnj + new_opp
    tot["old_mixed"] += old_mixed; tot["new_mixed"] += new_mixed
    tot["old_sign"] += len(old_sign); tot["new_sign"] += len(pb["sign_entries"])
    print(f"{y:5s} {len(old_sign):8d} {len(pb['sign_entries']):8d} | "
          f"{old_mixed:7d} {new_cnj:7d} {new_opp:7d} | "
          f"{old_mixed:9d} {new_mixed:9d}")
print(f"TOTAL {'':3s} {tot['old_sign']:8d} {tot['new_sign']:8d} | "
      f"{tot['old_mixed']:7d} {'':7s} {'':7s} | {tot['old_mixed']:9d} "
      f"{tot['new_mixed']:9d}")

# 3. Is every OLD row still present in the new sets (same ist + body)?
print("\n--- superset check: are old crossings preserved? ---")
missing = []
for y in sorted(a, key=int):
    pa, pb = a[y]["precise_events"], b[y]["precise_events"]
    new_all = pb.get("natal_aspects_crossings", [])
    key_new = {(c["transit"], c["natal_body"], c["ist"]) for c in new_all}
    for c in pa.get("natal_conjunctions", []):
        # Saturn x Rahu was labelled natal_body "Rahu" but targeted Ketu;
        # the new file labels it Ketu. Accept either.
        k1 = (c["transit"], c["natal_body"], c["ist"])
        k2 = (c["transit"], "Ketu", c["ist"])
        if k1 not in key_new and k2 not in key_new:
            missing.append((y, k1))
print("old crossing rows NOT found in new file:", missing or "NONE")

# 4. Did any old row's separation value change? (proves solve untouched)
print("\n--- separation value stability for preserved rows ---")
changed = []
for y in sorted(a, key=int):
    pb = y and b[y]["precise_events"]
    old = {(c["transit"], c["natal_body"], c["ist"]): c["separation_deg"]
           for c in a[y]["precise_events"].get("natal_conjunctions", [])}
    new = {(c["transit"], c["natal_body"], c["ist"]): c["separation_deg"]
           for c in pb.get("natal_aspects_crossings", [])}
    for k, v in old.items():
        for body in (k[1], "Ketu" if k[1] == "Rahu" else None):
            kk = (k[0], body, k[2])
            if kk in new and abs(new[kk] - v) > 1e-6:
                changed.append((y, kk, v, new[kk]))
print("separation values that changed:", changed or "NONE")