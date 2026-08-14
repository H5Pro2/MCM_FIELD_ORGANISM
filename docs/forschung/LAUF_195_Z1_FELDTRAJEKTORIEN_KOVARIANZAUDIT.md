# Lauf 195: Z1-Feldtrajektorien-Kovarianzaudit

Stand: 2026-08-06

## Ergebnis

```text
TECHNICALLY_UNDECIDABLE
```

Lauf 195 wurde genau einmal ueber den vorregistrierten one-shot Einstieg
ausgefuehrt. Das Ergebnis wird nicht als Befund zu Zeitkovarianz,
Weltzeitbindung oder Ordnungssensitivitaet verwendet.

## Artefakt

```text
reports/mcm_f3_z1_lauf_195.json
schema: mcm.f3.z1.run.v1
run_id: lauf-195
SHA256: F18346A9FC965F0E10C6672B3357DBE071433EA64A341DF12EA94BED8A8F3F73
```

Das Artefakt enthaelt nur skalare Distanzen, Huellen, Kontrollen und
Klassifikationen. Vollstaendige S/H/M-Trajektorien wurden nicht persistiert.

## Technische Kontrollen

Alle vorregistrierten Paketkontrollen bestanden:

```text
source_contracts_hold:                 true
handoffs_complete:                     true
reproductions_exact:                   true
mass_and_value_invariants_hold:        true
refinement_final_error_decreased:      true
```

## Ausschlaggebender Teilungsbefund

Beide Mechaniken verletzten die vorregistrierte technische
Teilungsinvarianz deutlich:

| Modell | S-Distanz | S-Huelle | H-Distanz | H-Huelle | M-Distanz | M-Huelle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F3 | 0,01718799 | 6,5220e-7 | 6,9858e-5 | 8,4517e-7 | 1,5544e-4 | 4,0360e-6 |
| B3 | 0,01718792 | 6,5296e-7 | 6,9844e-5 | 8,4396e-7 | 1,6510e-4 | 4,1823e-6 |

Damit greift fuer beide Modelle die vorregistrierte Stopplinie. Die
Klassifikation lautet jeweils ausschliesslich
`TECHNICALLY_UNDECIDABLE`.

## Nicht freigegebene Rohklassifikationen

Die Auswertung berechnete unterhalb der Stopplinie fuer beide Modelle:

```text
time_reparameterization_covariant: false
order_sensitive_field_path:        true
```

Diese Werte sind keine Forschungsentscheidungen. Sie duerfen weder als
Weltzeitbindung noch als Ordnungssensitivitaet des MCM-Feldes berichtet
werden, weil die technische Teilungsnullkontrolle zuvor scheiterte.

## B3-Vergleich

`baseline_explains_f3` ist `false`. Sechs der sieben Arme lagen innerhalb der
5-Prozent-Grenze. Nur `A.stretched` ueberschritt sie in M mit
`0,05291931`; S und H blieben dort mit rund `4,09e-5` beziehungsweise
`3,62e-5` sehr klein.

Auch dieser Rest wird nicht als F3-Neuheit interpretiert. Die vorgelagerte
Teilungsstopplinie macht den gesamten Z1-Sachvergleich unentscheidbar.

## Methodische Ursache

Der Referenzarm besitzt 91 technische Vorschlagsschritte und entsprechend
Observerpunkte an den Rezeptorabschluessen. `A.partitioned` besitzt 182
Vorschlagsschritte und fuegt zwischen denselben Rezeptorabschluessen je einen
weiteren leeren Integrationsabschluss ein.

Die vorregistrierte polygonale Pfadmetrik verwendete alle Observerpunkte.
Damit veraenderte die technische Teilungsintervention gleichzeitig:

1. die Integrationsgrenzen und
2. die Stuetzpunktdichte der observerseitig rekonstruierten Polygonbahn.

Lauf 195 kann deshalb nicht trennen, ob die gemessene Pfaddistanz aus der
Felddynamik oder aus der unterschiedlichen Polygonabtastung stammt. Das ist
ein Messkonflikt, kein negativer oder positiver Feldzeitbefund.

## Aussagegrenze

Nicht nachgewiesen sind technische Teilungsinvarianz,
Zeit-Reparametrisierungskovarianz, Weltzeitbindung, Ordnungssensitivitaet,
relative Feldzeit, Memory, Feldzeitverdichtung, innerer Kontext,
Organisation, Topologie, Semantik, Selbstregulation oder KI.

## Bester naechster Schritt

Vor Lauf 196 eine einzige Messkorrektur binden: Vollstaendige technische
Observerpunkte bleiben fuer Diagnose und Reproduktion erhalten, aber die
Sachpfadmetrik erhaelt in jedem Arm nur den neutralen Start und die echten
Rezeptorabschlusszeitpunkte. Quellen, Feldmechaniken, Integrator,
Refinements, Schwellen und Entscheidungslogik bleiben unveraendert.
