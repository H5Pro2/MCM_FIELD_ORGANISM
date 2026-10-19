# URA1-V3: vollständiger technischer Abbruchabschluss

Status TECHNICAL_ABORT. Genau ein autorisierter Aufruf ausgeführt. Kein Retry, Resume, Ersatzfall oder Tuning. Vorstart-SHA e774d87d8a3df55eaa5e68142d3ca69d8dbfdc979fbdb99731e803c68b412382; Freigabe nach START verbraucht.

## Start und maßgeblicher Abschluss

Unmittelbar vor Start sämtliche 414 Datei-, Runtime-, Aufruf-, Namensraum- und Grenzbindungen erfolgreich geprüft. Zielverzeichnis und Berechtigung fehlten. Danach passende URA1_RESEARCH_ONCE_V3-Berechtigung exklusiv erstellt und genau der gebundene Aufruf gestartet. START.json mit consumed=true und 16384-Byte-Terminalreserve vor Forschungsarbeit angelegt.

START-Dateizeit 2026-10-15 02:48:27.569 UTC; terminal.json-Dateizeit 02:48:31.724 UTC. Dateizeiten sind Metadaten, keine unabhängigen Zeitatteste. Globale monotone Dauer im maßgeblichen Supervisorbeleg: 4.396087399996759 Sekunden.

terminal.json: TECHNICAL_ABORT; erste Ursache FileNotFoundError / WinError 2 beim Zugriff auf sources-manifest.json.partial. Keine aufgezeichneten Folgefehler. worker_ended=true, worker_exitcode=1. Kein externer Stopauftrag und kein manuelles Stop-Process in diesem Versuch: Der gebundene Supervisor beendet den Worker nach seinem Prüfpfadfehler selbst. Nachprüfung findet keinen laufenden Pythonprozess dieses V3-Einstiegs.

worker.json, result.json, closure.json und statistics.json fehlen. terminal.json ist wie vereinbart der maßgebliche gespeicherte Supervisorabschluss. Das separat hinzugefügte delivery-closure.json sichert lediglich diese Abschlussübergabe und vorhandene Dateien; es ersetzt weder den fehlenden regulären Laufabschluss noch eine Forschungsabnahme.

## Quellen- und Fallstand

32 neue Quellen unter MCM-URA1/source/v3 und sources-manifest.json vorhanden. Manifest enthält 32 Einträge, all_before_policy=true und den korrekten Namensraum. Alle 32 gespeicherten Dateihashes stimmen mit dem Manifest überein. Nach gebundenem Workerablauf wurden die Quellen vor dem Manifest einzeln unabhängig geprüft. Die nachträgliche Kontrolle prüfte ausschließlich Hashes und Metadaten, keine neue Quellenrekonstruktion oder leistungsbezogene Besichtigung.

completed_cases=[]: null quittierte Fälle. active_case=null: kein aktiver Fall im letzten gespeicherten Terminalstand. Keine Fallarchive oder Erfassungsmanifeste. Ein begonnener Policyfall ist nicht belegt; der tatsächliche interne Fortschritt bis zur Prozessbeendigung wird darüber hinaus nicht behauptet. Die 32 Quellen gelten nun als bereits erzeugte Forschungsquellen dieses abgebrochenen Versuchs. Keine Wiederverwendung oder neue Quellenentscheidung aus diesem Abschluss ableiten. Historische V2-Quellen und Teilarchive wurden nicht verwendet oder ergänzt.

## Ergebnis und Aussagegrenzen

Primärkontrast U−R: NICHT AUSWERTBAR. Nominales 95%-Intervall: NICHT BERECHENBAR. Ergänzende Q/G_all/S/Q_X/Q_Y-Bilanzen und Diagnosen: NICHT AUSWERTBAR. Es gibt keine vollständige Serie und keine statistische Ergebnisdatei. Keine Teilmengenwertung, keine Aussage zur Überlegenheit von U oder R und kein wissenschaftliches Nullergebnis.

Workerende bestätigt. Datei-Cleanup bestätigt: keine verbliebenen Partialdateien. Interner Arm-/Store-Cleanup bleibt gemäß terminal.json UNCONFIRMED; weder Prozessende noch ein fehlender aktiver Fall beweisen ausgeführte interne Cleanup-Routinen.

## Ressourcen und Integrität

Harter gemeinsamer Job: 536870912 Byte; gemessener Jobpeak 44756992 Byte, Prozesspeak 31920128 Byte. Kein belegtes Zeit- oder Speicherlimitereignis. Globalbudget 57600 s, Workerbudget 54000 s und übrige Grenzen unverändert. Vor dieser zusätzlichen Abschlussdokumentation: Vorbereitung inklusive Berechtigung 4469075 Byte; Laufverzeichnis 219273 Byte, zusammen 4688348 Byte. Die abschließende Kategorie-/Exportkontrolle umfasst auch diesen Bericht und delivery-closure.json und bleibt unter allen Grenzen.

Vorstartbindung nach Abbruch erneut vollständig gültig. Gebundene Dateien, Marker, Quellen, Manifest und Terminalbeleg nicht verändert. Alle neuen Quellenhashes geprüft; keine Archive vorhanden, daher keine nachträgliche Archivintegritätsbehauptung. Die Vorbereitungstests werden durch diesen echten Laufbefund nicht zu einer bestandenen Forschungsserie.

## Technische Einordnung und nächster Vorschlag

Beobachtung: Supervisorfehler nennt eine nicht mehr vorhandene Manifest-Partialdatei; das endgültige Manifest ist vorhanden. Gebundener Code erfasst Dateien und fragt deren Größe in getrennten Schritten ab, während der Worker Partialdateien umbenennt. Ein konkurrierendes Umbenennen zwischen Erfassung und stat ist deshalb eine durch Code und Artefakte gestützte Ursachenhypothese. Ein vollständiger Traceback wurde nicht gespeichert; eine exakte Fehlerzeile ist nicht belegt.

Empfehlung: separat begrenzter Entwicklungsauftrag für konsistente beziehungsweise gegen konkurrierendes Umbenennen abgesicherte Budgeterfassung und aussagekräftige Supervisorfehlerbelege. Die Korrektur muss echte Grenzüberschreitungen weiterhin erkennen und mit kurzen neutralen gleichzeitig schreibenden Workern geprüft werden. Kein automatischer Neustart; auch nach technischer Korrektur sind die nun erzeugten V3-Quellen und der verbrauchte Start ausdrücklich in einer neuen Entscheidung zu berücksichtigen.
