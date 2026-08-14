# S1-CJ: E1 E4 E1-, B0-, B1-Runner und S1-CD-Kontinuitaet

## Status

E1, die exakte P0-Baseline B0 und der einzige statische H8-Gain B1 sind an
den gemeinsamen E4-Checkpoint- und Probevertrag gebunden und isoliert
technisch abgenommen.

Der S1-CD-Einmallauf und seine Tests wurden nicht erneut ausgefuehrt. Der
neue E4-E1-Runner bildet seine eigenen H8-, G1/G4/G8- und C1-C8-Zustaende
und prueft daraus die gespeicherten S1-CD-Kontinuitaetsanker.

Es wurde keine E4-Gesamtmatrix komponiert und keine Baselineentscheidung
erzeugt.

## Implementierung

```text
mcm_field_organism/e1_e4_e1_runners.py
tests/test_e1_e4_e1_runners.py
```

Die bestehende E3-Zustandsimplementierung wurde minimal erweitert:

```text
produce_e1_competing_checkpoints(...)
```

Sie gibt die acht bereits berechneten C-Zwischenstaende aus. Der vorhandene
E3-Endpfad verwendet nun dieselbe Funktion und behaelt exakt denselben C8-
Endzustand. Es wurde keine E1-Gleichung veraendert.

## E1-Runner

Der Runner verwendet ausschliesslich bestehende Bausteine:

```text
H8       produce_e1_mirrored_histories
G1/G4/G8 produce_e1_uniform_release_checkpoints
C1-C8    produce_e1_competing_checkpoints ab G4
Probe    advance_frozen_e1_probe und fester E1-Adapter
```

An jedem Checkpoint werden aktive E1-Probe, exakte Ablation, Fixed-Gain-
Kontrolle sowie n=2/n=4 erzeugt. Das primaere Profil verwendet n=4 und
enthaelt 72 signierte S/H-Komponenten.

## B0 und B1

B0 ist das exakte P0-Profil und besitzt an allen 72 Komponenten den Wert
null.

B1 verwendet genau den am E1-H8-Zustand gebildeten festen Kantenratenadapter.
Dieser eine Adapter wird unveraendert an allen zwoelf Checkpointidentitaeten
verwendet. B1 kann daher einen einzelnen H8-Gain darstellen, aber keine
autonome Geschichte, Freigabe oder Konkurrenz entwickeln.

## S1-CD-Kontinuitaet

Aus dem neuen E1-Profil werden an H8, G4 und C8 erneut die zehn
Probewirkungsmetriken gebildet. Dazu kommen die vorhandenen Zustandsmetriken:

```text
release_analytic_linf
resource_budget_linf
release_total_binding_drop
compete_total_binding_rebound
maximum_refinement_linf fuer H8/G4/C8
```

Namen und Reihenfolge aller 15 Anker stimmen mit dem S1-CG-Vertrag ueberein.
Jeder neu berechnete Wert liegt innerhalb der vorregistrierten absoluten
Toleranz `1e-12` zum gespeicherten S1-CD-Wert.

Dies ist eine Kontinuitaetspruefung des neuen Runners, keine Wiederholung der
S1-CD-Entscheidung.

## Technische Abnahme

Fokussiert:

```text
python -m unittest -v tests.test_e1_e4_e1_runners

9 tests
OK
```

Gemeinsam mit E1-Historie, E3-Zustandsarmen, Frozen-Probe, gekoppeltem
E1-Feld, S1-CH, S1-CF und den B3-B6-Runnern, jedoch ohne S1-BZ und S1-CD:

```text
75 tests
OK
```

Geprueft wurden:

- vollstaendige Checkpoint- und Profilordnung;
- messbares, checkpointvariables E1-Profil;
- exaktes B0-Nullprofil;
- checkpointkonstanter einziger B1-H8-Gain;
- Ablation, Fixed Gain, Ressourcenbilanz und n=2/n=4;
- alle 15 S1-CD-Kontinuitaetsanker;
- identischer bestehender C8-Endzustand;
- unveraenderte Eingaben und private API-Grenze.

## Aussagegrenze

S1-CJ vergleicht E1 noch nicht mit B1 oder einer anderen Baseline innerhalb
einer E4-Gesamtentscheidung. Die technische Kontinuitaet ist kein Nachweis
fuer Memory, Lernen, Organisation, Semantik oder KI.

## Anschluss

S1-CK bindet den konkreten S2-B2-Runner samt B1-Rueckwirkungsintervention und
Frozen-L-Probe. ORACLE-G reproduziert das Fixed-Gain-validierte E1-Profil
exakt. Eine E4-Gesamtmatrix wurde nicht erzeugt.

## Bester naechster Schritt

S1-CL prueft das vollstaendige Runnerinventar ausschliesslich statisch und
ohne Aufruf von Komposition oder Entscheidung. S1-CM bindet als naechstes
den Einmallaufvertrag, weiterhin ohne Ausfuehrung.
