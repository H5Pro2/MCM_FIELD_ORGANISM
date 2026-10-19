# S2-SP: PPB-Lebenszyklus V2 – Einmallauf

Lauf-ID: `s2sp-ppb-lifecycle-v2-20260919-01`  
Technischer Status: `RECORDING_COMPLETE`  
Read-only-Verifikation: `VERIFIED`

Der einmalig gebundene Zweiarmvergleich lief vollständig mit der vorab
versiegelten OA-Quellenfolge. Die vorherige Runnerdeckung besteht aus den
drei Kontrollen der Qualifikation `...-03` und der nativen Feldkontrolle
`...-04`; die vollständige Bindung steht im benachbarten
`-binding`-Verzeichnis.

## Technischer Abschluss

| Umfang | Ist |
|---|---:|
| Ereignisse je Arm | 20 |
| Formationen je Arm | 18 |
| read-only Hinweise je Arm | 2 |
| gemeinsam materialisierte Payloads | 38 |
| Audioanalysen / NJ-Projektionen | 18 / 18 |
| visuelle Analysen | 20 |
| Cue-Scans einschließlich Direktbaselines | 4 |
| Feldkontakte | 0 |

Die einmalige unabhängige read-only Hüllenprüfung bestätigte
`RECORDING_COMPLETE`, Recorddigest, alle Übergangsbelegdigestwerte,
Cue-Zustandsinvarianz, Zähler und beide Armformen. Sie führte keine
Quellen-, Rezeptor-, NJ-, Memory- oder Feldoperation aus.

| Ergebnisdatei | Byte |
|---|---:|
| `record.json` | 56.016 |
| `verification.json` | 121 |
| `evaluation.json` | 553 |
| Gesamt | 56.690 / 262.144 |

Recorddigest: `3deedc2772ede2321898c01a098d90c5b1bf44127c8ed5de7a552fdee2a8cd27`.

## Getrennte Funktionsauswertung

Beide Arme (`historical.v1`, `identity-preserving.v1`) weisen dieselben
gebundenen Einzelbefunde auf:

- Bis Formation 4 entsteht und stabilisiert sich der visuelle PPB-Slot
  `...slot.000`; seine Readouts lauten `CREATED`, danach `MATCHED` und
  `MATCHED`.
- Vor Hinweis 14 enthalten die gespeicherten Cue- und Baselinescans keine
  **passenden** B4- oder Fast-Kandidaten. Der Hinweis findet die gebundene
  visuelle Slow-Generation `...slot.000`; die Auswertung markiert ihre
  eigene Bedingung als `READY`.
- Ereignis 19, die siebzehnte Formation der Folge, erzeugt für denselben Slot
  einen nativen
  `visual_ppb_readout.event = REPLACED`.
- Hinweis 20 ist read-only und hat keine **passenden** B4-, Fast- oder
  visuellen Slow-Kandidaten. Die Auswertung markiert die Ersetzungsbedingung
  als `READY`.

## Nachweisgrenze

Die leeren Listen `B4: []` und `FAST: []` sind Trefferlisten, keine
Inventarlisten. Der Direktvergleich filtert vorhandene Einträge auf Gleichheit
mit den 32 sichtbaren Cuepositionen ([Runner, Zeilen 81–84](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2sp_ppb_lifecycle_v2_runner.py:81)).
Aus ihnen folgt daher weder eine leere Bank noch eine Entfernung der
ursprünglichen A-Bindung.

Der Record hält für Fast nur Slot-ID, Primärereignis und gesättigten Support
fest. `fast_generation` ist ausdrücklich `None` mit
`NOT_AVAILABLE_IN_NATIVE_SLOT` ([Übergangsbeleg, Zeilen 213–231](/C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2sp_private_memory_compare.py:213)).
Er enthält keine vollständigen B4-/Fast-Inventare oder eine fortlaufende
A-Generation. Die A-Entfernung vor Hinweis 14 ist deshalb **nicht belegt**.

Belegt sind die visuelle PPB-Kette, ihr späterer nativer Ersatz und das Fehlen
passender Kandidaten für die zwei gebundenen Hinweise. Der Record führt keine
öffentliche A/B-Auflösung oder Hypothesenanwendung aus; die gespeicherten
`observed`-Werte sind bankspezifische Scanbefunde, keine öffentliche
Cueentscheidung.

Die zwei Arme zeigen in diesem Lauf keine unterschiedliche bankspezifische
Scanbeobachtung. V2 belegt damit keinen Zusatznutzen der neuen Aktualisierung
auf dieser Folge. Der frühere unmittelbare Schutz vor Rundungsdrift bleibt ein
getrennter Einzelbefund; die Randvarianten-Fehlzuordnung bleibt offen. Quellen,
Regeln, Schwellen, Memorykerne und historische Befunde wurden nicht geändert;
das Gate wurde nach dem Lauf zurückgesetzt.
