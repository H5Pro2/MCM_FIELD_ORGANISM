# Lauf 191

## Forschungsfrage und Korrekturgrenze

Geprueft wurde, ob die in Lauf 189 isolierte M-Wirkung von der konkreten
Zuordnung der M-Werte zur festen Feldgeometrie abhaengt.

Grundvertrag:

- `docs/K2_F3_E2_GEOMETRISCHE_M_KAUSALITAET_VORREGISTRIERUNG.md`

Nach dem reinen Serialisierungsabbruch von Lauf 190 galt zusaetzlich:

- `docs/K2_F3_E2_KORREKTURVERTRAG_LAUF_191.md`

Die einzige Korrektur war die Observerkonvertierung von `numpy.bool_` in
natives Python-`bool`. Welt, Probe, Geometrie, Masken, Parameter, Arme und
Entscheidungsregeln blieben unveraendert.

## Gebundene Interventionen

```text
shared probe digest: dba4ae9b51af783ec4abe195eacaac98be94380f1e7125d6cf56f154a15cc927
reflection pairs:    84
reflection digest:   603db647df0717d7c94747e90f98dd907717e08f9830e23c5aa038e4d82d2ffb
left mask size:      36
left mask digest:    c6221c5edee311f8795bdda1de10a30828e5a712e0355d29c1f4faf614217a24
right mask size:     36
right mask digest:   77485ba0a8cd50f54bc83b6e0d00459c5935fb0e346ed95e27a799af5ca9d8d5
```

Die Spiegelung war fuer beide Geschichtsfelder bijektiv, involutiv und
erhielt die komplette M-Wertemultimenge exakt. Beide lokalen
Neutralisierungen erhielten die Gesamtmasse und M-Nichtnegativitaet.

## Beobachtete Messung

Geschichte `same`:

```text
M Linf natural/reflected:       0.0012417220246048084
S Linf natural/reflected:       0.00010883343044029714
H Linf natural/reflected:       0.00016990261203676804
S Linf natural/neutral-left:    0.00011702769627104648
H Linf natural/neutral-left:    0.00018178262741951057
S Linf natural/neutral-right:   0.000048157941036311436
H Linf natural/neutral-right:   0.00008414793824738226
S Linf left/right:              0.00012120413290622745
H Linf left/right:              0.00018517477161485163
eta-null S/H Linf:              0.0 / 0.0
```

Geschichte `changed`:

```text
M Linf natural/reflected:       0.0010360775104229624
S Linf natural/reflected:       0.00007788319424485712
H Linf natural/reflected:       0.00014362713766647578
S Linf natural/neutral-left:    0.00005403011803092883
H Linf natural/neutral-left:    0.00010171697534493152
S Linf natural/neutral-right:   0.00009648070734653846
H Linf natural/neutral-right:   0.00016021180838584476
S Linf left/right:              0.00010417435107845652
H Linf left/right:              0.00016536546755181042
eta-null S/H Linf:              0.0 / 0.0
```

Alle `19` vorregistrierten Integritaets- und Kausalkontrollen waren `true`.
Der groesste M-Gesamtmassenfehler blieb unter `1e-12`; negative M-Werte oder
S/H-Bereichsverletzungen traten nicht auf.

## Entscheidung

```text
decision: GEOMETRIC_M_CAUSALITY
```

## Technische Interpretation

Die spaetere Wirkung kann nicht allein aus Gesamtmasse, ungeordneter
M-Werteverteilung oder deren globalen Momenten bestimmt sein:

1. Die Spiegelung erhielt jeden M-Wert exakt und veraenderte nur seinen Ort.
2. Trotzdem aenderte sich die spaetere S/H-Fortsetzung unter derselben Probe
   in beiden unabhaengigen Geschichtsfeldern.
3. Bei eta-null verschwand dieser Unterschied in S und H exakt, obwohl die
   M-Zuordnungen verschieden blieben.
4. Zwei geometrisch verschiedene, massenbilanzierte lokale
   Neutralisierungen erzeugten verschiedene spaetere Wirkungen.

Damit ist Evidenzstufe E2 fuer die feste K2/F3-Kandidatenform erfuellt:
M wirkt als geometrisch verteilter kausaler Geschichtstraeger.

## Grenzen und Nichtnachweise

- Die K2/F3-Form ist selbst eine lokale konservative Drift-
  Diffusionsphysik auf dem bestehenden S-Feld.
- E2 schliesst unabhaengige lokale Spuren, Gegenvariablen, Hysterese oder
  lineare gekoppelte Feldmoden noch nicht als Erklaerung aus.
- Nicht nachgewiesen ist verteilte kausale Nichtseparierbarkeit gegen enge
  Baselines.
- Wiederholte Teilnahme, Feldzeitverdichtung, funktionale Loesung und
  Wiederpraegung wurden nicht untersucht.
- Es besteht kein Nachweis von MCM-Memory, Organisation, Topologie, Semantik
  oder KI.

## Ergebnisartefakt

```text
reports/mcm_f3_geometry_lauf_191.json
```

## Bester naechster Schritt

Vor einer Verdichtungs- oder Memory-Interpretation folgt E3: ein fester
Baselinevertrag muss dieselben Geschichten, S/H-Angleichung, M-Budgets,
Geometrieinterventionen und dieselbe Probe gegen enge lokale Leaky-Spuren,
lineare Gegenvariablen und eine lineare gekoppelte Feldform vergleichen.
Nur ein nicht durch diese Klassen erklaerbarer Rest darf als verteilte
kausale Nichtseparierbarkeit offenbleiben.
