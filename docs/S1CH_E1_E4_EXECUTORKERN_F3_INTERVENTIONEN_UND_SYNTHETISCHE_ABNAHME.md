# S1-CH: E1 E4-Executorkern, F3-Interventionen und synthetische Abnahme

## Status

Der private E4-Executorkern aus S1-CG ist implementiert und synthetisch
abgenommen. Es wurde kein realer E4-Modelllauf ausgefuehrt, keine
S1-BZ- oder S1-CD-Einmalausfuehrung wiederholt und keine E4-Entscheidung fuer
das Projekt erzeugt.

## Implementierung

```text
mcm_field_organism/e1_e4_execution.py
tests/test_e1_e4_execution.py
```

Alle neuen Rollen bleiben privat und sind weder im Paketwurzelexport noch in
`current_api` enthalten.

## F3-Interventionswrapper

`without_e1_e4_f3_backreaction(...)` wertet den jeweils vorhandenen
Kopplungsrechner unveraendert aus. Seine `mass_rate` bleibt erhalten; nur die
ausgegebene `activation_backreaction` wird fuer Phase C auf exakt null
gesetzt.

`build_frozen_e1_e4_f3_reader(...)` bindet einen festen M-Zustand an die
Probe. Der vorhandene Kopplungsrechner berechnet daraus weiterhin die
Rueckwirkung auf das aktuelle S. Die ausgegebene `mass_rate` wird auf exakt
null gesetzt, sodass M waehrend der Probe fest bleibt. Eine abweichende
Knoten- oder Kantengeometrie wird abgelehnt.

Beide Wrapper veraendern keine F3-, local-leaky-, linear-coupled- oder
CONST-V-Gleichung.

## Ergebnisrollen

Genau die drei in S1-CG registrierten Rohdatenrollen sind implementiert:

```text
E1E4ModelRun
E1E4BaselineMeasurement
E1E4RunResult
```

`E1E4ModelRun` bindet Modell- und Parameteridentitaet, das geordnete
72-Komponenten-Profil, Kontrollflags, Refinementrest und eigene
Ressourcenmetriken.

`E1E4BaselineMeasurement` bindet fuer B1 bis B6 den bereits vorhandenen
Profilabstand und die technische Entscheidungszulaessigkeit.

`E1E4RunResult` erzwingt die Reihenfolge E1, B0 bis B6 und ORACLE-G, die sechs
Entscheidungsbaselines sowie alle S1-CD-Kontinuitaetsanker. Der Container
enthaelt keine eingebettete Entscheidung und keine Memoryrolle.

## Executorkern

`preflight_e1_e4_runners(...)` akzeptiert nur ein vollstaendiges Inventar
ohne fehlende oder zusaetzliche Modelle und fuehrt dabei keinen Runner aus.

`compose_e1_e4_run_result(...)` ruft ein zuvor geprueftes, injiziertes
Runnerinventar in fester Reihenfolge auf, bildet die sechs Profilabstaende
und materialisiert den interpretationsfreien Ergebniscontainer.

`evaluate_e1_e4_run(...)` verwendet ausschliesslich die vorregistrierte
Reihenfolge:

```text
INVALID_E4_RUN
TECHNICALLY_INCOMPATIBLE_BASELINE_SET
E4_EXPLAINED_BY_NARROW_BASELINE
E4_RESIDUAL_AFTER_REGISTERED_BASELINES
```

P0 muss exakt null bleiben, ORACLE-G muss E1 bis `1e-12` reproduzieren,
Refinement muss innerhalb `0.01` liegen und eine erklaerende Baseline muss
den relativen Profilrest `0.05` erreichen.

## Synthetische Abnahme

Die neue Suite verwendet ausschliesslich kuenstliche Profile und injizierte
Testfunktionen. Sie fuehrt keinen Forschungsrunner aus.

```text
python -m unittest -v tests.test_e1_e4_execution

13 tests
OK
```

Gemeinsam mit Profil/Handoffs und den bestehenden F3-Kopplungs-, Baseline-
und Runtimevertraegen:

```text
48 tests
OK
```

Geprueft wurden unter anderem:

- festes Runnerinventar und Vertragsdigest;
- unveraenderte Zustandsrate bei ausgeschalteter Rueckwirkung;
- feste M-Lage bei erhaltener Rueckwirkung in der Probe;
- Geometrieablehnung;
- vollstaendige Profil- und Baselineordnung;
- vollstaendige S1-CD-Ankerliste;
- alle vier Entscheidungswege und ihre Reihenfolge;
- private API-Grenze und claimfreie Ergebnisrollen.

## Aussagegrenze

S1-CH bestaetigt nur die technische Kompositions- und Kontrolllogik. Die
konkreten E1-, B0-, B1-, S2-, F3- und CONST-V-Modellrunner sind noch nicht an
den Executorkern gebunden. Es existiert daher weiterhin kein E4-Ergebnis und
kein Memory-, Lern-, Organisations-, Semantik- oder KI-Befund.

## Anschluss

S1-CI bindet B3 bis B6 an die gemeinsame H/G/C-Welt und die identische
Probe. Alle vier F3-Familienrunner bestehen isoliert; eine E4-Matrix oder
Entscheidung wurde nicht erzeugt.

## Bester naechster Schritt

S1-CJ bindet E1, B0 und B1 an denselben Profilvertrag und bestaetigt alle 15
S1-CD-Kontinuitaetsanker. S1-CK schliesst als naechstes S2-B2 und ORACLE-G
an, weiterhin ohne E4-Gesamtmatrix.
