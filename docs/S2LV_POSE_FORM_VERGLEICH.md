# S2-LV: Read-only Pose-/Formvergleich

## Fragestellung

S2-LV prueft, ob sich aus den unveraenderten 288 visuellen Rezeptorwerten zwei
getrennte, label- und zielfreie Ansichten ableiten lassen:

- `POSE_V1`: Aktivitaetsmasse, Schwerpunkt, Ausdehnung und gewichtete Streuung;
- `FORM_DESCRIPTOR_12X12_V1`: positions- und isotrop skalennormalisierte
  raeumliche Aktivitaetsstruktur.

Die Projektion verwendet weder Memoryschwellen noch Familienrollen. Erst der
nachgelagerte Vergleich kennt die vier Formfamilien. Das Korpus umfasst 32
vorab versiegelte RGB8-Frames: vier Anordnungen derselben zwei Quadrate mit je
acht Varianten fuer Position, Kantenlage, Groesse und Kontrast. Korrespondierende
Varianten besitzen dieselbe Pixelhistogramm- und Helligkeitssumme.

## Technischer Abschluss

- neutrale Qualifikation: `10/10`, Exit-Code `0`, `OK`;
- Vergleich: `RECORDING_COMPLETE`;
- vollstaendige Paarmatrix: `112` innerfamiliaere und `384`
  familienuebergreifende Beziehungen;
- Rezeptoraufrufe: `32`; Memory-, Kontext- und Feldaufrufe: `0`;
- keine Schwellenwahl, Produktionsintegration oder Rohdatenablage.

## Vergleich

| Messung | 288-L1 | Formdeskriptor |
| --- | ---: | ---: |
| Leave-one-out, naechster Familienzentroid | `14/32` | `32/32` |
| maximale innerfamiliaere Distanz | `0.037763` | `0.011905` |
| minimale Zwischenfamiliendistanz | `0.008956` | `0.008564` |
| globaler Trennrand | `-0.028808` | `-0.003341` |

Die Form-/Ortstrennung organisiert dieses Korpus deutlich besser als der rohe
288-L1-Vergleich. Die Paarverteilungen ueberlappen aber weiterhin. Der Befund
begruendet daher weder eine universelle Grenze noch eine direkte
Memoryintegration.

Die bestehenden Memorygrenzen wurden nur diagnostisch auf beide Ansichten
angewandt:

| Beziehungen | 288-L1 `<=0.01` | Form `<=0.01` | jeweils `<=0.2` |
| --- | ---: | ---: | ---: |
| innerhalb | `16/112` | `107/112` | alle |
| zwischen | `2/384` | `44/384` | alle |

Die Gradientenbaseline bleibt auf ihrer festen Skalierung fuer alle 496 Paare
unter `0.01` und liefert keinen begruendeten Integrationsvorteil.

## Teilhinweismaske

Die bestehende Maske `0..31` beobachtet weiterhin nur 32 von 288 Werten in
Rasterzeile 0. Auf dem neuen Korpus sind `315/384` Beziehungen zwischen
verschiedenen Formfamilien und `91/112` Beziehungen innerhalb einer Familie
auf diesen Positionen exakt gleich. Die Maske ist damit weder raeumlich
repraesentativ noch fuer diesen Formvergleich ausreichend informativ.

## Entscheidung

`POSE_V1` und `FORM_DESCRIPTOR_12X12_V1` bleiben private read-only
Vergleichsansichten und bilden keine dritte Memoryebene. Vor einer
Memoryintegration muss separat eine source-bound Teilhinweisform mit
raeumlicher Abdeckung untersucht werden. S2-LV aendert weder Rezeptoren,
Memorykerne, Schwellen noch Feldpfad.

Belege:

- `reports/s2lv/s2lv-pose-form-corpus-20260905-01/presealed-plan.json`
- `reports/s2lv/s2lv-pose-form-comparison-20260905-01/comparison.json`
- `reports/s2lv/s2lv-pose-form-comparison-20260905-01/verification.json`
- `reports/s2lv/s2lv-pose-form-qualification-20260905-01/qualification.json`
