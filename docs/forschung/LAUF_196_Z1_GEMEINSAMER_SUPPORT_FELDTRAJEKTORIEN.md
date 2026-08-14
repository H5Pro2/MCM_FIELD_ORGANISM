# Lauf 196: Z1-Feldtrajektorien mit gemeinsamem Observer-Support

Stand: 2026-08-06

## Ergebnis

```text
TECHNICAL_PARTITION_INVARIANT
WORLD_TIME_BOUND_FIELD_PATH
ORDER_SENSITIVE_FIELD_PATH
```

Lauf 196 wurde genau einmal ueber den korrigierten one-shot Einstieg
ausgefuehrt. Die einzige Aenderung gegen Lauf 195 war der vorab gebundene
gemeinsame Observer-Support aus neutralem Start und echten
Rezeptorabschlussgruppen.

## Artefakt

```text
reports/mcm_f3_z1_lauf_196.json
schema:        mcm.f3.z1.run196.v1
run_id:        lauf-196
correction_id: mcm.f3.z1.completion-support.v1
SHA256:        DC23B79DC68955EFD92DB918E2BCE23E2E3773CBFA9CDA0D6DEEA0D22B5E76A8
```

Das Artefakt enthaelt Supportzaehlungen, Kontrollen und skalare
Auswertungswerte, aber keine vollstaendigen S/H/M-Trajektorien.

## Bestandene Kontrollen

Alle technischen Matrixkontrollen bestanden:

```text
source_contracts_hold
handoffs_complete
reproductions_exact
mass_and_value_invariants_hold
refinement_final_error_decreased
```

Auch alle Korrekturkontrollen bestanden:

```text
source_contracts_match
all_required_ticks_present
reference_partition_support_equal
nonpartition_support_unchanged
partition_empty_support_removed
```

`A.reference` behielt 92 Voll- und Entscheidungssamples.
`A.partitioned` behielt 183 Vollsamples fuer Diagnose und Reproduktion, gab
aber dieselben 92 Entscheidungssamples wie die Referenz an die Sachmetrik.
Alle anderen Arme blieben mit je 92 Samples unveraendert.

## Technische Teilungsinvarianz

Nach der gebundenen Supportkorrektur lagen die Partitionsdistanzen klar
innerhalb der numerischen Huellen:

| Modell | S-Distanz | S-Huelle | H-Distanz | H-Huelle | M-Distanz | M-Huelle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F3 | 2,0122e-8 | 6,5220e-7 | 2,6122e-8 | 8,4517e-7 | 1,2400e-7 | 4,0360e-6 |
| B3 | 2,0146e-8 | 6,5296e-7 | 2,6085e-8 | 8,4396e-7 | 1,2849e-7 | 4,1823e-6 |

Der Messkonflikt aus Lauf 195 ist damit technisch aufgeloest. Die vorhandene
Runtime ist im untersuchten Korridor robust gegen die reine Halbierung ihrer
Vorschlagsschritte.

## Weltzeitbindung

Zeitdehnung und Zeitkompression veraenderten die geometrischen Zustandsbahnen
weit oberhalb der festen 5-Prozent-Grenze:

| Modell | Arm | S | H | M |
| --- | --- | ---: | ---: | ---: |
| F3 | gedehnt | 0,4343 | 0,7014 | 0,5774 |
| F3 | komprimiert | 0,3564 | 0,5647 | 0,4796 |
| B3 | gedehnt | 0,4343 | 0,7013 | 0,5502 |
| B3 | komprimiert | 0,3564 | 0,5647 | 0,4732 |

Die bestehende S/H/M-Runtime traegt daher keine
Zeit-Reparametrisierungskovarianz. Ihre Bahn ist an die reale Dauer der
Weltanregung und die in Sekunden definierten Dynamikraten gebunden.

## Ordnungssensitivitaet

Umkehrung, Blockpermutation und unabhaengige Quelle ueberschritten in beiden
Mechaniken die vorregistrierte Ordnungsgrenze deutlich. Die Runtime traegt
damit kausale Verlaufs- und Reihenfolgenabhaengigkeit.

Dieser Befund ist keine relative Feldzeit. B3 zeigt dieselbe Klassifikation,
sodass die Eigenschaft bereits von einer engen linearen gekoppelten
Felddynamik getragen wird.

## B3-Einordnung

F3 und B3 erhielten dieselben drei Klassifikationen. Sechs von sieben
vollstaendigen 4n-Pfaden lagen innerhalb der festen 5-Prozent-Grenze. Nur der
gedehnte M-Pfad lag mit `0,05291931` knapp darueber. Deshalb lautet
`baseline_explains_f3` formal `false`.

Der Rest von 0,2919 Prozentpunkten oberhalb der Grenze ist nur ein offener
enger Residualbefund. Er wird weder durch Grenzlockerung beseitigt noch als
Feldzeit, Organisation oder neue Physik interpretiert.

## Forschungsentscheidung

Z1 ist fuer die bestehende Runtime abgeschlossen:

- technische Teilungsrobustheit ist gezeigt;
- Weltzeitbindung ist gezeigt;
- kausale Ordnungssensitivitaet ist gezeigt;
- Zeit-Reparametrisierungskovarianz ist nicht vorhanden;
- relative Feldzeit ist nicht nachgewiesen;
- F3 besitzt in Z1 keinen belastbaren funktionalen Abstand zur
  Klassifikation der linearen B3-Baseline.

F3 oder B3 werden nicht durch veraenderte Zeitkonstanten, laengere Quellen
oder gelockerte 5-Prozent-Grenzen auf Zeitkovarianz optimiert.

## Aussagegrenze

Nicht nachgewiesen sind relative Feldzeit, observerfreie innere Zeitbildung,
kausale Rueckwirkung eines Zeitkontexts, Memory, Feldzeitverdichtung, innerer
Kontext, Organisation, Topologie, Semantik, Selbstregulation oder KI.

## Bester naechster Schritt

Z2 statisch auditieren: Kann eine lokale ereignisgetragene
Entwicklungsordnung physikalisch begruendet werden, die weder Weltsekunden
noch Ereigniszaehler oder globale Pfadlaenge als Organismusvariable verwendet
und nicht auf eine vorprogrammierte Hysteresekurve zurueckfaellt? Vor diesem
Audit keine neue Zeitvariable und keine neue Runtime.
