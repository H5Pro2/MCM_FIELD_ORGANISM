# URA1-V4: vollständiger integrierter Vorbereitungsabschluss

Workflow-Auftrag 736878d8-1036-4029-8dc3-e659e5cbb722. Status PASS_PREPARATION_V4. Kein Forschungsstart. Die gesonderte Forschungsentscheidung bleibt offen.

## Gelieferte Dateien und Integration

Neue Dateien: tools/s2uc_ura1_prepare_v4.py, tools/_s2uc_ura1_v4_sources.py, tools/_s2uc_ura1_v4_source_reference.py, tests/test_s2uc_ura1_prepare_v4.py. Aktuelle ungebundene Übersichten README.md, AKTUELLER_FORSCHUNGSWEG.md und docs/README.md aktualisiert. Statische Berichte und Nachweise im vorliegenden Vorbereitungspaket.

Der neue tatsächliche Worker-/Supervisorpfad verwendet unmittelbar Terminal, Ledger, inventory, treebytes und supervise aus dem abgenommenen Modul _s2uc_ura1_fs_accounting_v4. Die Komponente selbst wurde nicht verändert. Fallquittungen stammen weiterhin aus execute_with_receipts; echte U/R-Arme, Referenz-/Bestands-/Ticket-/Zell-/Hypothesenprüfungen, Erfassungsanker und unabhängiger Decoder laufen unverändert über policy_case. Keine Workerattrappe ersetzt die Integrationsfälle.

IntegratedLedger ergänzt ausschließlich Messzähler und eindeutig auf neutrale Modi begrenzte Fehlerhooks. Im Forschungsmodus sind sie deaktiviert, ebenso der neutrale Supervisor-Handshake. Alle Export-/Kategorie-/Tempvorprüfungen, Aufnahme-/Registrierungspfade, Vorbereitungsgrößen und der Closure-Dateibestand verwenden den neuen gemeinsamen Erfassungspfad. Finale Dateien werden nach bestätigtem Workerende gehasht. Closure schließt den danach abschließend geschriebenen maßgeblichen terminal.json aus; beide Belege sind getrennt zu beurteilen.

Der feste 16384-Byte-Terminalslot wird vor Workerzulassung innerhalb Export-/Abschlussbudget reserviert. Erste Ursache und begrenzte Diagnose enthalten Phase, Operation, Pfad, Traceback und eindeutigen Fehlerort. Workerende, Datei-Cleanup, interner Cleanup, quittierte Fälle und aktiver Fall werden getrennt gespeichert. Fehlerdiagnosen werden nicht nachträglich zu bestätigtem Cleanup umgedeutet.

## Vorab festgelegte Quellenentscheidung

Neuer Forschungsnamensraum MCM-URA1/source/v4. Neues exklusives Ziel reports/s2uc/ura1-comparison-v4-consistent16h. Zielordner und authorization.json fehlen weiterhin. Keine V4-Forschungsquellen erzeugt oder besichtigt. V3-Quellen bleiben ausschließlich historische Abbruchbelege; keine Wiederverwendung, kein Pooling, keine Fortsetzung. V2/V3-Marker bleiben verbraucht.

Quellenrezept unverändert, ausschließlich neuer Namensraum und neuer Admissionimport: 32 Geschichten, 1024 Frames je Geschichte, 16 je Orientierung, dieselben drei Streams und Kontingenzen. Die unabhängige Referenz wird entsprechend separat umgestellt. N03 prüft die exakten erlaubten Quelltextänderungen. Vor zukünftiger erster Policy werden alle 32 Quellen unabhängig geprüft und mit Manifest versiegelt.

U/R-Verfahren, Primärkontrast D:U-R mit allen 256 Q-Zielen je Geschichte, ergänzende Bilanzen, rationale Weiterverarbeitung gespeicherter binary64-MAE, 10000 geschichtete Paarziehungen und nominales 95%-Intervall bleiben unverändert. Bootstrapmatrix bytegleich übernommen: 320000 Byte, SHA 0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965. Keine neue Matrix oder Suche nach Ziehungen.

## Konkrete Integrationsprüfungen

I01 regulärer Abschluss: zwei Achtframe-Handfälle, vier frische verschiedene U/R-Arme. Je Arm und Fall 24 äußere Ereignisse, 92 interne Ereignisse, vier Prognosen und drei beobachtete Ziele. Beide Archive PASS_DELTA_INTEGRITY, vollständige Quittungen [1,2], aktiver Fall null, interner und Datei-Cleanup bestätigt. Worker/result/closure/terminal gespeichert; sämtliche Closurehashes geprüft. Dauer 2.186398 s.

I02 deterministische Umbenennung: Bei echtem Armstart im zweiten Fall schreibt der Worker eine neutrale Partialdatei. Der Supervisor stoppt seine Aufnahme nach der Auflistung und signalisiert genau dann die Umbenennung; der Worker quittiert sie, erst danach setzt die Größenaufnahme fort. Ein Handshake belegt die Position zwischen Auflistung und Größenabfrage. Finales Ziel erkannt, beide U/R-Fälle mit Decoderprüfung und Cleanup abgeschlossen. Dauer 2.109576 s. Keine pauschale Behandlung als null Bytes; das unveränderte F02 ergänzt den exakten Größen-/Kategoriennachweis.

I03 Exportüberschreitung, I04 Verwaltungsüberschreitung, I05 Tempüberschreitung: jeweils erster realer Achtframefall vollständig quittiert, zweiter Fall mit tatsächlichem Armstart aktiv. Neutrale Dateien überschreiten die jeweilige echte Bytegrenze um mindestens ein Byte. Der Fehler wird vom integrierten Worker-Ledger erkannt und einschließlich Diagnose gesichert. Drei tatsächliche Arme angelegt; interner Cleanup bestätigt. Der reguläre Workerbericht kann wegen des weiterhin belegten Budgets nicht gespeichert werden; terminal.json wird dennoch vollständig geschrieben. Workerende und Datei-Cleanup bestätigt. Erster Fehler bleibt budget:export, budget:admin beziehungsweise budget:temp, Folgefehler ersetzen ihn nicht.

Die Budgetproben synchronisieren den Supervisor während der Injektion bis zur gesicherten Workerfehlerdiagnose. Das ist ein ausschließlich neutraler Testhook, um Cleanup und erstes Workerereignis deterministisch zu prüfen, kein Verhalten im Forschungsmodus. Export-/Temp-Proben belegen vor dem Bericht erneut eine Partialdatei, weil execute() die erste bereits beim Cleanup entfernt hat. Verwaltungstestdatei bleibt als neutraler Größenbeleg erhalten. Beabsichtigte Überschreitungen sind Fehlerstimuli, keine Forschungsbudgeterweiterung.

I06 dauerhaft instabile Erfassung: nach quittiertem Fall 1 und tatsächlichem Armstart in Fall 2 erzwingt ein Handshake eine Änderung bei jeder Aufnahme. Exakt acht Handshakes, dann INVENTORY_UNSTABLE im Supervisor. Workerende und Datei-Cleanup bestätigt; interner Cleanup UNCONFIRMED. Dauer 1.376521 s.

I07 Workerfrist: gleiche Fortschrittsgrenze [1], aktiver Fall 2; neutraler Worker wartet. Supervisor setzt verkürzte neutrale Prüffrist von acht Sekunden durch. Maßgeblicher Terminalabschluss nach 8.028306 s, Workerende bestätigt, interner Cleanup UNCONFIRMED. Forschungsfrist unverändert 54000 s.

I08 Erfassungsaufwand unter neutraler Dateilast: zwei weitere Achtframefälle mit 104 kleinen neutralen Metadatendateien im selben Budgetverzeichnis. Vier U/R-Arme, beide Decoderprüfungen, Quittungen und Cleanup bestanden. 87 Workerprüfungen: insgesamt 2.123767 s Erfassungszeit; 123 Supervisorprüfungen: 3.078041 s Erfassungszeit. Diese Zeiten überlappen und dürfen nicht einfach als Wandzeit addiert werden. Gesamtdauer 4.672947 s, höchster Jobpeak aller Integrationsproben 52781056 Byte.

I09 reine Metadatenmessung ohne Policy: 112 neutrale Dateien, 40 vollständige inventory-Aufnahmen. Mittel 0.024386 s, Maximum 0.026840 s pro Aufnahme. Unveränderte Dateien, keine Quellen, keine 1024-Frame- oder 32-Geschichten-Serie. Rohmessungen in inventory-cost.json.

N01–N07 bestanden: Forschung vor Hashaufruf gesperrt; zwei neutrale Rezept-/Referenzvergleiche; exakt erlaubte Namespace-/Admissionänderungen; alte Berechtigungsart abgewiesen; exklusives Ziel ohne Resume; neues Ziel/Berechtigung fehlen; unmittelbare Verwendung der abgenommenen Komponenten und deaktivierte Forschungs-Fault-Hooks. focused-tests.json dokumentiert den ausgeführten Testlauf.

## Ressourcenbilanz und aktualisierte Planung

Harter gemeinsamer Windows-Job 536870912 Byte und zwei Prozesse; Mitgliedschaft vor Gatefreigabe geprüft. Höchster gemessener Jobpeak 52781056 Byte. Terminalslot und sämtliche neuen Nachweise zählen vollständig mit. Neues Vorbereitungspaket bleibt unter 8388608 Byte; sein kompletter Umfang einschließlich späterer Berechtigung zählt gegen 67108864 Byte Gesamtexport. Quelle-, Archiv-, Record-, Dictionary-, Tabellen-, Verwaltungs-, Temp- und Abschlussgrenzen unverändert.

Global 57600 s ab vor Admission; Worker 54000 s ab demselben Beginn; 3600 s Abschlussreserve innerhalb der Globalfrist. Die zusätzliche Fünfsekundenreserve der Erfassungskomponente liegt ebenfalls innerhalb dieser Grenze. Keine Forschung in der Abschlussreserve.

Übernommene konservative V3-Planung 44031.048368 s global. Neu zusätzlich 6500 s Erfassungsaufwand. Grundlage: 131072 Frameprüfungen (64 * 1024 * 2), auf 135000 für Quellen, Fälle, Cleanup, Statistik und Abschluss aufgerundet. Größter beobachteter Einzelprüfaufwand im belasteten integrierten Pfad 0.0377151 s; mit 25 Prozent Zuschlag etwa 6364.423 s, auf 6500 s aufgerundet. Der gemessene Wandzeitunterschied der belasteten und unbelasteten kurzen Integration ist berücksichtigt und kleiner als diese angesetzte Kostenrate. Der parallel arbeitende Supervisor wird nicht fälschlich als vollständig serieller zweiter Lauf addiert; dessen tatsächliche Überlappung ist eine verbleibende Planungsannahme.

Aktuelle Planung: Worker 46931.048368 s, Abschlussreserve 3600 s, global 50531.048368 s = 14.0364 h. Verbleibender Puffer 7068.951632 s = 1.9636 h. Das ist eine plausibilisierte Planung aus kurzen neutralen Messungen, keine gemessene oder garantierte Serienlaufzeit. Mehr Dateisystemlatenz, andere Schedulerinterferenz oder wiederholte instabile Aufnahmen können den Versuch weiterhin terminal abbrechen. Keine Änderung des Zeitvertrags.

## Übernahmen und Grenzen

Abgenommenes FS-Korrekturpaket a1bdca305b43ceba1e5755cd70557d1eec7b4b0b31352c0425d87902004face4: sämtliche 580 gebundenen Dateien vor Übernahme unverändert geprüft. F01–F14, die frühere unabhängige Statistik-/Matrixqualifikation und unveränderte U/R-/Decoder-/Größennachweise werden mit ihren Bindungen übernommen; keine vollständige Qualifikationsserie erneut ausgeführt. Historische Einstiege, Bindungsdateien, Startmarker, Forschungsquellen und Abbruchbelege bleiben unverändert.

Die Dateierfassung ist weiterhin eine begrenzt wiederholte stabile Sicht, kein Betriebssystem-Snapshot/Lock; beliebig kurze Zwischenüberschreitungen oder adversariale ABA-Änderungen sind nicht garantiert erkennbar. Acht instabile Aufnahmen führen zum Abbruch. Funktionierender Terminal-Schreibpfad und Betriebssystemantwort bleiben Voraussetzungen. Kein Vollseriennachweis, keine Forschungsergebnisse und keine Behauptung bestätigten internen Cleanups nach erzwungenem Workerende.

## Exakter zukünftiger Einstieg und nächster Schritt

Verbindlicher argv unter call in prestart.json:
C:\Python314\python.exe -m tools.s2uc_ura1_prepare_v4 run C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\ura1-v4-preparation-20261015-01\prestart.json C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\ura1-v4-preparation-20261015-01\authorization.json

Passende zukünftige Berechtigung ausschließlich URA1_RESEARCH_ONCE_V4 mit exaktem prestart_sha256 und allow_research=true. Nicht erstellt. Der Forschungsaufruf wurde nicht ausgeführt. Exklusives Ziel und verbrauchender START werden erst innerhalb des separat beauftragten Aufrufs angelegt; Terminalreserve vor Workerfreigabe. Kein Retry-/Resumeweg.

Nächster Schritt: Projektleiter prüft die vollständige integrierte V4-Vorstartbindung und die ausgewiesenen Ressourcen-/Dateisystemgrenzen. Erst danach gesonderte Entscheidung über einen Forschungseinstieg. Diese Vorbereitung autorisiert keinen Start.
