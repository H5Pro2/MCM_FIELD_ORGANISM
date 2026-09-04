# S2-LW: Raeumlicher Maskenvergleich

## Umfang

S2-LW vergleicht drei read-only Ansichten derselben unveraenderten 288
visuellen Rezeptorwerte:

1. `TOP_ROW_32`: die bisherige zusammenhaengende Maske `0..31`;
2. `SPATIAL_SEEDED_32`: 32 raeumlich verteilte Werte;
3. `SPATIAL_SEEDED_96`: eine 96-Werte-Kontrolle mit demselben 32er-Praefix.

Die verteilte Reihenfolge entsteht ausschliesslich aus Rasterzeile, Spalte,
Kanal und einem festen SHA-256-Seed. Bildwerte, Familienrollen und Ergebnisse
sind bei der Maskenbildung nicht verfuegbar.

Das neue vorab versiegelte Korpus umfasst vier Drei-Punkt-Anordnungen mit je
acht Varianten fuer Position, Kantenlage, Groesse und Kontrast. Korrespondierende
Varianten besitzen dieselbe Pixelhistogramm- und Helligkeitssumme.

## Abdeckung

| Maske | Werte | Zeilen | Spalten | Kanaele | Zellen |
| --- | ---: | ---: | ---: | ---: | ---: |
| Top-Row | 32 | 1 | 11 | 3 | 11 |
| verteilt | 32 | 8 | 12 | 3 | 27 |
| verteilt | 96 | 8 | 12 | 3 | 62 |

## Ergebnis

| Maske | Exakte Zwischenfamilien-Kollisionen | Eindeutige Maskenvektoren | Leave-one-out | Mehrdeutig |
| --- | ---: | ---: | ---: | ---: |
| `TOP_ROW_32` | `337/384` | `3/32` | `0/32` | `30/32` |
| `SPATIAL_SEEDED_32` | `5/384` | `28/32` | `7/32` | `0/32` |
| `SPATIAL_SEEDED_96` | `0/384` | `32/32` | `17/32` | `0/32` |
| Vollvektor | n/a | n/a | `18/32` | `0/32` |

Die verteilte 32er-Maske beseitigt den groessten Teil der exakten Kollisionen,
traegt aber nicht genug Information fuer eine belastbare Familienzuordnung.
Die 96er-Kontrolle beseitigt exakte Kollisionen vollstaendig, erreicht jedoch
nur die Leistung des rohen Vollvektors und nicht den `32/32`-Befund des
positionsnormalisierten S2-LV-Formdeskriptors.

Die metrischen Beziehungen bestaetigen denselben Befund:

| Maske | Innerhalb `<=0.01` | Zwischen `<=0.01` | Unter `0.2` |
| --- | ---: | ---: | ---: |
| `TOP_ROW_32` | `98/112` | `337/384` | alle |
| `SPATIAL_SEEDED_32` | `24/112` | `74/384` | alle |
| `SPATIAL_SEEDED_96` | `11/112` | `3/384` | alle |

Diese Zaehler sind Diagnosen, keine neue Schwellenwahl.

## Entscheidung

Die feste Top-Row-Maske ist als allgemeiner visueller Teilhinweis ungeeignet.
Eine verteilte 32er-Maske genuegt auf diesem Korpus noch nicht. 96 verteilte
Werte liefern eine kollisionsfreie, aber weiterhin rohe Ortsansicht. Vor einer
Memoryintegration muessen deshalb Formnormalisierung und source-bound
raeumliche Sichtbarkeit gemeinsam geplant werden. Es wurden keine Schwellen,
Rezeptoren, Memorykerne oder Feldfunktionen geaendert.

Technischer Abschluss: `9/9`, Exit-Code `0`, `OK`; Vergleich und unabhaengige
read-only Verifikation: `RECORDING_COMPLETE`.

Belege:

- `reports/s2lw/s2lw-spatial-mask-corpus-20260905-01/presealed-plan.json`
- `reports/s2lw/s2lw-spatial-mask-comparison-20260905-01/comparison.json`
- `reports/s2lw/s2lw-spatial-mask-comparison-20260905-01/verification.json`
- `reports/s2lw/s2lw-spatial-mask-qualification-20260905-01/qualification.json`
