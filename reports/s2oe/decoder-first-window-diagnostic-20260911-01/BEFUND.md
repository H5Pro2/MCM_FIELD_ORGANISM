# Decoderdiagnostik: neutrale Qualifikation nicht bestanden

Stand: 2026-09-11. Bezugscommit
`537109994cf777f8d36cda617aafe12226806c25`; bestehender schmutziger Arbeitsbaum.
Qualifikations-ID: `decoder-phase-neutral-20260911-01`.

## Umfang und Ergebnis

Die Workerdiagnostik wurde als `s2oe.decoder-job.v2-phase-diagnostic`
ergänzt. Ursprünglicher Fehlercode, Ausnahmetyp, Modul, errno und begrenzter
Stack ohne lokale Werte bleiben getrennt von Jobmeldungen erhalten.
Phasenmeldungen übertragen nur Phase, Operation und Sequenz. Der letzte
bestätigte Stand bleibt auch bei abruptem Kanalende erhalten; er wird nicht
als genaue native Auslösestelle ausgegeben. Prozessstatus vor Abbruch und
abschließender Exitcode sind getrennt.

Keine Decoderoptimierung: Auswahl, RGB-Konvertierung, Formate und
512-MiB-Commitgrenze bleiben unverändert. Die Änderungen und sechs aktiven
Dateien wurden vor dem Test in `binding.json` gehasht.

Genau ein neutraler Testaufruf, fünf Prüfgruppen, **4/5 bestanden**:

- ursprünglicher Fehler und Stack: bestanden;
- MemoryError getrennt erhalten: bestanden;
- begrenzte Diagnose ohne Rohpayloads, unveränderte Limits: bestanden;
- abruptes Workerende mit letzter Phase und unbekannter Ausnahme: bestanden;
- synthetische Limitmeldung zusammen mit ursprünglichem ValueError: nicht bestanden.

Der Status bleibt `NOT_QUALIFIED`. Vollständiges Log: `qualification.log`.
Die fehlgeschlagene Prüfung erreichte zunächst die erwarteten Assertions
für `DECODER_MEMORY_LIMIT` und den erhaltenen `ValueError`. Erst die
anschließende Erwartung `memory_limit_messages == [10]` erhielt `[]`.

## Lokalisierter Fehler der neutralen Bindung

`tests/test_s2oe_diagnostic.py:37` ersetzt `job.snapshot()` nur innerhalb
des Select-Aufrufs. Bei `:40` ist diese Ersetzung bereits aufgehoben.
`close()` kann einen weiteren echten Snapshot lesen; die echte neutrale
Windows-Jobinstanz hat keine Limitmeldung erzeugt. Damit wird die künstliche
Meldung durch deren leeren Bestand ersetzt. Die bisherige Fixture bildet
die dauerhafte Speicherung einer realen Jobmeldung in `DecoderJob.limit_messages`
nicht nach. Ein tatsächlicher Diagnoseverlust bei einer realen Limitmeldung
ist dadurch weder bestätigt noch ausgeschlossen.

Kleinste vorgeschlagene Korrektur: die synthetische Jobmeldung konsistent
über den vollständigen kontrollierten Abschluss erhalten; Fehler-Snapshot
und Abschluss-Snapshot getrennt prüfen. Keine Lockerung der Assertion und
keine Produktkorrektur allein aufgrund dieses Fixturefehlers. Noch nicht umgesetzt.

## Stopp und Bilanz

Der vorgesehene reale Aufruf `select(1, 0)` wurde **nicht gestartet**.
Keine Diagnose-Verbrauchsdatei, kein Medienzugriff, keine Rezeptor-, NJ-,
Feld-, Memory- oder Runtimeverarbeitung. Folglich auch keine unabhängige
Prüfung eines realen Diagnosebelegs. Kein Retry; keine Gates geöffnet.
Der historische Videolauf bleibt unverändert `NOT_EVALUABLE`.

Vorbindung einschließlich Quellenstand und Reserven: 118.314 Byte.
Aktive sechs Dateien: 42.619 Byte; historische gemeinsame Quellenbindung:
10.159 Byte. Erzeugte Dateien vor diesem Bericht: 3.778 Byte
(Bindung 2.192, Claim 5, Ergebnis 162, vollständiges Log 1.419).
Zusammen 56.556 Byte vor Bericht. Berichtreserve 8.192 Byte bleibt enthalten;
keine Rohmedien zählen als neu erzeugte Diagnoseablage.

Historische Quellenzulassungen werden durch die geänderten Worker-/Decoder-
Hashes nicht erneuert. Die neue Bindung gilt nur für diesen Diagnoseanschluss,
nicht für einen neuen Player- oder Lernlauf.

**RÜCKMELDUNG ERFORDERLICH:** enge Fixturekorrektur und neue einmalige neutrale
Qualifikation freigeben. Bis dahin bleibt der reale Diagnoseaufruf gesperrt.
Die konkrete Fehlerphase des MP4-Decoders ist weiterhin unbelegt.
