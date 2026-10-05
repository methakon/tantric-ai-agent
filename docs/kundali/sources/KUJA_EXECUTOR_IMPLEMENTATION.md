# KUJA EXECUTOR IMPLEMENTATION

Status at checkpoint `815126c`:

```
SOURCE STATUS:       VERIFIED / FROZEN
RULE STATUS:         REGISTERED
EXECUTION STATUS:    IMPLEMENTED (executor exists; registry remains REGISTERED)
COMPUTABILITY:       dependent on authorized chart scope
PERSONAL EVALUATION: NOT RUN
```

## Frozen rule applied

```
KUJA_FORMATION_HOUSES = {1, 4, 7, 8, 12}
reference              = Ascendant / Lagna
source                 = BPHS Ch. 80, v.47
source_ref             = Girish/Chatur Vol. II, PDF index 712, printed p.692
exact_text             = लग्ने व्यये सुखे वाऽपि सप्तमे वाऽष्टमे कुजे ।
                         शुभदृग्योगहीने च पति हन्ति न संशयः ।।४७।।
```

`लग्ने` is retained as the source-derived 1st-house term. The 2nd house,
Moon/Venus reference points, numerical orb, severity grades and additional
popular bhanga rules are excluded. The Santhanam English rendering omits the
Lagna term; that is recorded neutrally as an unresolved translation/editorial
or recension discrepancy, not silently corrected.

The benefic clause (`शुभदृग्योगहीने`) is part of FORMATION: Mars must have
neither benefic association nor benefic aspect. It is not automatically a
cancellation. v.49 mutual-match cancellation remains a separate rule.
Strength is `UNSPECIFIED_BY_SOURCE`; orb is `UNSPECIFIED_BY_SOURCE`; chart
scope remains `TO BE CONFIRMED`.

## Architecture

`methods/kuja_executor.py` applies the frozen registry specification. It does
not define the house set. It reuses the project's authoritative
`kundali_core.house_of(mars_longitude, ascendant_sign)` whole-sign D1 helper;
no duplicate house calculation and no Kuja-specific boundary/orb exists.

The executor accepts explicit `native`, `scope` and optional `partner` data:

- `mars_longitude`: required numeric sidereal longitude
- `ascendant_longitude`: required numeric sidereal longitude
- `planet_longitudes`: optional explicit planet→longitude mapping; missing
  benefics are absent, never assumed
- `scope`: explicit `ChartScope(sex, varga, authorized, authority_note)`
- `partner`: optional explicit partner chart for v.49 only

### Default-deny chart scope

The source scope is unresolved: v.47 is written about a woman's horoscope and
v.48 extends the yoga to the male, but the text does not establish the modern
native-wide compatibility scope. There was no existing scope enum, so the
executor introduces a representation without authorizing one:

```
AUTHORIZED_SCOPES = ()
```

Every production call therefore returns `NOT_COMPUTABLE` (the executor alias
for the registry's canonical `NOT_IMPLEMENTED`) until a human authorizes a
scope. The test-only helper scope is explicitly not production authorization.
This prevents silently assuming female or male applicability.

Malformed charts and unsupported scope objects are rejected with
`NOT_COMPUTABLE`; the executor never guesses missing longitudes.

## Result model

`KujaResult` exposes:

- `state`: registry canonical `NOT_IMPLEMENTED`, `NO_FORMATION`,
  `FORMATION_PRESENT`, or `CANCELLED`
- `state_alias`: brief vocabulary `NOT_COMPUTABLE`, `NO_FORMATION`,
  `FORMATION`, or `FORMATION_CANCELLED`
- `formation`: whether v.47 formed
- `cancelled`: whether v.49 mutual-match cancellation applied
- `bhanga_evaluated`: whether a partner was supplied and v.49 was tested
- `reason`: explicit explanation
- `provenance`: source refs, exact text, houses, evaluated Mars house,
  formation-set membership, benefic findings, partner findings and explicit
  excluded-feature disclosures

A cancelled yoga keeps `formation=True`; formation and cancellation are never
collapsed.

## Test fixtures

`tests/test_kuja_executor.py` contains the required conceptual fixtures using
synthetic charts only — no personal chart and no empirical claim:

1. Positive: each of the five qualifying houses forms when the benefic
   formation condition is clear.
2. Negative: every excluded house, including the 2nd, does not form.
3. Boundary: exact whole-sign transitions, including 1st↔2nd and 12th↔1st,
   match `kundali_core.house_of`; no orb is applied.
4. Bhanga: both native and partner form; `formation=True`, `cancelled=True`,
   final alias `FORMATION_CANCELLED`.
5. Wrong scope: missing, unresolved, unauthorized and malformed scopes return
   `NOT_COMPUTABLE` before chart inspection.

Additional tests cover all four benefics for association/aspect, malformed
inputs, provenance, exclusion guards, registry immutability and the empty
production authorization set.

## Explicit non-claims

This executor has not evaluated Swarna Sekhar Dhar's chart. It has not been
connected to the risk engine, yearly predictions, PDF renderer, life-event
validation, Ashtakavarga, Shadbala, Nadi, Job Agent or Trading Agent.

This is source/rule implementation, not predictive validation.
