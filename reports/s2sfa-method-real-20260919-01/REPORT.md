# S2-SFA-Methodenversuch 20260919-01: Befund

## Technischer Abschluss

`RECORDING_COMPLETE` — einmaliger gebundener Lauf
`s2sfa-visual-method-20260919-01`.

- 32 Rezeptframes verarbeitet: acht Lernframes, acht Referenzframes und 16
  Prüfframes.
- Alle 32 Quellenquittungen sind `ANALYZED`; jede bindet den Hash des
  tatsächlich erzeugten Frames vor Analyse und den Digest ihrer 288
  Rezeptorwerte.
- Die SFA-Projektion wurde nach `L1` und `L2` einmal eingefroren.
- Der Record wurde einmal veröffentlicht, einmal unabhängig read-only
  verifiziert und anschließend einmal getrennt ausgewertet.
- Kein Rohframe wurde abgelegt.

## Öffentliche Prüffolgen

| Folge | Rohbaseline | SFA | Rohscore passend / andere Referenz | SFA-Score passend / andere Referenz |
|---|---|---|---:|---:|
| `QA → A` | korrekt | korrekt | `0,03650290892026595 / 0,08268926340129208` | `0,06562500000000018 / 1,809375000000001` |
| `QB → B` | korrekt | korrekt | `0,03714191368247954 / 0,08201764373955649` | `0,05937500000000012 / 1,815625000000001` |
| `QAB → A` | korrekt | korrekt | `0,3459704151275997 / 0,3961007245440275` | `0,4031250000000004 / 2,2781250000000015` |

Die getrennte Auswertung ergibt: zusätzliche korrekte Zuordnungen `[]`,
Verluste `[]`, Verwechslungen `[]`, Enthaltungen `[]`.

`QC` bleibt eine offene Diagnose, ohne Zuordnungsurteil. Die Rohscores gegen
`RA/RB` lauten `0,331743515284302 / 0,3336931444704648`; die SFA-Scores
`0,9406250000000006 / 0,9343750000000006`. Daraus wird keine
Unbekanntheits- oder Inhaltsbehauptung abgeleitet.

## Fachliche Einordnung

Die gebundene SFA-Ausführung zeigt **keinen zusätzlichen selektiven
Merkmalsnutzen**: Alle drei öffentlichen Fälle waren bereits im Roharm
korrekt. Der vorab erforderliche mindestens eine zusätzliche korrekte
Zuordnung wurde nicht erreicht. Es gibt zugleich keine Verluste oder
Verwechslungen. Geringere zeitliche Veränderung beziehungsweise der kleine
langsamste Eigenwert (`5,461126342809486e-16`) zählt dafür nicht als Nutzen.

Dieser Befund betrifft nur die gebundenen Farbmusterfolgen und diese lineare
SFA-Projektion. Er trifft keine Aussage über MCM allgemein, biologische
Lernmechanismen, Feld oder Memory.

## Istbilanz

| Artefakt | Byte |
|---|---:|
| `record.json` | 271.179 |
| `verification.json` | 73 |
| `evaluation.json` | 100 |
| **veröffentlichte Laufartefakte** | **271.352** |
| vorab gebundene gemeinsame Obergrenze | 4.932.218 / 8.388.608 |

Die tatsächlich veröffentlichten Artefakte bleiben innerhalb aller gebundenen
Grenzen. Der Lauf ist verbraucht; keine Wiederholung oder Parameteränderung
ist daraus abgeleitet.
