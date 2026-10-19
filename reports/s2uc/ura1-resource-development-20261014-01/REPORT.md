# URA1: begrenzte neutrale Ressourcenqualifikation

Stand 2026-10-14. Ergebnisübergabe MCM-KI-Entwickler an MCM KI Projektleiter.
Bezug: beauftragte offene Ressourcenqualifikation nach neutraler URA1-Entwicklung und Archivcodec; ursprüngliches Prüfpaket dda37469-3a5d-4448-abcc-45f05509760e.

**PASS_SMALL_RESOURCE_QUALIFICATION. Keine Forschungsbereitschaft.** Die beiden vorhandenen kleinen Handfolgen wurden gezielt für die fehlenden Ressourcenbelege erneut ausgeführt. U/R-Kernregeln, ursprüngliche Archive und Bindungen bleiben unverändert. Keine Forschungsquelle, Bootstrapmatrix oder Forschungsausführung; kein Größenablauf.

## Geänderte und ergänzte Dateien

- [tools/_s2uc_ura1_stream_archive.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_stream_archive.py): Fortlaufende Recordablage, begrenzte temporäre Dateien, inkrementeller referenzierender Encoder und Dateiausgabe.
- [tools/_s2uc_ura1_resource_neutral.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_resource_neutral.py): Neue Ressourcen-Prüfhülle: identische fachliche Prüfschritte, vier Listen durch dateigestützte Folgen ersetzt.
- [tools/s2uc_ura1_resource_qualify.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/s2uc_ura1_resource_qualify.py): Supervisor/Worker, harter gemeinsamer Windows-Job, Phasen- und Prozessmessung sowie Fehlerfälle.
- [tests/test_s2uc_ura1_resource_stream.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tests/test_s2uc_ura1_resource_stream.py): Drei fokussierte Kontrollen für Verlustfreiheit, Grenzen, Cleanup und unveränderte Prüflogik.
- [docs/S2UC_URA1_NEUTRALER_GROESSENABLAUF_VORSCHLAG_20261014.md](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/docs/S2UC_URA1_NEUTRALER_GROESSENABLAUF_VORSCHLAG_20261014.md): Konkreter Vorschlag für genau einen späteren, noch nicht ausgeführten Größenablauf.

Der bestehende unabhängige Decoder bleibt unverändert. Die neue Prüfhülle wurde gegen die vollständige ursprüngliche Quelldatei verglichen: außer Docstring, Import und Ersetzung der vier Listen events/internal/forecasts/rows bestehen keine Änderungen. Es wurde kein Prüfereignis gekürzt.

## Befund und Korrektur der Historienhaltung

Die bisherige Prüfhülle hielt vollständige redundante Ereignislisten im RAM. Das nachträgliche Kompaktieren beseitigte diesen Peak nicht. Die neue Hülle serialisiert jeden Record beim append unmittelbar in eine temporäre JSONL-Datei. Iteration liest jeweils einen Record; gepaarter Vergleich benötigt die aktuellen beiden Records. Es gibt keine Liste vollständiger Ereigniszustände im Spoolobjekt.

Grenzen: höchstens 262.144 serialisierte Byte je Record und 67.108.864 Byte Spooldaten je Fall. Die tatsächlichen größten Records sind unten ausgewiesen. Python-Zustand und Serialisierung eines einzelnen Records existieren kurzzeitig gemeinsam; die Bytegrenze ist deshalb keine Behauptung über dessen vollständigen Python-Heap. Die harte Prozessgrenze umfasst diese Kopien. Dateipuffer, Referenzen, Beobachter und Codec bleiben im gleichen Prozessbudget.

Nach Abschluss der Erfassung iteriert der Encoder die Dateien, bildet einen kanonischen Quellhash und kodiert Teilbäume in das bestehende DAG-Format. Er hält den begrenzten Knotengraphen und Referenzarrays, keine expandierte Historie. Die dekomprimierte Darstellung bleibt auf 4 MiB begrenzt, gzip auf 512 KiB. Ausgabe erfolgt über eine temporäre Datei, die nur bei erfolgreichem Abschluss veröffentlicht wird; partielle Dateien werden im finally entfernt.

## Windows-Prozessnachweise und Laufzeiten

Jeder der vier folgenden Szenarien läuft in einem eigenen Windows-Job mit genau einem Supervisor und höchstens einem geerbten Worker, ohne Breakaway. Der Supervisor verifiziert die Mitgliedschaft des konkreten Workerhandles im eigenen Job, bevor er dessen Arbeit freigibt. JOB_OBJECT_LIMIT_JOB_MEMORY bleibt 536.870.912 Byte; zusätzlich begrenzt ActiveProcessLimit die Zahl auf zwei. Es liefen keine Worker parallel.

Windows JobObjectExtendedLimitInformation liefert den gemeinsamen Commit-Peak; GetProcessMemoryInfo liefert Private Bytes und Prozess-Lebenszeitspitzen. Der Supervisor tastet etwa alle 10 ms ab. Worker-Phasen protokollieren Anfang/Ende, Zeit und tracemalloc-Peak. Phasenwerte des Python-Tracers sind absolute seit Tracerstart lebende Allokationen mit pro Phase zurückgesetzter Peakmarke, keine isolierten Nettoallokationen.

| Test-ID / Szenario | Supervisor-Grundbelegung | Gemeinsamer gesampelter Peak | Kernel-Job-Peak | Sekunden | Ergebnis |
| --- | ---: | ---: | ---: | ---: | --- |
| R01 / normal | 11120640 | 71057408 | 75165696 | 212.922 | PASS |
| R02 / memory | 10862592 | 49528832 | 678461440 | 1.814 | PASS |
| R03 / encoder | 10792960 | 51650560 | 51650560 | 7.924 | PASS |
| R04 / decoder | 10608640 | 52609024 | 60456960 | 7.876 | PASS |

**R02 ist ein Ablehnungstest, kein erfolgreicher hoher Verbrauch:** VirtualAlloc fordert 600 MiB reservierten und committed nativen Speicher an. Es liefert NULL, Windowsfehler 1455. Der Worker bleibt bereinigungsfähig und endet mit Code 0. Windows verzeichnet den abgelehnten Anforderungsversuch im Job-Peak (678.461.440 Byte); dieser Wert darf nicht als erfolgreiche Belegung oder bestandener Normalfall unter 512 MiB interpretiert werden. Die gesampelte gemeinsame tatsächliche Belegung lag dabei höchstens bei 49.528.832 Byte. Der Jobgrenzwert wurde nicht erhöht.

Der normale gemeinsame Kernel-Peak beträgt 75.165.696 Byte; die höchste einzelne Prozess-Lebenszeitspitze im Job beträgt 56.786.944 Byte. Supervisor-Grundbelegung: 11.120.640 Byte; Worker zu Beginn der gemessenen Initialisierung: 12.546.048 Byte. Alle vier Worker endeten kontrolliert mit Code 0.

## Normale Phasen

Die folgende Tabelle enthält Worker-Private-Bytes an Phasengrenzen und Python-Phasenspitzen; native Phasenspitzen aus Sampling folgen separat. Wiederholte Konstruktor-/Verarbeitungsnamen gehören in Reihenfolge zum 64- und zum 48-Frame-Fall.

| Phase | Sekunden | Worker Anfang | Worker Ende | Python-Peak |
| --- | ---: | ---: | ---: | ---: |
| imports_and_initialization | 1.648 | 12546048 | 35414016 | 12634942 |
| D_hand_case_material | 0.009 | 35414016 | 35414016 | 9914065 |
| D_hand_case_arms_references_observer | 0.006 | 35414016 | 35414016 | 9921930 |
| constructor_U | 0.001 | 35414016 | 35414016 | 9931074 |
| processing_U | 2.572 | 35414016 | 36388864 | 10536498 |
| constructor_R | 0.002 | 36388864 | 36388864 | 10507555 |
| processing_R | 9.070 | 36388864 | 37687296 | 11538729 |
| D_hand_case_encoder_and_file_output | 83.279 | 37687296 | 44621824 | 14671819 |
| D_hand_case_stream_decoder | 31.278 | 44621824 | 53178368 | 22253020 |
| D_hand_case_cleanup | 0.066 | 53178368 | 43806720 | 16288048 |
| lifecycle_trace_material | 0.005 | 43933696 | 43933696 | 9896214 |
| lifecycle_trace_arms_references_observer | 0.007 | 43933696 | 43933696 | 9905241 |
| constructor_U | 0.001 | 43933696 | 43933696 | 9916042 |
| processing_U | 1.790 | 43933696 | 45441024 | 10517678 |
| constructor_R | 0.001 | 45441024 | 45441024 | 10482022 |
| processing_R | 6.214 | 45441024 | 45506560 | 11513963 |
| lifecycle_trace_encoder_and_file_output | 55.905 | 45506560 | 48353280 | 14138532 |
| lifecycle_trace_stream_decoder | 20.728 | 48353280 | 51257344 | 21708967 |
| lifecycle_trace_cleanup | 0.069 | 51257344 | 45645824 | 15158500 |
| final_cleanup | 0.012 | 45768704 | 45768704 | 9825467 |

| Gesampelte Phase | Supervisor-Peak | Worker-Peak | Gemeinsamer Sample-Peak |
| --- | ---: | ---: | ---: |
| D_hand_case_cleanup | 17534976 | 53178368 | 70713344 |
| D_hand_case_encoder_and_file_output | 17547264 | 44621824 | 61956096 |
| D_hand_case_stream_decoder | 17534976 | 53522432 | 71057408 |
| complete | 18378752 | 39395328 | 57774080 |
| imports_and_initialization | 12845056 | 37416960 | 50262016 |
| lifecycle_trace_cleanup | 18378752 | 51257344 | 69636096 |
| lifecycle_trace_encoder_and_file_output | 18378752 | 48353280 | 66732032 |
| lifecycle_trace_stream_decoder | 18378752 | 51531776 | 69910528 |
| processing_R | 17547264 | 46858240 | 64393216 |
| processing_U | 17534976 | 45441024 | 62976000 |
| startup | 12304384 | 12447744 | 24752128 |
| transition | 18378752 | 45768704 | 64147456 |

Die Konstruktoren des Produktionsarms sind explizit markiert; die unabhängige Referenz wird unmittelbar danach in processing_U/R konstruiert und vollständig mitgemessen. Verarbeitung umfasst Aufnahme, Feedback, interne/äußere Beobachter, eigene Referenzen, Fehlerzellen, Gleichheitsprüfung und Arm-Cleanup. Auch Prüfvergleiche nach R sind in processing_R enthalten. Encoder und Dateiausgabe sind bewusst eine gemeinsame Phase.

## Verlustfreie Erfassung, Export und Cleanup

Beide Handfolgen stammen unverändert aus D_ITEMS beziehungsweise LIFECYCLE. In diesem Ressourcenpaket wird für beide der vollständige interne Trace eingeschaltet; der frühere D-Handfall hatte nur äußere Ereignisse. Deshalb ist sein neuer rekonstruierter Record größer und nicht bytegleich zum alten D-Record. Dies ist zusätzliche Beobachtung, keine Änderung von Material oder Policy.

| Fall | Frames | Äußere / interne Ereignisse je Arm | Spoolbytes | Größter Record | gzip | Dekomprimiertes Format | Rekonstruierter Record |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| D_hand_case | 64 | 192 / 716 | 19677758 | 15142 | 24009 | 339310 | 19728363 |
| lifecycle_trace | 48 | 144 / 552 | 13338998 | 15147 | 19768 | 266560 | 13380342 |

Beide vollständigen Quellrecords werden aus der Spoolfolge kanonisch gehasht; der unabhängig implementierte Decoder rekonstruiert anschließend dieselbe Bytezahl mit demselben SHA-256 fortlaufend. Darüber hinaus ist der Lebenszyklus-Quellhash 940b29d1f24deac9e1dfcf575234089ff6c78d29415aefce7972598fe66996cd exakt der Hash des ursprünglichen vollständigen neutralen Lebenszyklusrecords. Das belegt für diesen Fall auch Gleichheit zur unveränderten historischen Referenz. Die alte gzip-Datei wurde nicht überschrieben.

R03 verwendet die ersten zwei vorhandenen Lebenszyklusblöcke (8 Frames), injiziert INJECTED_ENCODER nach begonnener Dateiausgabe und bestätigt Arm-Cleanup, Entfernung der Partialdatei und sämtlicher Spooldateien. R04 verwendet denselben festen Präfix und injiziert einen falschen externen Decoderhash; BINDING wird erkannt, die nicht abgenommene Archivdatei sowie Spooldateien werden entfernt. Keine Teilresultate werden als gültig ausgewiesen. Native Ablehnung R02 und die Dateifehler sind getrennte Szenarien; es wird keine simultane Fehlertoleranz behauptet.

## Test-IDs

- R01: zwei vollständige kleine Fälle unter gemeinsamem harten Windows-Job, Referenzen, Ereignisgleichheit, verlustfreie Rekonstruktion, Grenzen und Cleanup: PASS.
- R02: native Speicheranforderung oberhalb des unveränderten Jobbudgets abgelehnt, Worker beendet: PASS.
- R03: Encoderfehler nach begonnener Ausgabe, partielle Datei und Spool bereinigt: PASS.
- R04: Decoder-Bindungsfehler, nicht abgenommenes Archiv und Spool bereinigt: PASS.
- tests.test_s2uc_ura1_resource_stream.StreamTests.test_R05_collection_lossless_order_and_cleanup: PASS.
- tests.test_s2uc_ura1_resource_stream.StreamTests.test_R06_record_and_total_bounds_cleanup: PASS.
- tests.test_s2uc_ura1_resource_stream.StreamTests.test_R07_original_and_policy_bindings: PASS.

R05–R07 wurden als fokussierte Komponententests ausgeführt (3 Tests, 0,069 s); ihre Laufzeit ist kein Job-Ressourcennachweis und wird nicht in R01 eingerechnet. R05 prüft explizit Byte-/Wertrekonstruktion und Reihenfolge einer dateigestützten Folge. R06 prüft Einzelrecord- und Gesamtabweisung mit Cleanup. R07 prüft beide bisherigen Closures, die fünf ursprünglichen Entwicklungsdateien und die vollständige Gleichheit des fachlichen Prüfcodes nach Rücknahme ausschließlich der Spoolersetzung.

## Aussage- und Messgrenzen

Der Job-Commit schließt native Allokationen der eingeschlossenen Prozesse ein; Python-Tracerwerte ersetzen ihn nicht. Es gibt keine Zuordnung jeder nativen Allokation zu einem bestimmten Konstruktor. Unter einer Millisekunde kurze Konstruktorphasen werden nicht notwendig vom 10-ms-Sampling getroffen; Python-Peaks und Prozess-Lebenszeitspitzen ergänzen sie, der kernelgemessene gemeinsame Peak erfasst den ganzen Job. Sample-Phasenwerte sind ausdrücklich keine exakten transienten Maxima.

Die Python-Interpreterinitialisierung vor Installation des Supervisor-Jobs ist nicht vollständig zeitaufgelöst. Sie wird durch Grundbelegung und Prozess-Lebenszeitspitze eingeordnet; alle beauftragten Material-, Arm-, Referenz-, Beobachter- und Codecschritte beginnen nach Jobinstallation/Workerprüfung. Der externe Codex-Aufrufer ist nicht Teil dieses Jobs. Dateisystemcache außerhalb des privaten Prozess-Commits sowie globaler System-/Treiberverbrauch sind ebenfalls nicht dessen Speichermaß.

Der Peak enthält die zusätzliche Messinstrumentierung. Spooldateien werden separat als temporärer Plattenbedarf ausgewiesen. Der normale Lauf schreibt fallweise bis zu 19.677.758 Byte temporäre redundante Daten und entfernt sie vor dem nächsten Fall; sie zählen nicht als dauerhaftes gzip-Archiv, sind aber kein kostenfreier Speicher. Betriebssystem-/Python-Caches können nach Cleanup weiter belegt sein; Cleanup bedeutet hier geschlossene Arme, entfernte temporäre Dateien und beendete Worker, nicht Rückkehr auf exakt denselben Private-Bytes-Wert.

## Genau ein späterer Größenablauf: Vorschlag und aktuelle Hürde

Der verlinkte Vorschlag definiert genau eine 1024-Frame-Handgeschichte aus D_ITEMS ×16, zwei Arme U/R und dieselben Referenz-/Ereignisprüfungen. Er ist nicht ausgeführt und benötigt einen gesondert beauftragten Einstieg; die bestehende 128-Frame-Grenze bleibt erhalten. Ein voller 32-Geschichten-Forschungsumfang wird damit nicht vorweggenommen.

**Konkretes Skalierungsrisiko:** Bereits 64 Frames benötigen 19.677.758 Byte Spool. Eine lineare Hochrechnung ergäbe rund 315 MB bei 1024 Frames; das ist eine Warnabschätzung, keine Messung. Sie liegt deutlich über der beibehaltenen 64-MiB-Spoolgrenze. Deshalb empfehle ich vor einer Freigabe dieses einen Größenablaufs zuerst direkt referenzierende fortlaufende Erfassung beziehungsweise früheres verlustfreies Kompaktieren der Spooldaten zu prüfen. Den vorhersehbaren Spoolengpass durch Erhöhung der Grenze oder Kürzen von Ereignissen zu umgehen wäre nicht zulässig.

Nächster fachlich sinnvoller Schritt: der Projektleiter bewertet diesen vollständig belegten Kleinfallstand und beauftragt gegebenenfalls genau die Beseitigung des Spool-Skalierungsengpasses. Die jetzt gemessenen kleinen Fälle begründen weiterhin keine Forschungsbereitschaft. Der Größenablaufvorschlag bleibt bis zu passender gesonderter Freigabe geschlossen.

## Belege

- [normal/worker.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/normal/worker.json)
- [normal/supervisor.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/normal/supervisor.json)
- [normal/worker.log](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/normal/worker.log)
- [memory/worker.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/memory/worker.json)
- [memory/supervisor.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/memory/supervisor.json)
- [memory/worker.log](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/memory/worker.log)
- [encoder/worker.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/encoder/worker.json)
- [encoder/supervisor.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/encoder/supervisor.json)
- [encoder/worker.log](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/encoder/worker.log)
- [decoder/worker.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/decoder/worker.json)
- [decoder/supervisor.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/decoder/supervisor.json)
- [decoder/worker.log](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/decoder/worker.log)
- [D_hand_case.dag.json.gz](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/normal/D_hand_case.dag.json.gz)
- [lifecycle_trace.dag.json.gz](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-resource-development-20261014-01/normal/lifecycle_trace.dag.json.gz)
- [Vorschlag für genau einen Größenablauf](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/docs/S2UC_URA1_NEUTRALER_GROESSENABLAUF_VORSCHLAG_20261014.md)
