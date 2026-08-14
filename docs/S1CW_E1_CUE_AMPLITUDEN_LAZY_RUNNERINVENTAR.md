# S1-CW: E1 Cue-Amplituden Lazy-Runnerinventar

## Status

Alle 72 S1-CU-Beobachtungsrollen sind als lazy, schreibgeschuetztes und
streng geordnetes Inventar gebunden. Beim Aufbau wurde kein
Amplitudenrunner, Kompositor oder Evaluator aufgerufen.

## Implementierung

```text
mcm_field_organism/e1_cue_amplitude_runner_inventory.py
tests/test_e1_cue_amplitude_runner_inventory.py
```

## Reihenfolge

```text
Modelle:      e1, p0, b1-static-h8
Geschichten:  left-g4, right-g4, neutral
Seiten:       left, right
Amplituden:   0.125, 0.25, 0.5, 1.0
```

Das kartesische Produkt besitzt exakt 72 eindeutige Schluessel. Jeder Wert
ist ein Callable fuer genau einen bereits isoliert abgenommenen Arm.

## Inventardigest

```text
d3a40cbf9e76bffb6ccab1a1a2a3facedef8ad8af7f0f2198bc876e7ef276cd9
```

Gebunden sind S1-CU-Vertragsdigest, alle Schluessel, Feldgeometrie,
G4-Zustaende, Neutralzustand, der eine statische H8-Adapter,
S/H-Zeitparameter und die unveraenderte Runnerfactory.

## Technische Abnahme

Sieben fokussierte Inventartests und 91 relevante Verbundtests bestehen.
Geprueft wurden Vollstaendigkeit, Reihenfolge, Schreibschutz,
Nebenwirkungsfreiheit, Digest, Zeitgrenzen, private API und genau eine
isolierte Identitaetsprobe.

Die Identitaetsprobe ist keine 72er-Matrix. Kompositor und Evaluator wurden
nicht aufgerufen.

## Aussagegrenze

S1-CW bestaetigt nur statische Matrixbereitschaft. Es existiert kein realer
Amplitudenkurvenbefund und daraus folgt keine Aussage zu Nichtlinearitaet,
Mustervervollstaendigung, Rekonstruktion oder Memory.

## Bester naechster Schritt

S1-CX registriert einen atomaren Einmallaufvertrag fuer die 72er-Matrix. Er
bindet Inventardigest, Ergebnisstruktur, Versuchsnachweis, Fehlerverhalten
und Wiederholungsverbot, ohne einen Runner aufzurufen.
