# CR1 – Implementierung und neutrale Qualifikation

2026-10-17. Workflow-Auftrag `12411fb6-b054-4fec-808a-bcda26a48dd8`.
Status: **IMPLEMENTIERT / NEUTRAL GEPRÜFT / KEINE FORSCHUNGSFREIGABE**.
Grundlage ist der vom Projektleiter angenommene [Konzeptvertrag](../../../docs/S2UC_URA1_CR1_KALTAUSWAHL_KONZEPTVERTRAG_20261017.md). Dessen historischer Einreichungsstatus bleibt als Zeitstand erhalten; der jetzige Auftrag nimmt den Vertrag an, ohne seine Regel oder Forschungsgrenzen zu ändern.

## Umsetzung

`tools/_s2uc_ura1_cr1.py` implementiert C als Unterklasse von U. Ein einziger Freeze-/Receipt-Durchlauf validiert und friert dieselben Hypothesen ein. Nur bei nicht leerem H ohne gültige Fehlerzelle wählt C den Nachfolger mit größter Originalordinalzahl, bei Gleichstand das kleinste Tupel (role,generation,offset). Entscheidung `SELECTED_COLD_ORIGINAL_RECENCY`, Bank-Reason 6. Jede warme Zelle, auch EC−EP=0, führt zur unveränderten U-Entscheidung. Gemischte Bestände, negative Gleichstände, fehlende negative Bewertung, deaktivierter Adapter und unvollständige Paare bleiben U-konform.

Kein neuer persistenter Lernzustand; weiterhin sechs Zellen und 416 Byte. Rückmeldung, Aufnahme, Promotion, Pruning und Cleanup sind dieselben geerbten Methoden. Der explizite U-Receipt-Code bleibt im CR1-Modul nachvollziehbar; historische U-/R-Dateien wurden nicht editiert.

Die unabhängige C/U-Referenz führt eigenen Bestand, Schlüssel und Fehlerzellen und verwendet sortierte Originaldatensätze statt des laufenden Maximums der Implementierung. Der neue Executor prüft Ausgaben, Wahl, Begründung, Headerbytes, Tickets, Originale, Rückmeldung und Bestand gegen diese Referenz. Der gemeinsame Zustandsvergleich normalisiert ausschließlich Bytes 202 und 203; sämtliche 416 Byte wurden einzeln als Negativkontrolle geprüft.

Getrennte C/U-Archivprüfung: explizite Armerkennung, Vergleich gemeinsamer Ereignisse und Hypothesen, Kaltzweigregel, vollständige C/U-Identität außerhalb dieses Zweigs. Zusätzlich unabhängiger Referenzdurchgang durch die gespeicherten 32-Frame-Quellen und dekodierten Prognosen/Fehlerdaten. Neue gültige Archivprüfsummen reichen nicht aus, um verfälschte Fehler, kalte Ausgaben, Begründungen oder einen umbenannten R-Arm zu akzeptieren. Decoder, Codec, Integritätsanker und Schutzgrenzen bleiben unverändert.

Getrennte Quellenimplementierung und unabhängige Rekonstruktion verwenden das festgelegte REV1-Rezept. Ausschließlich der neutrale Namensraum `MCM-URA1-CR1/neutral/v1` wurde ausgewertet. Die 32 vollständigen neutralen Rezeptprüfungen sind reine Quellengeneratorprüfungen; keine davon wurde als 1024-Frame-Policygeschichte ausgeführt. Echte Policytests verwenden kurze, fest ausgeschriebene Handfolgen. Forschungsnamensraum `MCM-URA1-CR1/source/v1` bleibt vor der Hashberechnung gesperrt, solange keine gesonderte Aufnahme vorliegt.

Statistik und unabhängige Statistikreferenz berechnen ausdrücklich **C−U** für alle Q129–160 je Geschichte. Alle 32 Geschichten bleiben im Nenner, auch ohne kalte Treffer. Untere Grenze >0 bedeutet U besser/C nachteilig; obere Grenze <0 bedeutet C besser; Nullberührung oder -überschreitung bleibt INCONCLUSIVE. Leere diagnostische Teilgruppen haben Anzahl 0 und `mean_delta=null`. Feste Bootstrapindexmatrix unverändert; ausschließlich künstliche Fehlerdaten wurden ausgewertet.

## Testnachweise

[Finale Testliste mit Ressourcen](unit-tests.json), [Einzellog](unit-tests.log): **29/29 PASS**, keine Fehler, Fehlschläge oder übersprungenen Tests.

| IDs | Geprüfter Umfang |
|---|---|
| P01–P03 | Methodenidentität, kein zusätzlicher Instanzzustand; rein kalt, gemischt, warme Null-/Positivbewertung, negativer Gleichstand, eindeutiger Gewinner; Originalzeitgleichstand und Reihenfolge |
| P04 | Erste kalte Wahl → gültiges Feedback → warme Wahl; gleiche Aufnahme-, Promotions- und Verdrängungsereignisse in einer 48-Frame-Handfolge |
| P05–P08 | Leere/ungeeignete Hypothesen, deaktivierter Pfad, ungültige Identitäten/Zellen; verbotene Rückkopplungen erkannt; Fehlercleanup und genau ein Freeze |
| P09–P10 | Unabhängige Archivsemantik einschließlich neu gehashter Verfälschungen; ausschließlich choice/reason normalisiert |
| S01–S06 | Forschungssperre vor Hash, 32 neutrale Quellenreferenzen, Mutationen, Rejection Sampling, Ziehungsgrenze, exakter neutraler Namensraum |
| T01–T09 | Matrix, Q128/129 und Q160/161, Nenner und Vorzeichen, nichtkonstante Intervalle, Nullberührung, unvollständige Daten, referenzseitige Fehlererkennung, Geschichten ohne kalte Treffer |
| E01–E04 | Fehlende Forschungserlaubnis, exklusives Ziel ohne Resume, unveränderte Schutzobjekte, getrennte Produktionsintegration |
| G01 | Zwei echte 32-Frame-Handfälle, vier frische U/C-Arme, jeweils 96 äußere und 372 interne Ereignisse pro Arm; unabhängige Referenzen und Archivprüfung |
| G02 | Administrationsbudget absichtlich um ein Byte überschritten; nach Fall 1 in Fall 2 technischer Abschluss, kein Teilserienurteil, bestätigtes Cleanup |

G01: [Terminal](integration-complete/terminal.json), [Fall 1](integration-complete/case-01-continuity.json), [Fall 2](integration-complete/case-02-continuity.json), [Integrität](integration-complete/neutral-integrity.json). Am neutralen Schnitt 16/17 bleiben Arm, Bank und gemeinsame Zustände identisch; zwei warme Zellen bleiben erhalten. Kein Reset und kein Schnittsignal an die Policy.

G02: [Fehlerabschluss](integration-admin/terminal.json). Erwartet `TECHNICAL_ABORT`, completed_cases=[1], active_case=2, drei erzeugte Arme, Worker beendet, Arm- und Datei-Cleanup bestätigt. Der negative Test überschreitet absichtlich die 2-MiB-Administrationsgrenze um ein Byte; genau dies löst den Schutzabschluss aus. Sein Artefakt bleibt als Nachweis erhalten.

Erster Entwicklungsstand: 28 Tests bestanden. Anschließend ausschließlich Nullteilgruppenmittel explizit gemacht und byteweisen Normalisierungstest ergänzt; finale 29 Tests erneut bestanden. Erste Testquittung unter `unit-tests-attempt-01.*` erhalten. Keine Forschungswiederholung.

## Ressourcen und Bindung

Finale Units: 34.429337700014 s, Jobpeak 48599040 Byte. G01: 10.6531265 s, Jobpeak 53972992 Byte. G02: 5.5853654 s, Jobpeak 50610176 Byte. Alle Prozesse liefen mit harter 512-MiB-Jobgrenze; Integrations-Supervisor und Worker höchstens zwei Prozesse. Die explizite Fehlerauslösung ist oben getrennt ausgewiesen.

Die abschließende [Archivreferenzquittung](archive-reference-verification.json) enthält die erneute unabhängige Prüfung der bereits gespeicherten kurzen Integrationsarchive, deren Größen und Ressourcen. Keine neuen Policyausführungen dabei. [Vererbungsbeleg](inheritance.json) bindet sämtliche unveränderten Dateien des REV1-Vorstarts `3d05e2fc657a704be3fb5901a302c0c81e519aefaa377909529686a6cf7e650d`; übernommen wird nur der jeweilige unveränderte Schutz-/Implementierungsumfang, kein C-Nachweis aus U/R.

[Vorstartbindung](prestart.json), [SHA](prestart.sha256), [Abschlussprüfung und genaue Paketgröße](seal-verification.json), [Ressourcenplan](resource-plan.json). Bericht und neue Module sind im Vorstart gebunden. Drei veränderliche Projektübersichten und die nachträgliche Siegelquittung bleiben zur Vermeidung zirkulärer Hashes außerhalb der Bindung.

Alle Vertragsgrenzen bleiben: global 57600 s, Worker 54000 s, Abschlussreserve 3600 s innerhalb der Gesamtfrist; Job 512 MiB/2 Prozesse; Vorbereitung 8 MiB; Quellen 2 MiB/32 KiB je Fall; Archive 32 MiB/512 KiB je gzip; encoded/dictionary je 4 MiB; record 256 KiB; nodes 65536, edges 262144, indices 65536, collections 16; temporär und Gesamtexport je 64 MiB; Administration 2 MiB, Closure 1 MiB. Export zählt Vorbereitung und temporäre Dateien mit.

## Zukünftiger Aufruf – nicht ausgeführt

Arbeitsverzeichnis `C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace`:

```powershell
& 'C:/Python314/python.exe' -m tools.s2uc_ura1_prepare_cr1 run 'C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-cr1-preparation-20261017-01/prestart.json' 'C:/Users/TV/Documents/MCM_FIELD_ORGANISM/workspace/reports/s2uc/ura1-cr1-preparation-20261017-01/authorization.json'
```

Erfordert eine separate ausdrückliche Einmallauffreigabe zum exakten Vorstart-SHA; Schema in `prestart.json`. Autorisierungsdatei wurde nicht erzeugt. Exklusives Forschungsziel `reports/s2uc/ura1-cr1-comparison-16h-01` fehlt weiterhin. Keine Forschungsquelle und kein neuer Forschungsstartmarker. Historische verbrauchte Marker bleiben unverändert. Zielanlage schlägt bei vorhandenem Verzeichnis fehl; kein Resume, Retry oder Ersatzlauf.

## Grenzen und nächster Schritt

Nachgewiesen ist die begrenzte neutrale technische Umsetzung. Keine 1024-Frame-Policygeschichte, keine Forschungsserie, kein gemessener C-Nutzen und keine Laufzeitgarantie für die vollständige Serie. Insbesondere ist der zusätzliche Aufwand der C/U-Archivreferenz bei Vollgröße ungemessen; harte Schranken führen gegebenenfalls zum technischen Abbruch. Die Hypothese bleibt diagnosemotiviert; historische Daten werden nicht als unabhängiger C-Beleg ausgegeben. Gleiche Fehlerzustände und Aufnahme bedeuten, dass selbst ein späterer Ausgabevorteil keine verbesserte Erfahrungsbildung beweist.

Empfehlung an den Projektleiter: dieses konkrete Vorbereitungspaket samt Vorstart-SHA abnehmen; anschließend über genau einen gesondert autorisierten C/U-Vergleich nach dem unveränderten Vertrag entscheiden. Bis zu dieser Entscheidung bleibt die Forschung geschlossen. Keine weitere Varianten- oder Namensraumsuche.
