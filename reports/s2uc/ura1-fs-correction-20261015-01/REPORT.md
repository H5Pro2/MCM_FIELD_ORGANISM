# URA1: getrennte Korrektur der Dateierfassung und Supervisorfehlerdiagnose

Status PASS_FS_CORRECTION. Technische Korrektur, keine Forschungsfreigabe. Kein Forschungsstart, Retry, Resume, großer Policy-Lauf oder neue Forschungsquelle. V3-Quellen bleiben unveränderte Abbruchbelege; ihre weitere Behandlung ist nicht entschieden.

## Ursache und vollständige Pfadprüfung

Im tatsächlich verwendeten V3-Pfad ruft launch den Supervisor mit ReservedLedger auf. ReservedLedger.check liest zunächst Dateikategorien mit iterdir/is_file/stat, danach Ledger.check nochmals über rglob/is_file/stat. Dort erfolgen getrennte stat-Aufrufe für Gesamtexport, temporäre Bytes und Kategorien. Eine Workerumbenennung zwischen Auflistung und stat lässt einen zuvor vorhandenen Partialpfad verschwinden. Das endgültige Ziel kann bereits vorhanden sein und trotzdem scheitert die Erfassung am alten Namen.

Dasselbe Muster betrifft ReservedLedger.write (Export-/Kategorievorausprüfung) und die register-/write-Pfade des Basisledgers. Terminal.__init__ und prepare_v3.treebytes besitzen ebenfalls getrennte Existenz-/Größenabfragen; die Terminalzulassung erfolgt zwar vor Workerstart, die Vorbereitung ist im Forschungsfall statisch, sie werden für die neue Komponente dennoch über denselben konsistenten Erfassungspfad abgedeckt. Die neutralen Budget-Fault-Hooks in prepare_v3 berechnen Füllmengen ebenfalls aus getrennten stat-Aufrufen; sie sind keine Forschungslogik und werden nicht in das neue Korrekturpaket übernommen. Der alte Closurehash-Aufbau erfolgt erst nach Workerende und ist unter dieser Ein-Schreiber-Grenze nicht derselbe Konkurrenzfall. Arm-/Archivcode und execute-Cleanup ändern sich nicht.

F01 reproduziert genau den problematischen Ablauf mit einem separaten neutralen Worker: Die Auflistung enthält neutral.json.partial; ein Handshake erzwingt danach die Umbenennung nach neutral.json; anschließend scheitert die historische list-then-stat-Operation mit FileNotFoundError. Der vollständige terminale Supervisorabschluss einschließlich Traceback ist gespeichert. Damit ist der Fehlermechanismus experimentell bestätigt. Die exakte historische V3-Fehlerzeile bleibt mangels damaligem Traceback nicht rekonstruierbar; es wird kein nachträglicher Stacktrace erfunden.

## Neue Implementierung und Integrationsgrenze

Neue Dateien: tools/_s2uc_ura1_fs_accounting_v4.py, tools/s2uc_ura1_fs_revision_probe.py und tests/test_s2uc_ura1_fs_accounting_v4.py. Historische Module, Einstieg, Bindungen und Laufartefakte unverändert.

inventory liefert eine gemeinsame Dateitabelle für Export, Temp und alle Kategorien. Eine vollständige Aufnahme enthält Pfad, Identität, Größe, Änderungszeit und Dateityp. Akzeptiert werden zwei aufeinanderfolgende identische vollständige Aufnahmen. Verschwindet ein erfasster Dateipfad, wird die ganze Aufnahme verworfen und neu begonnen: weder null Bytes für den verschwundenen Pfad noch Weiterrechnung mit einer unvollständigen Tabelle. Nach Umbenennung wird das finale Ziel mit neuer Kategorie erfasst. Neue Dateien, geänderte Größen und Entfernungen verändern die Vergleichstabelle und erzwingen eine weitere Aufnahme. Nach höchstens acht Aufnahmen entsteht ein expliziter INVENTORY_UNSTABLE-Abbruch; keine unbegrenzte Warteschleife. 4096 Einträge begrenzen die Tabelle. Andere stat-/list-/Typfehler werden nicht verschluckt.

Das neue Ledger benutzt diese eine Aufnahme für jede Budgetentscheidung sowie für Vorprüfung, Kategoriezuordnung und Registrierung. Vorausgeprüft werden Datei-, Kategorie-, Gesamtexport- und temporärer Platz; während des Schreibens zählt die Partialdatei zu Temp und Export, nach Veröffentlichung zur finalen Kategorie und weiter zum Export. treebytes verwendet denselben Erfassungspfad. Terminalzulassung zählt den unveränderten 16384-Byte-Slot bereits vor Belegung gegen Export und Abschlusskategorie. Alle bisherigen LIMITS bleiben unverändert.

Der neue Supervisor wird in sämtlichen Prozessproben tatsächlich mit diesem Ledger und einem parallel schreibenden neutralen Worker ausgeführt. Das Paket stellt eine korrigierte Dateierfassungs-/Diagnosekomponente bereit, keinen neuen Forschungseinstieg. Ein zukünftiger Forschungseinstieg muss diese Komponenten ausdrücklich binden; der historische V3-Aufruf wird nicht heimlich umgeleitet.

## Diagnosen und Abschluss

Nach bestätigtem Workerende wird dessen vorhandener erster Fehlerstand gelesen und erhalten. Supervisorfehler ergänzen Phase, Operation, betroffenen Pfad, Ausnahmetext, begrenzten Traceback und einen eindeutigen letzten Fehlerort mit Datei/Zeile/Funktion. Folgefehler überschreiben die erste Ursache nicht. Die erste Diagnose ist einschließlich JSON-Escaping auf 4096 Byte begrenzt; Fehlertexte und bis zu acht Folgefehler sind ebenfalls nach serialisierten Bytes begrenzt. Der Unicode-Grenztest prüft den tatsächlichen gespeicherten Datensatz. Diagnosebytes liegen innerhalb des unveränderten festen 16384-Byte-Terminalslots und zählen damit vollständig gegen Export und Abschlusskategorie; keine unbeschränkte Logdatei und kein neues Zusatzbudget.

Workerende, Datei-Cleanup und interner Cleanup bleiben getrennt. Die neutralen Dateiarbeiter haben keine Policyarme; der Supervisor behauptet deshalb keinen Arm-Cleanup. Alle geforderten Fehlerproben enden mit gespeichertem, zurückgelesenem terminal.json und bestätigtem Workerende. Das Speichern hängt weiterhin nicht vom bereits fehlgeschlagenen Ledgerpfad ab.

## Tests und gemessene Ressourcen

F01 historischer Ablauf mit deterministischer Umbenennung: erwarteter FileNotFoundError und vollständiger Terminalbeleg.
F02 gleicher Handshake mit neuer Erfassung: regulärer Abschluss, finales Ziel exakt 192 Byte Verwaltung, null Tempbytes.
F03 Entfernung genau zwischen Auflistung und stat: vollständige Neuerfassung, keine Phantombytes, regulärer Abschluss.
F04 Erstellung nach Auflistung: neue finale Datei exakt mitgezählt, regulärer Abschluss.
F05 echte Exportüberschreitung: terminaler budget:export-Abbruch.
F06 echte Verwaltungsüberschreitung: terminaler budget:admin-Abbruch.
F07 echte temporäre Überschreitung: terminaler budget:temp-Abbruch.
F08 injizierter PermissionError an der tatsächlichen stat-Schnittstelle: nicht ignoriert, Phase/Operation/Pfad/Traceback gespeichert.
F09 injizierter sonstiger E/A-Fehler an stat: ebenso terminal mit Diagnose.
F10 tatsächlicher neutraler Worker verändert die Datei vor jeder Größenaufnahme: exakt acht Handshakes, danach INVENTORY_UNSTABLE, vollständiger Terminalabschluss.
F11 Worker-Schreib-/Registrierungspfad: Quellen-, Verwaltungs-, Abschluss- und Tempzuordnung korrekt.
F12 Vorprüfung verhindert zusätzlichen Exportverbrauch und erhält den Terminalslot.
F13 maximale Unicode-Fehlertexte/Folgefehler: erste Ursache erhalten, Diagnose höchstens 4096 Byte, ganzer gespeicherter Terminaldatensatz innerhalb des Slots.
F14 Partial-zu-Final-Umbenennung: Gesamtbytes unverändert, Bytes vollständig von Temp zur finalen Kategorie verschoben.

Alle F01–F14 bestanden. Zehn abschließende Prozessproben zusammen 2.190495 s; höchster gemessener Kernel-Jobpeak 28057600 Byte bei unverändertem hartem 536870912-Byte-/Zwei-Prozess-Job. Frühere Entwicklungsproben vor Begrenzung der Unicode-Diagnose bleiben separat erhalten; final/ enthält die maßgeblichen Proben des endgültigen Codes. Kein großer oder wissenschaftlicher Qualifikationslauf wurde wiederholt.

Budgetfehler werden mit tatsächlichen neutralen Dateien oberhalb der jeweiligen Schranke ausgelöst, nicht durch falsche Rückgabewerte. Die große Datei wird mit truncate angelegt, nicht als großer Policy-/Speicherlauf. Erwartete Überschreitungen sind ausschließlich Fehlerstimuli; sie werden erkannt. Supervisor entfernt Tempbelege nach Workerende. Übergroße finale neutrale Testdateien werden erst nach gespeichertem Fehlerabschluss entfernt; evidence.json hält ihre tatsächlichen Größen und diese nachgelagerte Testbereinigung fest. Damit bleibt das ausgelieferte Korrekturpaket klein. Die künstlichen Steuerdateien liegen außerhalb des gemessenen neutralen Datenverzeichnisses und sind im ausgelieferten Gesamtinventar enthalten.

## Aussagegrenzen und historischer Schutz

Die Aufnahme ist eine begrenzt wiederholte, auf Stabilität geprüfte Sicht kooperierender Dateioperationen; sie ist kein Betriebssystem-Snapshot und kein Dateisystem-Lock. Nicht beansprucht wird die Erkennung jeder beliebig kurzen Überschreitung zwischen zwei Kontrollen oder adversarialer ABA-Änderungen. Diese Grenze bestand auch beim bisherigen pollenden Supervisor. Dauerhaft instabile Erfassung wird ausdrücklich abgebrochen statt als budgetkonform bestätigt. Final veröffentlichte Forschungsdateien müssen weiterhin unveränderlich bleiben. Permission-/E/A-Fehler werden gezielt injiziert; daraus folgt keine Prüfung real beschädigter Datenträger. Slot-Schreibfähigkeit und Betriebssystemantwort bleiben Voraussetzungen.

Alle 414 Dateien der V3-Vorstartbindung sind unverändert geprüft; sämtliche 37 Dateien der historischen V3-Abschlussübergabe stimmen mit deren Hashes überein. historical-preservation.json hält die Prüfung fest. Die drei aktuellen Übersichten sind in dieser V3-Bindung ungebunden und werden ausschließlich um den neuen technischen Stand ergänzt.

## Nächster Schritt

Projektleiter lässt dieses eng begrenzte Korrekturpaket technisch abnehmen. Erst danach entscheidet er über die weitere Behandlung der bereits erzeugten V3-Quellen und einen gegebenenfalls neu gebundenen Forschungseinstieg. Diese technische Korrektur autorisiert keinen weiteren Versuch.
