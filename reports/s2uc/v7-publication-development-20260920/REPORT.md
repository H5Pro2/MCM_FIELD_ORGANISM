# V7-Publikation und Fehlerabschluss: Entwicklungsabschluss

**117/117 neutrale Tests bestanden, Exitcode 0.** Isolierte Publikationskomponente fertiggestellt. Die echte V7-Startersperre bleibt erhalten. Keine reale Quelle, finale Hauptlaufbindung, Defaultumschaltung, Workflowaenderung oder formale Qualifikation. Die unabhaengige Abnahme bleibt offen.

## Umsetzung

`publish_neutral(record_bytes, binding_path, directory)` verarbeitet bereits erzeugte serialisierte neutrale Verbindungsrecords. Die API nimmt keinen Quellenlieferanten entgegen und startet keine Verbindungsgeschichte. Sie verlangt die synthetische Entwicklungsbindung und verweigert Records mit Quellenabschluss oder Materialisierungsreceipts. Die neutralen Eingaben werden ausschliesslich vor dem Publikationsaufruf in der Testvorbereitung erzeugt.

Recordbytes werden vor dem Schreiben gegen Reserve, absolute Grenze, Staging- und Gesamtbudget geprueft. Publikation: exklusives Anlegen von `publication.tmp`, vollstaendiges Schreiben/Flush/fsync, Bytevergleich, atomare Umbenennung innerhalb desselben Dateisystems und erneuter Bytevergleich. Danach wird der Record neu eingelesen und technisch geprueft. Verifikation und gegebenenfalls Auswertung stehen im eigenen `verification.json`; der Terminal referenziert dessen konkrete Bytezahl und SHA256.

Verifikations- und Auswertungsdaten sind bis zum erfolgreichen Abschluss vorlaeufig. Die Referenzen bleiben fest an die geprueften Recordbytes und die serialisierten Verifikationsbytes gebunden. Eine nachtraegliche Aenderung darf nicht durch Neuberechnung des Hashs legitimiert werden. Die zusaetzliche Gegenprobe dazu ist enthalten; die gefundene und behobene Entwicklungsluecke steht in [development-correction.json](final/development-correction.json).

Vorstartinventar und Ergebnisinventar bleiben getrennt. Die laufende Bilanz misst die unveraenderten Vorstartdateien und alle vorhandenen Ergebnisdateien anhand der festen Vertragsrollen. Unbekannte Dateien werden mit ihrer Groesse als unklassifiziert ausgewiesen und sperren einen gueltigen Abschluss. Reservierungen werden nicht als vorhandene Dateien ausgegeben.

Bei Fehlern bleibt der erste Fehler erhalten; die Ergebnisauswertung wird gesperrt. Bereits publizierte Record-/Verifikations-/Terminaldateien bleiben erhalten und bilanziert. Eine vorhandene Stagingdatei wird vor jedem weiteren Schreibversuch bereinigt oder blockiert weitere Publikation. Restbytes vor Bereinigungsversuchen werden protokolliert. Fehlende dauerhafte Fehler-/Abschlussbelege stehen ausdruecklich in `missing_durable_evidence`. Bestehende Ausgabeordner werden abgewiesen und bleiben unveraendert.

## Dateien und Hashes

| Datei | Byte | SHA256 |
|---|---:|---|
| `tests/test_s2uc_publication_v7.py` | 18798 | `cca38c6818d0099b6a70dc2f6b3ab1db29b15e79448f2e0b5501d39d999462da` |
| `tools/_s2uc_inventory_v7.py` | 8882 | `08b167956c6572024344bf94702142bdcd2cc00ea8a442627792dc92260e8e33` |
| `tools/_s2uc_publication_v7.py` | 13790 | `08595b394a3943e2d417903b1173fd9125efb9a33642c3935eb5a765451ffee4` |

Vorher-/Nachherhashes: [changed-files.json](final/changed-files.json); Ausgangsstand: [before.json](before.json); Endstand: [after.json](final/after.json). Andere erfasste Projektquellen sind unveraendert, einschliesslich Starter, Vorstartvalidator, alter Ledger und bisheriger Testsuiten.

## Testnachweis

| Suite | Tests |
|---|---:|
| `test_s2ub_candidate_confirmation` | 11 |
| `test_s2uc_materialization_connection` | 46 |
| `test_s2uc_neutral_connection` | 11 |
| `test_s2uc_prestart_v7` | 16 |
| `test_s2uc_publication_v7` | 19 |
| `test_s2uc_resource_contract_v7` | 14 |

Alle konkreten Test-IDs, Einzelergebnisse, gebundenen Codehashes und Runnerangaben: [test-result.json](final/test-result.json). Vollstaendige Ausgaben: [tests.stderr.txt](final/tests.stderr.txt), [tests.stdout.txt](final/tests.stdout.txt). Keine Fehler und keine uebersprungenen Tests.

Die neue Suite prueft Erfolg, Recorduebergroesse, Wiedereinlese- und Verifikationsfehler, Aenderungen nach Verifikation/Auswertung, fehlerhafte oder uebergrosse Verifikationspublikation, Schreib-/Umbenennungs-/Bereinigungsfehler, erhaltenen Primaerfehler trotz fehlendem Fehlerbeleg, gleichzeitige Fehler-/Terminal-/Minimalbelege, Stagingreste, veraenderte Vorstartbelege, unbekannte Ergebnisdateien, bestehende Ausgabeordner und den unveraenderten echten Starterstopp.

## Codebudget

**40 Dateien, 654068 / 655360 Byte; Rest 1292 Byte.** Vollstaendige Vereinigung von Starter und sechs gebundenen Testsuiten: [dependency-inventory.json](final/dependency-inventory.json). Neue Komponente und Tests werden voll mitgezaehlt. Keine bestehende Pruefpflicht wurde entfernt oder ausgelagert.

Der restliche Codespielraum ist gering. Externe Installationsbytes und Prozessspeicher sind weiterhin getrennt; die Artefaktbilanz ist keine RAM- oder Gesamtdiskgarantie.

## Gemessene Abschlussbilanzen

Alle Werte sind tatsaechliche Datei-Bytes aus neutralen Tests, keine Hauptlaufergebnisse. Der unveraenderte Vorstartanteil betraegt C=654068, M=26651 und B=94564 Byte, zusammen 775283 Byte. Die folgende Auswahl enthaelt zusaetzlich saemtliche vorhandenen Ergebnisdateien. E/T/Tmin gehoeren zu Shared und werden im Gesamtwert genau einmal gezaehlt.

| Fall / Messung | Record | Verifikation | Fehler | Terminal | Minimal | Staging | Gesamt inkl. C/M/B |
|---|---:|---:|---:|---:|---:|---:|---:|
| [Erfolg](final/closures/028/measurement.json) | 40635 | 2465 | 0 | 796 | 0 | 0 | 819179 |
| [Record vor Publikation zu gross](final/closures/013/measurement.json) | 0 | 0 | 650 | 650 | 0 | 0 | 776583 |
| [Technische Verifikation fehlgeschlagen](final/closures/030/measurement.json) | 40635 | 0 | 763 | 763 | 0 | 0 | 817444 |
| [Fehler nach Verifikationspublikation](final/closures/024/measurement.json) | 40635 | 2465 | 902 | 902 | 0 | 0 | 820187 |
| [Fehler + Terminal + Minimal gleichzeitig](final/closures/019/measurement.json) | 40635 | 2465 | 886 | 796 | 947 | 0 | 821012 |
| [Partielle Schreiboperation, Bereinigung blockiert](final/closures/015/measurement.json) | 0 | 0 | 0 | 0 | 0 | 113 | 775396 |
| [Terminalschreiben und Bereinigung blockiert](final/closures/032/measurement.json) | 40635 | 2465 | 0 | 0 | 0 | 71 | 818454 |
| [Fehlerbeleg fehlt, Primaerfehler erhalten](final/closures/009/measurement.json) | 40635 | 0 | 0 | 808 | 0 | 0 | 816726 |

In den blockierten Bereinigungsfaellen fehlen dauerhafte Fehler- und Abschlussbelege; dies wird nicht als erfolgreicher Abschluss behandelt. Im Fall eines gescheiterten Fehlerbelegs bleibt `error.json` ausdruecklich als fehlend gemeldet, auch wenn ein Fehlerterminal geschrieben wurde. Bei veraendertem Vorstartinventar oder unbekannten Zusatzdateien wird `accounting_complete=false` gemeldet; die bekannten Byteposten sind dann kein vollstaendiger Zulassungsnachweis.

Alle **39 Messungen**: [closure-measurements.json](final/closure-measurements.json). Jede Messung besitzt unter `final/closures/<Nummer>/files/` die unveraendert kopierten Ergebnisbytes und unter `inputs/` die zugehoerigen Nicht-Code-Vorstartdateien. `measurement.json` bindet diese Dateien mit Pfad, Groesse und Hash. Aktive Codequellen sind ueber das vollstaendige Codeinventar gebunden. Die Archivkopien sind Entwicklungsnachweise, keine weiteren aktiven Laufartefakte.

Archivnachpruefung: **547 Dateien** mit erneut gepruefter Groesse und SHA256; alle 39 Gesamtsummen aus den gespeicherten Bytes nachgerechnet. Beleg: [archive-verification.json](final/archive-verification.json). Die Prospektivreservierungen bleiben separat: [prestart-budget.json](final/prestart-budget.json).

## Echter Starter bleibt geschlossen

Beleg: [starter-stop.json](final/starter-stop.json).

```text
V7_EXECUTION_NOT_CONNECTED: V7-Ausführung noch nicht angebunden
Supplier=0; Adapter=0; Laufeinstieg=0
Gate offen=False; USED=False; Ergebnisablage vorhanden=False
```

## Aussagegrenzen und naechster Schritt

Die Komponente setzt genau einen Schreiber in einem neu angelegten Ausgabeordner voraus. Atomare Sichtbarkeit der einzelnen Dateiumbenennung ist keine Zusage einer transaktionalen Mehrdateipublikation oder einer Wiederherstellung nach Stromausfall. Fehlende dauerhafte Belege bleiben bei blockiertem Dateisystem moeglich und werden sichtbar gemeldet. Wissenschaftliche Wahrnehmungs-/Memoryaussagen werden aus den neutralen Publikationstests nicht abgeleitet.

Naechster Vorschlag: unabhaengige Abnahme des V7-Gesamtpfads anhand der archivierten Fehlerabschluesse. Danach die kleinste Starteranbindung mit konkreter Byteplanung festlegen; es bleiben nur 1292 Byte. Die Ausfuehrungssperre und eine gesonderte Entscheidung ueber reale Quellen bleiben bestehen.

Nur die Belege unter `final/` dokumentieren den Endstand. Die uebrigen Dateien dieses neuen Berichtsordners sind Zwischenstaende; die erste gemeinsame Regression wurde nach Entdeckung der Integritaetsluecke bewusst abgebrochen. Historische Berichtsordner wurden nicht geaendert.
