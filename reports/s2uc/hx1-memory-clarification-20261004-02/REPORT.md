# HX1: technische Abschlussauswertung der Speichergrenze

Stand 2026-10-04. Auswertung der bereits vorhandenen neutralen Messungen
`hx1-memory-clarification-20261004-01` und `-02`; keine erneute Ausführung
dieser Proben, kein weiterer vollständiger Größenablauf, kein Forschungsstart.

## Urteil

Die gemeinsame Commit-Grenze von 536.870.912 Byte (512 MiB) wird im geprüften
Windows-Pfad durchgesetzt. Der historische Wert 687.595.520 Byte ist der rohe
Windows-Höchststand `PeakJobMemoryUsed`. Er belegt hier nicht, dass dem Worker
687.595.520 Byte erfolgreich bereitgestellt wurden. Die vorhandenen gezielten
Messungen zeigen, dass auch ein abgewiesener Commit-Antrag diesen Höchststand
erhöht. Eine Änderung des Produktionscodes oder der Grenzwerte ist nicht nötig.
Die technische Abnahme durch den Projektleiter und der Forschungsstart bleiben
getrennte Entscheidungen; diese Auswertung erteilt keine Forschungsfreigabe.

## Welches Feld wurde gemessen?

`tools/_s2uc_hx1_windows.py` fragt mit `QueryInformationJobObject`, Klasse 9
(`JobObjectExtendedLimitInformation`), die Struktur
`JOBOBJECT_EXTENDED_LIMIT_INFORMATION` ab. Das JSON-Feld
`peak_job_committed_bytes` enthält unverändert deren `PeakJobMemoryUsed`;
`peak_process_committed_bytes` enthält `PeakProcessMemoryUsed`.
Es handelt sich weder um RSS noch um eine aktuelle Commit-Summe.

Das aufgezeichnete 64-Bit-Layout ist konsistent: Basic 64, IO 48, Extended 144
Byte; ProcessMemoryLimit an Offset 112, JobMemoryLimit 120,
PeakProcessMemoryUsed 128 und PeakJobMemoryUsed 136. Prozesszählerstruktur:
80 Byte; MEMORY_BASIC_INFORMATION: 48 Byte. Kein Hinweis auf eine vertauschte
Struktur oder ein falsch gelesenes Feld.

Microsoft beschreibt PeakJobMemoryUsed als bisherigen Höchststand aller
zugeordneten Prozesse und JobMemoryLimit als Grenze des gemeinsam committeten
Speichers. Die Dokumentation erklärt die hier beobachtete Berücksichtigung
fehlgeschlagener Commit-Anträge im Peak nicht ausdrücklich. Diese Aussage ist
daher ein lokaler Messbefund, keine behauptete allgemeine API-Garantie.
[Microsoft: Extended Limit Information](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information).

## Gesetzte Grenze und gemeinsame Mitgliedschaft

In sämtlichen gespeicherten Phasen aller sechs Proben wurden vom konkreten
Job-Handle zurückgelesen: LimitFlags = 512 = 0x200
(`JOB_OBJECT_LIMIT_JOB_MEMORY`), JobMemoryLimit = 536.870.912,
ProcessMemoryLimit = 0. Damit ist die gemeinsame Job-Grenze aktiv; es wurde
kein gesondertes Prozesslimit als Ersatz verwendet. Das Flag lässt Commit-
Anträge oberhalb der gemeinsamen Grenze scheitern und ist keine bloße
Benachrichtigungsschwelle.
[Microsoft: Basic Limit Information](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information).

`IsProcessInJob` wurde für Supervisor und Worker mit demselben konkreten
Job-Handle erfolgreich geprüft, zusätzlich die PID-Liste über Klasse 3:

| Vorhandene Probe | Supervisor | Worker native / python / aggregate |
| --- | ---: | --- |
| 01 | 6932 | 8748 / 13008 / 14740 |
| 02 | 2712 | 12344 / 8808 / 7552 |

Jede Job-Liste enthält genau den jeweiligen Supervisor und Worker. Die Proben
verwenden die unveränderte produktive Installation `install(fresh=True)`.
Auch der produktive Supervisor prüft den Worker mit seinem konkreten Job-Handle
(`verify_worker`). Die historischen Abschlussdaten enthalten nicht diese
vollständigen PID-Listen; die ergänzenden Proben liefern den expliziten Nachweis
für denselben Installationspfad, keine nachträgliche historische PID-Messung.

## Vorhandene gezielte Prüfergebnisse

Alle sechs gespeicherten Prozesse endeten mit Exitcode 0; native und aggregate
erreichten nach Ablehnung auch die kleine erfolgreiche 4-MiB-Recovery und
Freigabe. Python meldete jeweils die erwartete MemoryError-Ablehnung.

| Probe | Antrag Byte | Job-Peak nach Antrag | Ergebnis |
| --- | ---: | ---: | --- |
| 01/native | 629.145.600 | 666.308.608 | NULL, Fehler 1455, gesamter Bereich MEM_RESERVE |
| 01/python | 629.145.600 | 668.127.232 | MemoryError, aktuelle PrivateUsage unverändert |
| 01/aggregate | 508.190.720 | 545.259.520 | NULL, Fehler 1455, gesamter Bereich MEM_RESERVE |
| 02/native | 629.145.600 | 665.399.296 | NULL, Fehler 1455, gesamter Bereich MEM_RESERVE |
| 02/python | 629.145.600 | 666.832.896 | MemoryError, kein entsprechender PrivateUsage-Anstieg |
| 02/aggregate | 508.211.200 | 544.894.976 | NULL, Fehler 1455, gesamter Bereich MEM_RESERVE |

Besonders eindeutig ist 01/native: vor dem Antrag Job-Peak 37.163.008 Byte,
danach 666.308.608 = 37.163.008 + 629.145.600 Byte. PrivateUsage des Workers
bleibt vor/nach dem Versuch exakt 21.934.080 Byte. VirtualAlloc gibt NULL
zurück; VirtualQuery meldet die gesamte Länge 629.145.600 mit State 8192
(MEM_RESERVE), Protect 0. Der Antrag wurde nicht als nutzbarer Commit geliefert.
Ein folgender 4-MiB-Commit gelingt; nur dieser Teil hat anschließend MEM_COMMIT.

01/aggregate trennt die gemeinsame Grenze von einer hypothetischen Einzelgrenze:
Supervisor 15.228.928 + Worker 21.839.872 Byte vor dem Antrag. Mit Antrag
508.190.720 wäre Worker allein bei 530.030.592 < 536.870.912 Byte, beide zusammen
bei 545.259.520 > 536.870.912 Byte. Trotzdem wird der Antrag abgewiesen; der
Worker-Commit bleibt unverändert. Das belegt die Wirkung auf die gemeinsame Summe.

02 ergänzte bereits vor dieser Abschlussauswertung die systemweite Commit-
Verfügbarkeit unmittelbar vor dem jeweiligen Antrag: native 8.731.443.200,
python 8.728.961.024, aggregate 8.726.810.624 Byte. Alle Werte liegen weit über
dem Antrag. Eine allgemeine Commit-Erschöpfung ist somit keine durch die
Messungen gestützte Erklärung. Diese Momentaufnahmen sind keine atomare
Aufzeichnung aller systemweiten Aktivitäten. Kleinere PrivateUsage-Schwankungen
in 02 sind dokumentiert; es wird dort keine exakte Vorher/Nachher-Gleichheit behauptet.

MEM_RESERVE reserviert Adressraum, MEM_COMMIT belastet das Commit-Konto;
physische Seiten werden erst bei Zugriff bereitgestellt. PrivateUsage misst
aktuellen privaten Commit. Auch PeakPagefileUsage stieg bei den abgewiesenen
Anträgen an und ist deshalb hier kein Ersatzbeleg für erfolgreich gelieferten
Speicher. Quellen:
[VirtualAlloc](https://learn.microsoft.com/en-us/windows/win32/api/memoryapi/nf-memoryapi-virtualalloc),
[Prozesszähler](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters_ex),
[System-Commit](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-performance_information).

## Einordnung des historischen Peaks 687.595.520 Byte

Der historische Fehlerfall beantragte bytearray(629.145.600), dokumentierte
`allocation_rejected: true` und schloss mit `NOT_EVALUABLE`, Worker-Exitcode 1,
`worker_alive: false`, `resume_permitted: false`. Der Roh-Peak liegt
150.724.608 Byte über der Grenze. Er wird unverändert erhalten und nicht als
erfolgreiche Einhaltung eines Peak-Grenzwertes umetikettiert.

Die vorhandenen Proben reproduzieren sowohl nativ als auch mit Python denselben
scheinbaren Widerspruch: abgewiesener Antrag bei einem Roh-Peak über dem Limit.
Im historischen Fehlerfall fehlen unmittelbare PrivateUsage-/VirtualQuery-
Messungen. Seine exakte interne Zusammensetzung lässt sich deshalb nicht
rückwirkend beweisen. Ebenso wird keine interne Reihenfolge der Windows-
Kernelbuchung behauptet. Belastbar sind Feldzuordnung, dokumentierte Ablehnung,
korrekter Fehlerabschluss und die direkte Reproduktion der Peak-Wirkung.

Die bestehende zusätzliche Abschlussregel verwirft jeden Lauf mit Roh-Peak
über der Grenze. Sie bleibt konservativ erhalten. Der vollständige erfolgreiche
neutrale Größenablauf hatte 132.042.752 Byte Job-Peak und bleibt unter dem Limit.
Die Vereinbarung wird als Grenze erfolgreich bereitgestellten gemeinsamen
Commits durchgesetzt; ein Roh-Peak oberhalb der Grenze im absichtlichen
Ablehnungstest ist kein erfolgreicher Ressourcenlauf.

## Änderungen, Bindung und Anschluss

Keine Produktionskorrektur, keine Änderung an Limit, Abschlussregel,
Forschungsquelle, Auswertung, U oder A1/K1. Der diagnostische Probe-Code und seine
beiden bereits ausgeführten Fassungen werden mit den sechs Rohmessungen in
einer separaten Ergänzungsbindung gesichert. Die erste Quellenkopie existierte
bereits; die zweite wird zum Abschluss aus der verwendeten Diagnosefassung
gesichert. Diese Archivkopie ist keine neue Ausführung.

`python -m tools.s2uc_hx1 check` wurde ausschließlich zur lesenden
Bindungsprüfung ausgeführt: `PASS_HX1_PRESTART_NO_RESEARCH`, Exitcode 0.
Die ursprüngliche Codebindung mit 139 Dateien und Vorstartbindung bleiben
unverändert; keine neue produktive Vorstartversion erforderlich:

- Codebindung SHA256: `66dfca57e696747b9125333f58666afab7dd23745c69ba0a78deea7250e1bf1c`.
- Vorstartbindung SHA256: `e8cb8f935d28a5624239aafdbab75d0cb8246b665045442afcc9ec4a8931d36e`.
- Ergänzung: `docs/S2UC_HX1_SPEICHERGRENZE_ERGAENZUNGSBINDUNG_20261004.json`.
- Lesende Ergebnisprüfung: `verification.json` neben diesem Bericht.

Die Ergänzung ersetzt nicht die Vorstartbindung und wird vom bisherigen
Starter nicht automatisch als neue Autorisierung konsumiert. Historische
Fehlerbelege, Qualifikationsarchiv und Vorbereitungsbericht bleiben unverändert.

Empfehlung an den Projektleiter: technischen Speicherpunkt anhand dieser
Ergänzung schließen und über die technische Abnahme entscheiden. Erst danach
kommt eine gesonderte Einmalbeauftragung des gebundenen Forschungsdurchlaufs
in Betracht. Kein weiterer technischer Blocker aus diesen Speicherbefunden;
Forschungsstart bis zur Entscheidung weiterhin gesperrt.
