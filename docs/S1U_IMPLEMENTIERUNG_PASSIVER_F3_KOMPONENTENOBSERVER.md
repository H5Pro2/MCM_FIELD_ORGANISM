# S1-U: Implementierung passiver F3-Komponentenobserver

Stand: 2026-08-09

Implementierungsstatus: `SINGLE_CELL_LEDGER_IMPLEMENTED_NOT_CLASSIFIED`

Formaler Forschungslauf: nein

## Ziel

S1-U implementiert den in S1-T vorregistrierten stufengenauen
Komponentenobserver fuer eine einzelne gebundene Zelle. Er bilanziert die
beiden direkten M-Beitraege, ohne Feldzustand, Integrator oder Quelle zu
veraendern.

## Runtimeinstrumentierung

Die F3-Runtime besitzt jetzt einen optionalen privaten Diagnosehook je
SSPRK-Stufe. Er erhaelt:

- das bereits feststehende Integrationsgewicht der Stufe;
- schreibgeschuetzte Kopien von S und M;
- das unveraenderte Kopplungsergebnis.

Der Hook besitzt keinen Rueckgabepfad zum Feld. Ein Rueckgabewert ungleich
`None` wird von der Runtime abgewiesen. Ohne Hook bleibt der bisherige Pfad
unveraendert.

## Komponentenledger

Der neue Adapter
[`s1u_f3_component_observer.py`](../mcm_field_organism/s1u_f3_component_observer.py)
berechnet je Stufe getrennt:

```text
D_i = lambda * sum_j (M_j - M_i)
A_i = -lambda * kappa * sum_j ((M_i + M_j) * (S_j - S_i))
```

Die Beitraege werden mit den exakten SSPRK-Gewichten `1/6`, `1/6` und `2/3`
integriert. Der Ledger gibt vollstaendige Knotenvektoren, M-Anfang und
M-Ende, Bilanzrest, Knotensummen, Stufenzahl, integriertes Gewicht und
Argmax-Knoten aus.

## Gebundene Einzelzelle

Die aktive technische Hauptzelle lautet:

```text
model:          f3
dose_count:     8
source_form:    repeated-supports
delay:          0.200 s
refinement:     4
```

Ihr Ledger ergibt:

```text
SSPRK-Stufen:                         96
integriertes Stufengewicht:           0.2 s
Transport-Linf:                       0.0028248369534719484
Aktivierungsantrieb-Linf:             0.0028452129424663976
tatsaechliches M-Inkrement-Linf:      0.0006167263531163397
Bilanzrest-Linf:                      9.75578667329613e-17
Argmax-Knoten Anfang/Ende:            auditory.n0 / auditory.n0
Observer-Enddigest bitgleich:         ja
```

Transport und Aktivierungsantrieb sind in dieser Zelle einzeln deutlich
groesser als ihr verbleibendes Gesamtinkrement und wirken weitgehend
gegeneinander. Dies ist eine technische Komponentenbilanz, noch keine
Ursachenentscheidung fuer die vier S1-T-Kurven.

## Kontrollen

| Kontrolle | Ergebnis |
|---|---|
| Enddigest mit/ohne Observer | bitgleich |
| Ledgerabschluss | innerhalb `1e-12` |
| Knotensumme Transport | innerhalb `1e-12` bei null |
| Knotensumme Aktivierungsantrieb | innerhalb `1e-12` bei null |
| P0-Komponenten | exakt null |
| aktive uniforme S/M-Null | exakt null |
| 2/4-Komponentendifferenzen | endlich, lokale Boeden bildbar |
| Runtime-/AV-/S1-R-Kompatibilitaet | bestanden |

## Testergebnis

Der fokussierte S1-U-Verbund besteht mit:

```text
4 passed
4 subtests passed
3.67 s
```

Der direkte Runtime-, S1-J-, S1-R- und S1-U-Verbund besteht mit:

```text
25 passed
39 subtests passed
28.65 s
```

Die bekannte Pytest-Cachewarnung `WinError 183` betrifft ausschliesslich den
lokalen Cachepfad.

## Aussagegrenze

S1-U hat weder die vier Kurven komponiert noch `kappa=0`, `eta=0` oder die
lineare Komponentenentscheidung ausgefuehrt. Die Einzelzelle belegt keine
allgemeine Ursache der spaeten M-Mischung.

Der Ledger ist kein Memory, kein Lernen, keine Feldzeit und keine
Selbstregulation. Er belegt keine Semantik, Organisation, Topologie oder KI.
Es gab keinen Browserstart, keine reale Sensorik, keinen externen Runner,
keinen Report und keine neue Laufnummer. Lauf 197 bleibt unberuehrt.

## Bester naechster Schritt

S1-V implementiert den begrenzten Vierkurven-Ledgeradapter mit den bereits
vorregistrierten F3-, linearen, `kappa=0`- und `eta=0`-Armen. Zunaechst
werden Armidentitaet, Komponentenbilanz, 2/4-Boeden und Endzustands-
transparenz zellweise getestet. Die drei S1-T-Entscheidungsrollen werden in
S1-V noch nicht berechnet.

## Spaeterer Umsetzungsstand S1-V

S1-V hat den zellweisen Vierarmadapter inzwischen umgesetzt. Fruehe
kumulative Ledger und spaete geschachtelte Intervallledger bleiben getrennt;
F3, linear, `kappa=0` und `eta=0` bestehen mit Bilanz-, Transparenz- und
2/4-Kontrollen. Eine Vollklassifikation steht aus.
