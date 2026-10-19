# V7: isoliertes Ressourcenledger abgeschlossen

Implementiert: `tools/_s2uc_resource_contract_v7.py` und `tests/test_s2uc_resource_contract_v7.py`.

71/71 Entwicklungstests bestanden (14 neue Tests, 57 bestehende S2-UC-Tests), Exitcode 0. Vollstaendige Ausgaben: `tests.stdout.txt`, `tests.stderr.txt`; ausgefuehrte Test-IDs und Kommando: `test-result.json`.

Dateigroessen und SHA256 werden aus realen Dateien ermittelt. Reservierungen bleiben getrennt von Ist-Messungen. Vollstaendigkeit gilt innerhalb des angegebenen Verzeichnisses; der Aufrufer muss die verbindliche Zuordnung bereitstellen. Keine Aussage ueber atomare Snapshots bei gleichzeitigen Dateiaenderungen.

Grenzen und Grenze+1 sind mit temporaeren Dateien geprueft. Der Gesamttest erreicht die feste Gesamtgrenze unter gleichzeitiger Verletzung der Codegrenze; ein zusaetzlicher isolierter Arithmetiktest prueft den Vergleich ohne produktiven Grenzwert-Override. Auch die Shared-Grenze ist wegen der engeren Unterkonten nicht isoliert erreichbar. Manipulierte, intern konsistente Summen werden gegen den Dateibestand verworfen.

Statische Importinventur einschliesslich aller drei Testsuiten und ihrer Projektabhaengigkeiten: 34 Dateien, 574658 Byte. Codegrenze 655360 Byte; verbleibend 80702 Byte. Details, Importkanten, externe Laufzeitabhaengigkeiten und Hashes: `dependency-inventory.json`.

Abschlussalternativen bei voll reservierten Code-/Metadaten-/statischen-/Stagingkonten:

| Alternative | Byte |
|---|---:|
| Erfolg | 1556480 |
| Fehler vor Publikation | 1196032 |
| Fehler nach Publikation | 1572864 |
| Fehler mit gleichzeitig vorhandenem Minimalabschluss | 1589248 |

Die Alternativen sind Reservierungen, keine Messung eines realen Quellenlaufs. Ihre Summen wurden zusaetzlich mit temporaeren Dateien getestet. Details: `closure-alternatives.json`.

Alle 13 vorher erfassten S2-UC-Code-/Testdateien unveraendert; Vorher-/Nachher-SHA256 und neue Dateien: `before.json`, `changed-files.json`. Starter, Materialisierung, Publikation und alte Ledger bleiben unveraendert. Keine formale Neuqualifikation und kein realer Quellenlauf. Prozessspeicher nicht gemessen.

Naechster Vorschlag fuer den Projektleiter: diese isolierte Grundlage abnehmen, danach ein begrenztes V7-Integrationspaket fuer verbindliches Abhaengigkeitsinventar und Starterpruefung festlegen. Die Integration ist in diesem Paket nicht ausgefuehrt.
