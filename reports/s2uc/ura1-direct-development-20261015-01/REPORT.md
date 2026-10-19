# URA1: Abschluss der begrenzten direkt referenzierenden Erfassung

Stand 2026-10-15. MCM-KI-Entwickler an MCM KI Projektleiter.
Bezug: Anschlussauftrag zur Beseitigung des belegten temporären JSONL-Engpasses nach Abnahme der Kleinfall-Ressourcenqualifikation.

**PASS_BOUNDED_DIRECT_CAPTURE.** Beide vorhandenen 64-/48-Frame-Handfolgen sind unter dem gemeinsamen harten 512-MiB-Windows-Job vollständig qualifiziert. Der unabhängige, unveränderte Decoder rekonstruiert exakt die bisherigen kanonischen Ressourcenrecords. Kein Ereignis wurde gekürzt. Keine Forschungsbereitschaft und kein ausgeführter Größenablauf.

## Implementierung und Begrenzung

- [tools/_s2uc_ura1_direct_archive.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_direct_archive.py): Direktes Internieren vollständiger Records, geordnete Referenzfolgen, begrenzte Finalisierung und Ausgabe.
- [tools/_s2uc_ura1_direct_neutral.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/_s2uc_ura1_direct_neutral.py): Neue Prüfhülle; gegenüber der vorherigen Ressourcenhülle ausschließlich anderer Collectionimport und Docstring.
- [tools/s2uc_ura1_direct_qualify.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tools/s2uc_ura1_direct_qualify.py): Getrennte Phasenmessung und Kleinfall-/Fehlerqualifikation im gemeinsamen Windows-Job.
- [tests/test_s2uc_ura1_direct_archive.py](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/tests/test_s2uc_ura1_direct_archive.py): Sieben fokussierte Tests D02–D08.
- [docs/S2UC_URA1_DIREKTERFASSUNG_GRENZEN_20261015.md](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/docs/S2UC_URA1_DIREKTERFASSUNG_GRENZEN_20261015.md): Dokumentierte Grenzen und Integritätsvertrag.

Aufnahme, Auswahl, Lernen, Referenzen und sämtliche fachlichen Ereignisprüfungen bleiben unverändert. D07 prüft die ursprünglichen Bindungen und vergleicht den vollständigen Prüfcode nach Rücknahme genau des Import-/Docstringwechsels. Das bereits geprüfte Format URA1_JSON_DAG_V1 und sein unabhängiger Decoder bleiben unverändert.

Jeder Record wird unmittelbar in einen gemeinsamen Teilbaum-Dictionary überführt. Die Collections halten nur geordnete Knotennummern. Für Vergleiche werden aktuelle Records rekonstruiert; kein unbeschränkter Rekonstruktionscache und keine vollständige redundante Historie werden gehalten. Die Finalisierung referenziert vorhandene Knoten, kodiert das begrenzte JSON-Dokument und komprimiert es einmal.

| Verwaltung / Puffer | Unveränderte oder zusätzliche feste Grenze je Fall |
| --- | ---: |
| Knoten | 65.536 |
| Referenzkanten | 262.144 |
| Recordindizes insgesamt | 65.536 |
| Collections | 16 |
| Einzelrecord, kanonisch einschließlich Zeilenumbruch | 262.144 Byte |
| Serialisierte Dictionaryknoten insgesamt | 4.194.304 Byte |
| Vollständiges dekomprimiertes Archivformat | 4.194.304 Byte |
| gzip-Archiv | 524.288 Byte |
| Temporäre Dateien insgesamt | 67.108.864 Byte |
| Gemeinsamer harter Windows-Job | 536.870.912 Byte |

Die Dictionary-Bytegrenze ist keine Python-Heapbehauptung. Tabellen, Schlüssel, Indizes, Containerüberallokation und JSON-/gzip-Zwischenbuffer werden zusätzlich vom gemeinsamen Prozessbudget erfasst. Anzahl und Nutzdatenmenge der Verwaltung sind beschränkt; es gibt kein unbegrenztes Wachstum im RAM. Der JSON-Buffer kann während der Konvertierung gleichzeitig als String und Bytes vorliegen; auch dies ist prozessweit gemessen.

## Vorher/Nachher: temporäre Ablage und Archive

Die einzige temporäre Datei ist nun die gzip-Partialdatei im Zielverzeichnis. Keine Rohhistorie, Dictionarydatei, Journale oder rekonstruierte Historie werden auf Platte abgelegt. Nach erfolgreichem Schreiben erfolgt eine Umbenennung im selben Verzeichnis, keine Kopie. Der Peak wird nach jedem Schreibabschnitt erfasst. Die Werte sind logische Dateibytes; Dateisystemblockbelegung ist kein separat gemessener Wert. Veröffentlichtes gzip und dauerhafte Prüfprotokolle sind keine temporären Zwischenkopien und werden im Abschlussmanifest separat bilanziert.

Der alte gleichzeitige temporäre Bedarf lässt sich aus den gespeicherten Spoolbytes plus der damals gleichzeitig geschriebenen gzip-Partialdatei bestimmen; er wird unten als abgeleiteter Vorherwert gekennzeichnet.

| Fall | Alte JSONL-Daten | Alter gleichzeitiger temporärer Bedarf (abgeleitet) | Neuer gemessener temporärer Peak | Neues gzip | Neues dekomprimiertes Format | Vollständig rekonstruierter Record |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| D_hand_case | 19677758 | 19701767 | 23491 | 23491 | 339990 | 19728363 |
| lifecycle_trace | 13338998 | 13358766 | 19210 | 19210 | 267066 | 13380342 |

Während der Erfassung selbst beträgt der neue temporäre Dateibedarf null. Die größte gleichzeitig vorhandene temporäre Datei im normalen Ablauf umfasst 23.491 Byte; die 64-MiB-Spoolgrenze wird ohne Umdefinition einer komprimierten inneren Nutzlast eingehalten. Die größeren rekonstruierten Historien bleiben vollständig erhalten.

| Fall | Knoten final | Kanten final | Recordindizes | Dictionarybytes final | Größter Record | Collections |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| D_hand_case | 2699 | 13980 | 1942 | 337128 | 15142 | 8 |
| lifecycle_trace | 2179 | 10801 | 1486 | 264724 | 15147 | 8 |

## Vollständige Rekonstruktion gegen vorhandene Belege

Die erwarteten Originalhashes und Bytezahlen werden aus dem unveränderten, über seine Closure gebundenen worker.json des vorherigen Ressourcenpakets gelesen. Der neue Encoder setzt diese Referenzangaben nur in das Format ein. Erst der unabhängige Decoder bestätigt sie durch vollständige kanonische Rekonstruktion aller Bytes. Die Bestätigung umfasst Originalmetadaten, Hypothesen, Tickets, Fehlerzellen, Auswahlunterschiede und jede Ereignisposition.

| Fall | Äußere / interne Ereignisse je Arm | Kanonischer SHA-256, gleich zum bisherigen Ressourcenrecord |
| --- | --- | --- |
| D_hand_case | 192 / 716 | `abc86c2b96fddd529aa1101f7d7364063ca515be174e7b9dae97a77b426a7d78` |
| lifecycle_trace | 144 / 552 | `940b29d1f24deac9e1dfcf575234089ff6c78d29415aefce7972598fe66996cd` |

Zusätzlich prüft D02 einen vollständigen Bytevergleich einschließlich Reihenfolge, wiederholter Originalidentitäten, Tickets, Fehlerzellen und Typen. Es wurden keine neuen Quellen gewählt; die ursprünglichen Handfolgen D_ITEMS und LIFECYCLE bleiben unverändert.

## Prozess- und Laufzeitvergleich

Normaler Ablauf: Supervisor und genau ein geerbter Worker im gemeinsamen Windows-Job, harte Commitgrenze 536.870.912 Byte, ActiveProcessLimit=2. Die Workerzugehörigkeit wurde vor Arbeitsbeginn am konkreten Prozesshandle bestätigt. Beide finalen Qualifikationsszenarien endeten mit Exitcode 0.

| Messgröße | Vorher | Nachher |
| --- | ---: | ---: |
| Gemeinsamer Kernel-Job-Peak (Byte) | 75165696 | 69181440 |
| Gemeinsamer gesampelter Private-Bytes-Peak | 71057408 | 64323584 |
| Supervisor-Grundbelegung (Byte) | 11120640 | 10833920 |
| Gesamtlaufzeit (s) | 212.922 | 94.934 |

Die Tabelle der Phasen zeigt die Arbeitsteilung: Referenzierung findet jetzt schon während der Erfassung statt. Deshalb steigt dort die Laufzeit; die bisherige nachträgliche vollständige Wiederverarbeitung entfällt weitgehend. Die Decoderimplementierung ist unverändert. Die Zeiten enthalten die gleiche tracemalloc-Instrumentierung und sind keine instrumentierungsfreien Leistungsbenchmarks.

| Fall / Phase | Vorher Sekunden | Nachher Sekunden | Nachher Python-Peak | Nachher gemeinsamer Sample-Peak |
| --- | ---: | ---: | ---: | ---: |
| D_hand_case: Erfassung + Referenzen + Prüfungen | 11.651 | 23.551 | 11413945 | 54075392 |
| D_hand_case: Finale Kodierung + Datei | 83.279 | 0.114 | 12110275 | 54665216 |
| D_hand_case: Unabhängiger Decoder | 31.278 | 31.738 | 20010691 | 63565824 |
| lifecycle_trace: Erfassung + Referenzen + Prüfungen | 8.013 | 15.674 | 11054347 | 60596224 |
| lifecycle_trace: Finale Kodierung + Datei | 55.905 | 0.105 | 11667518 | 60739584 |
| lifecycle_trace: Unabhängiger Decoder | 20.728 | 21.794 | 19629166 | 64323584 |

Phasenwerte des Prozesssamplings werden etwa alle 10 ms aufgenommen; sie können kurze Transienten verpassen. Der gemeinsame Kernel-Job-Peak ist nicht gesampelt. Python-Peaks sind absolute lebende Tracerallokationen mit pro Phase zurückgesetzter Peakmarke, keine isolierten Nettoallokationen. Native Allokationen sind im Prozess-Commit enthalten, werden aber nicht einzelnen Pythonobjekten zugeordnet. Interpreterstart vor Jobinstallation, globaler Dateisystemcache und externe Codex-Prozesse bleiben wie im Vorgängerbericht außerhalb dieser gezielten Phasenbilanz.

## Test-IDs, Fehlerfälle und Entwicklungskorrektur

D01: vollständige neue Erfassung beider vorhandener Fälle, unveränderte Ereigniszählung, Vergleich gegen die kanonischen Vorgängerrecords, Prozess-/Archiv-/Verwaltungsgrenzen und Cleanup: PASS.

- `tests.test_s2uc_ura1_direct_archive.DirectTests.test_D02_roundtrip_order_metadata_cells`: PASS.
- `tests.test_s2uc_ura1_direct_archive.DirectTests.test_D03_table_edge_dictionary_index_collection_limits`: PASS.
- `tests.test_s2uc_ura1_direct_archive.DirectTests.test_D04_record_and_temporary_limit`: PASS.
- `tests.test_s2uc_ura1_direct_archive.DirectTests.test_D05_write_and_encoder_failure_cleanup`: PASS.
- `tests.test_s2uc_ura1_direct_archive.DirectTests.test_D06_capture_failure_terminates_arm`: PASS.
- `tests.test_s2uc_ura1_direct_archive.DirectTests.test_D07_immutable_rules_references_and_check_scope`: PASS.
- `tests.test_s2uc_ura1_direct_archive.DirectTests.test_D08_integer_metadata_key_normalization`: PASS.

D03 injiziert niedrige Grenzen für Knoten, Kanten, Dictionarybytes, Indizes und Collections; D04 prüft einen tatsächlich zu großen Einzelrecord und eine injizierte niedrige temporäre Dateigrenze. Damit sind die Ablehnungspfade geprüft, ohne einen künstlichen Maximalgraphen als Größenlauf zu erzeugen. D05 injiziert Schreib- und Encoderfehler nach begonnener Partialausgabe; die Datei wird entfernt. D06 überschreitet die Indexgrenze während der realen kleinen Armerfassung; der Arm wird terminal geschlossen und seine Bank, Kandidaten und Retained-Spuren bereinigt. Der Store gibt Knoten und Indizes auch bei Ausnahmen frei.

Der erste Entwicklungsversuch wurde vom unabhängigen Decoder mit MEMBER abgewiesen: numerische Metadatenschlüssel waren nicht in die JSON-Schlüsselform normalisiert. Dieser Befund wurde nicht als Erfolg gewertet. Die Erfassung normalisiert jetzt Integer-Schlüssel zu Strings und ordnet sie wie der bestehende kanonische JSON-Record. D08 prüft dies ausdrücklich auch mit Schlüsseln 1, 2 und 10. Der korrigierte Fehlerpfad entfernt ein nicht abgenommenes Kandidatenarchiv bei Decoderfehlern.

Die ursprünglichen sechs Komponententests und der fehlgeschlagene erste Normalversuch bleiben getrennt dokumentiert; dessen Archiv ist ausschließlich als .rejected erhalten. Abnahmebelege sind faults-corrected und normal-corrected: sieben bestandene Komponententests (0,118 s im Worker) sowie D01 mit beiden vollständigen Fällen. Der korrigierte Fehler-/Komponententestjob hatte einen Kernel-Peak von 55.980.032 Byte und dauerte 2,130 s. Diese Entwicklungswiederholung war zur Fehlerkorrektur nötig und ist keine Forschungswiederholung.

## Einschätzung zum vorgeschlagenen einzelnen 1024-Frame-Größenablauf

Der JSONL-Spoolengpass ist beseitigt. Ein separat beauftragter einmaliger technischer Grenztest mit der bereits vorgeschlagenen festen Folge D_ITEMS ×16 erscheint **bedingt technisch vertretbar**, weil Verwaltung, Ausgabe und Prozessspeicher jetzt terminal begrenzt sind. Ein erfolgreicher vollständiger Durchlauf ist damit nicht prognostiziert. Die verbleibende dominante Frage ist die 4-MiB-Grenze der Dictionary-/Archivdarstellung, nicht mehr ein wachsender Rohspool.

Reine lineare Abschätzungen aus dem 64-Frame-Fall, ausdrücklich keine Messungen für 1024 Frames:

- Falllaufzeit Sekunden (ungefähr): 887.2.
- Dekomprimiertes Archivformat Byte: 5439840.
- Dictionarybytes: 5394048.
- gzip Byte: 375856.
- Knoten: 43184.
- Kanten: 223680.
- Recordindizes: 31072.

Die linearen Dictionary-/Formatabschätzungen überschreiten 4 MiB. Wiederholte Teilbäume können sublineares Wachstum ermöglichen; neue Zeitindizes, Generationen und Zustände können Wiederverwendung begrenzen. Daraus folgt weder ein sicherer Erfolg noch ein sicherer Abbruch. Die Laufzeitabschätzung liegt unter den vorgeschlagenen Fristen 3540/3600 s, ist aber ebenfalls keine Garantie. Prozessspeicher wird wegen fixer Grundkosten und variabler Objektbelegung nicht blind linear hochgerechnet.

Vor einem solchen einen Start braucht es den separat beauftragten Größen-Prüfeinstieg und eine unabhängige Integritätsbindung für den bislang nicht vorhandenen 1024-Frame-Record. Die aktuelle Vergleichshülle benutzt vorhandene Kleinfallhashes und behält ihre 128-Frame-Grenze. Sie wurde nicht still zum Größenrunner erweitert. Der Größenauftrag müsste einen terminalen Dictionary-/Formatabbruch als zulässigen technischen Befund behandeln; keine Grenzerhöhung, Kürzung, Teilmengenwertung oder Wiederholung.

Empfehlung an den Projektleiter: den jetzigen Kleinfallauftrag abnehmen und über genau diesen begrenzten Grenztest einschließlich seiner notwendigen Vorbereitung entscheiden. Eine weitere Policyänderung ist hierfür nicht angezeigt. Der Test ist hier nicht ausgeführt; Forschungsquellen, Bootstrapmatrix und Forschungsversuch bleiben unbeauftragt. Keine Forschungsbereitschaft wird behauptet.

## Belegverweise

- [normal-corrected/worker.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-direct-development-20261015-01/normal-corrected/worker.json)
- [normal-corrected/supervisor.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-direct-development-20261015-01/normal-corrected/supervisor.json)
- [normal-corrected/worker.log](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-direct-development-20261015-01/normal-corrected/worker.log)
- [faults-corrected/worker.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-direct-development-20261015-01/faults-corrected/worker.json)
- [faults-corrected/supervisor.json](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-direct-development-20261015-01/faults-corrected/supervisor.json)
- [faults-corrected/worker.log](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-direct-development-20261015-01/faults-corrected/worker.log)
- [Korrigierte Testausgabe](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-direct-development-20261015-01/faults-corrected/tests.txt)
- [D_hand_case.dag.json.gz](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-direct-development-20261015-01/normal-corrected/D_hand_case.dag.json.gz)
- [lifecycle_trace.dag.json.gz](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-direct-development-20261015-01/normal-corrected/lifecycle_trace.dag.json.gz)
- [Getrennt dokumentierter abgewiesener Entwicklungsversuch](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-direct-development-20261015-01/normal/attempt.json)
- [Unveränderter früherer Vorschlag; technische Einordnung heute siehe oben](C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/docs/S2UC_URA1_NEUTRALER_GROESSENABLAUF_VORSCHLAG_20261014.md)
