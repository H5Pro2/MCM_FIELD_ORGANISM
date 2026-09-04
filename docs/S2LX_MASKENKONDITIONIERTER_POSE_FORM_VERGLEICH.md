# S2-LX: Maskenkonditionierter Pose-/Formvergleich

## Fragestellung

S2-LX prueft, ob die unveraenderte verteilte 96-Werte-Maske aus S2-LW durch
dieselbe Form-/Ortstrennung wie in S2-LV besser nutzbar wird. Beide bestehenden
Korpora, Vergleichsergebnisse und die Maskenbindung sind unveraendert per
Datei- und Inhaltsdigest gebunden.

Die neue Projektionsfunktion erhaelt ausschliesslich 96 `(Position, Wert)`-
Paare. Die 192 verdeckten Werte sind in ihrer Eingabe nicht vorhanden und
werden weder ergaenzt noch mit Nullwerten ersetzt. Teilhinweis und jeder
Vergleichskandidat durchlaufen dieselbe maskenkonditionierte Projektion.

Verglichen werden:

- Top-Row 32;
- verteilt 32;
- verteilt 96;
- voller 288-Werte-Vektor;
- S2-LV-Vollform;
- maskenkonditionierte 96-Werte-Form.

Familienrollen existieren nur im nachgelagerten Leave-one-out-Auswerter. Es
gibt keine Schwellenwahl, Parametersuche, Memory- oder Feldintegration.

## Ergebnis

| Korpus | Voll 288 | Verteilt 96 | Vollform | Maskierte Form 96 |
| --- | ---: | ---: | ---: | ---: |
| S2-LV | `14/32` | `15/32` | `32/32` | `28/32` |
| S2-LW | `18/32` | `17/32` | `30/32` | `26/32` |

Die maskenkonditionierte Form verbessert die rohe 96er-Sicht auf beiden
eingefrorenen Korpora deutlich. Damit enthalten die 96 sichtbaren Werte genug
Geometrie fuer eine brauchbare, posebereinigte Strukturbeschreibung. Die
Vollform bleibt jedoch um vier Faelle je Korpus staerker.

Die Restfehler betreffen vor allem kleine Formen und starke Lageverschiebungen.
Sie sind nicht mehrdeutig im Sinne exakter Zentroidgleichheit, sondern werden
mit kleinen positiven Abstaenden einer anderen Familie zugeordnet. Verdeckte
Information wurde dabei nicht rekonstruiert.

Auch die Formdistanzen ueberlappen weiterhin:

| Korpus | Vollform-Trennrand | Maskierte-Form-Trennrand |
| --- | ---: | ---: |
| S2-LV | `-0.003341` | `-0.007698` |
| S2-LW | `-0.003294` | `-0.007152` |

Eine neue globale Schwelle oder direkte PPB-Anbindung ist daraus nicht
begruendet.

## Technischer Abschluss

- neutrale Qualifikation: `10/10`, Exit-Code `0`, `OK`;
- Vergleich und read-only Verifikation: `RECORDING_COMPLETE`;
- zwei Korpora, 64 Rezeptoranalysen und je 496 vollstaendige Paarbeziehungen;
- historische S2-LV-/S2-LW-Baselines exakt reproduziert;
- Mutation aller 192 verdeckten Werte veraendert die maskierte Form nicht;
- Memory-, Kontext- und Feldaufrufe: `0`.

## Entscheidung

96er-Sichtbarkeit und Formnormalisierung sind gemeinsam tragfaehiger als rohe
maskierte L1-Werte. Der Befund qualifiziert eine private read-only
Vergleichsansicht, aber noch keine Memoryregel. Eine spaetere kontrollierte
Memoryzulassung muss fehlwertbewusste Formevidenz, Pose und Unsicherheit
getrennt binden und darf keine universelle Distanzgrenze aus diesem Korpus
ableiten.

Belege:

- `reports/s2lx/s2lx-masked-pose-form-comparison-20260905-01/comparison.json`
- `reports/s2lx/s2lx-masked-pose-form-comparison-20260905-01/verification.json`
- `reports/s2lx/s2lx-masked-pose-form-qualification-20260905-01/qualification.json`
