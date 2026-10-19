# Aktuelle Status- und Abbruchübergabe URA1-V2

Auftrag / Prüfpaket: c5ec9445-c4f4-4064-b09c-849e6117df44.
Stand: 2026-10-15. Diese ungebundene Standseinordnung dokumentiert ausschließlich den bereits beendeten Versuch und die inzwischen getroffenen Anschlussentscheidungen. Kein Start-, Retry- oder Resumeauftrag.

## Verbindlicher Status

Der historische Forschungsversuch bleibt TECHNICAL_ABORT; sein Start ist erfolgt und verbraucht. Die unabhängige technische Prüferabnahme des Korrekturpakets ist erfolgt: Paket 59477691-fe9f-4c08-8d03-50a861c4c844, Korrektur-SHA d93693d178f0f52938be9323a01fbaf681210e3fe8b1317b1af44a762faa9dd2. Der MCMKI Projektleiter hat die Korrektur übernommen, begrenzt auf die geprüften Fehlerpfade. Dies ist keine nachträgliche Forschungsabnahme des abgebrochenen Laufs. Die 32 vorhandenen Forschungsquellen bleiben historische Abbruchbelege; neue Forschungsquellen dürfen erst nach separater Forschungsbeauftragung erzeugt werden. Forschungsfreigabe weiterhin offen.

Die drei bisherigen Übersichten README.md, AKTUELLER_FORSCHUNGSWEG.md und docs/README.md sind inzwischen ausdrücklich in der Korrekturbindung d93693d178f0f52938be9323a01fbaf681210e3fe8b1317b1af44a762faa9dd2 enthalten. Sie werden auf diesem Auftrag nicht geändert. Diese separate aktuelle Standseinordnung ergänzt sie, ohne eine historische Bindung umzuschreiben.

## Nachvollziehbare Abfolge

1. START.json trägt consumed=true und den Forschungs-Vorstart-SHA 0c2f35cf2e6c6a68f6725fe9a71253efb70f757254019ada69f44d777ce05027. Dateizeit: 2026-10-15 00:47:00.435 UTC (02:47:00.435 Europe/Berlin). Diese Dateizeit ist Metadatenbeleg, kein unabhängig signiertes Ereignisprotokoll.
2. Nach dem Start wurden 32 Quelldateien und Fallbelege erzeugt. Die aktuelle Prüfung hat keine Quellen- oder Archivinhalte leistungsbezogen ausgewertet.
3. Der vorherige weitergeleitete Projektleiterauftrag stellte wegen des bestätigten Abschlussfehlers die Abnahme zurück und verlangte ausdrücklich, einen noch laufenden Versuch zu beenden. Ein genauer Empfangszeitpunkt dieses Auftrags ist in den untersuchten Laufdateien nicht dokumentiert.
4. Die damalige Prozessprüfung im Chat zeigte Supervisor PID 13444 und Worker PID 13188 noch aktiv. Anschließend wurde der autorisierte Befehl Stop-Process -Id 13188 -ErrorAction Stop ausgeführt und erfolgreich beendet. Dies ist der unmittelbare Beendigungsnachweis aus dem Werkzeugprotokoll; interruption.json hält diese Abfolge zusätzlich fest.
5. Der vorhandene Supervisor beendete seinen Abschlussweg selbst. result.json wurde um 02:31:55.501 UTC, closure.json um 02:31:55.872 UTC geschrieben (lokal jeweils 04:31:55). Gesamtdauer laut result.json 6295.247787699998 Sekunden. Status TECHNICAL_ABORT, worker_terminated=true, WORKER_EXIT:4294967295, retry_allowed=false und authorization_consumed=true.
6. Die erneute lesende Prozessabfrage findet keinen Python-Prozess mit s2uc_ura1-Aufruf. Zusammen mit dem damaligen Ende beider PIDs und dem Supervisorbeleg bestätigt dies den beendeten Versuch.

Einordnung: Der Abbruch geht nach Auftrag, Werkzeugprotokoll und Unterbrechungsbeleg auf die angeordnete Beendigung zurück. WORKER_EXIT ist deren technische Folge, kein ausreichender eigenständiger Ursachennachweis. Ein tatsächliches Erschöpfen des Exportbudgets in diesem Versuch ist damit nicht belegt. Dass result.json und closure.json diesmal geschrieben wurden, widerlegt oder behebt den beanstandeten Budget-Abbruchpfad nicht.

## Bearbeitungsstand und Beweisgrenzen

- Vorhanden: 25 Archive case-01 bis case-25 und 25 Erfassungsmanifeste; keine Belege zu case-26.
- Der gebundene sequenzielle Ablauf erreicht case-25 erst, nachdem Fälle 1–24 einschließlich unabhängiger Archivprüfung und Cleanup erfolgreich zurückgegeben haben. Daraus folgt die dokumentierte Untergrenze von 24 abgeschlossenen Fällen.
- Es fehlen eigenständige persistente Abschlussquittungen pro Fall sowie worker.json. Die Untergrenze ist deshalb ein Kontrollflussnachweis anhand gebundenen Codes und vorhandener Folgeartefakte, keine neue Einzelabnahme sämtlicher Archive. Die aktuelle Prüfung hat keine Archive erneut decodiert.
- Fall 25: Archiv und Erfassungsmanifest vorhanden; letzter Archivzeitpunkt 02:31:28.292 UTC. Seine nachgelagerte Prüfung und sein Cleanup sind nicht abschließend belegt.
- Ob bereits Fall 26 begonnen hatte, ist unbekannt. Das Fehlen seiner Datei beweist keinen fehlenden Beginn. Exakte Anzahl vollständig abgeschlossener Fälle bleibt unbekannt und wird nicht als null ausgewiesen.
- closure.json enthält 87 Dateieinträge. Alle 87 SHA-256-Werte stimmen bei der lesenden Prüfung mit den vorhandenen Dateien überein. Das belegt Dateiintegrität zum Abschluss, keine Vollständigkeit der unterbrochenen Forschung.

## Getrennter Cleanupstatus

Workerende: bestätigt durch result.json und Prozessprüfungen. Supervisorende: bestätigt durch damalige PID-Prüfung und erneute Prozessabfrage.

Datei-Cleanup: keine *.partial-Dateien im Laufverzeichnis vorhanden. Alle vorhandenen Forschungsbelege bleiben erhalten; keine nachträgliche Bereinigung oder Änderung durch diesen Auftrag.

Arm-/Store-Cleanup: für den unterbrochenen Fall unbestätigt. Kein Workerbericht und keine persistente letzte Cleanupquittung. Prozessende und Freigabe von Betriebssystemressourcen ersetzen keinen Nachweis ausgeführter interner Cleanup-Routinen. Für Fälle 1–24 besteht nur der oben erläuterte sequenzielle Kontrollflussnachweis.

## Belege

- Laufmarker: reports/s2uc/ura1-comparison-v2-time16h/START.json
- Supervisorergebnis: reports/s2uc/ura1-comparison-v2-time16h/result.json
- Abschlussmanifest: reports/s2uc/ura1-comparison-v2-time16h/closure.json
- Fallbelege: reports/s2uc/ura1-comparison-v2-time16h/case-01 bis case-25, jeweils .delta.json.gz und -capture.json
- Unterbrechungsgrund, Prozess-IDs und gesichertes Inventar: reports/s2uc/ura1-terminal-repair-20261015-01/interruption.json
- Bisherige getrennte Korrekturübergabe: reports/s2uc/ura1-terminal-repair-20261015-01/REPORT.md und prestart.json; unabhängige technische Prüferabnahme in Paket 59477691-fe9f-4c08-8d03-50a861c4c844 und Übernahme durch den Projektleiter erfolgt, begrenzt auf die geprüften Fehlerpfade.
- Beendigungsauftrag und erfolgreich ausgeführter Stop-Process-Befehl: vorangegangener Projektleiterauftrag und Werkzeugprotokoll dieses Entwicklerchats.

## Anschlussentscheidung

Die technische Korrekturabnahme und die Quellenentscheidung sind getroffen; daraus entsteht keine erneute Abnahmeschleife zum Korrekturpaket. Maßgeblich ist der bestehende Auftrag zur neuen vollständigen Vorbereitung. Diese wurde inzwischen als PASS_PREPARATION_V3 mit Integrationsprüfungen und Vorstart-SHA e774d87d8a3df55eaa5e68142d3ca69d8dbfdc979fbdb99731e803c68b412382 geliefert (reports/s2uc/ura1-v3-preparation-20261015-01/REPORT.md). Die gesonderte Forschungsentscheidung bleibt offen. Vorhandene Quellen werden nicht wiederverwendet; neue Quellen bleiben bis zur separaten Forschungsbeauftragung unerzeugt. Kein Retry oder Resume des historischen Starts. Diese Synchronisation erweitert oder erneuert keinen Ausführungsauftrag.

Auf diesem Auftrag ausschließlich lesende Prüfung und diese neue ungebundene Statusdatei. Keine Codeänderung, kein Testlauf, keine Policy-Ausführung, keine Leistungswertung und keine Änderung historischer Bindungen oder Laufartefakte.
