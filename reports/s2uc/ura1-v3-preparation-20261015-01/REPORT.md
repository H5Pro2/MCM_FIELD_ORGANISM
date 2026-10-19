# Vollständige URA1-V3-Vorbereitung mit integriertem Terminalabschluss

Status PASS_PREPARATION_V3. Ausschließlich Vorbereitung; keine Forschungsfreigabe und kein Forschungsstart.

## Quellenentscheidung und historischer Versuch

Der alte Versuch ura1-comparison-v2-time16h bleibt TECHNICAL_ABORT, sein START und seine Freigabe verbraucht. Unterbrechung erfolgte auf den damaligen Beendigungsauftrag. 25 Archive vorhanden, mindestens 24 abgeschlossene Fälle aus sequenziellem Ablauf ableitbar; exakter Abschlussstand unbekannt. Kein Leistungsurteil. Seine 32 bereits erzeugten Quellen werden weder fortgesetzt noch im neuen Vergleich wiederverwendet. Alte Laufartefakte und Bindungsdateien bleiben unverändert. Belegverweise und Hashes in source-decision.json.

Vorab festgelegt: Forschungsnamensraum MCM-URA1/source/v3; exklusives neues Ziel reports/s2uc/ura1-comparison-v3-terminal16h. Dieser Zielordner fehlt weiterhin. Keine neuen Forschungsquellen erzeugt oder besichtigt. Rezept unverändert: 32 Geschichten à 1024 Frames, 16 je Orientierung, dieselben drei Streams, Fisher-Yates mit begrenzter Rejection-Sampling-Ziehung und dieselben Kontingenzen. Ausschließlich Namensraum und Admissionimport ändern sich; N03 prüft diese Änderung am vollständigen Quelltext beider unabhängiger Implementierungen. Neutraler Namensraum bleibt v1.

U/R-Policies, Referenzen, private Bestände, Feedback, Primärkontrast D:U-R auf allen 256 Q-Zielen, sekundäre Bilanzen und rationale Statistik bleiben unverändert. Bootstrapmatrix bytegleich übernommen: 320000 Byte, SHA-256 0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965. Keine Neuziehung, Auswahl oder Suche.

## Vollständig verbundener Einstieg

Neuer Einstieg tools/s2uc_ura1_prepare_v3.py mit festem PREP/TARGET/AUTH, vollständiger Datei-/Runtime-/Grenzen-/Namensraum-/Aufrufprüfung. Nur ausdrücklich passende zukünftige URA1_RESEARCH_ONCE_V3-Berechtigung lässt den Forschungszweig zu. Die Datei authorization.json wurde nicht angelegt. Das exklusive Verzeichnis und START werden vor Quellenarbeit erstellt; auch ein Abbruch verbraucht den Start. Alte Berechtigungsart wird abgewiesen. Kein Retry-/Resumeweg.

Der neue Einstieg benutzt das unveränderte geprüfte Korrekturmodul _s2uc_ura1_terminal_v3 direkt: Terminal, ReservedLedger, supervise und execute_with_receipts. Er ersetzt keinen echten Worker durch einen Teststub. Derselbe Worker ruft für neutrale und zukünftige Forschungsfälle policy_case auf; dieser führt tatsächliche frische U/R-Arme, Referenzen, Paarprüfungen, Erfassungsanker, Deltaarchiv und unabhängigen Decoder aus. Fallquittung erst nach dessen erfolgreicher Rückkehr und Cleanup. Die Forschung erzeugt und prüft zunächst alle 32 neuen Quellen unabhängig und versiegelt sie gemeinsam vor dem ersten Arm; danach unveränderte Statistik samt unabhängiger Referenz.

16384 Byte Terminalreserve werden vor dem Worker vorallokiert und sowohl im Gesamtexport als auch in der Abschlusskategorie gezählt. Reguläre Berichte laufen über den begrenzten Ledger, terminal.json unabhängig davon über den reservierten festen Slot. Der finale terminal.json ist der maßgebliche Supervisorbeleg, auch wenn worker.json/result.json/closure.json aus Budgetgründen fehlen. Erste Ursache, Folgefehler, abgeschlossene Fälle, aktiver Fall, Prozessende, Datei-Cleanup und interner Cleanup bleiben getrennt. Prozessende ersetzt keinen Arm-Cleanupnachweis.

Harter gemeinsamer Windows-Job mit 512 MiB und zwei Prozessen; tatsächliche Job-Mitgliedschaft wird vor Gatefreigabe geprüft. Global 57600 s ab vor Admission, Worker 54000 s ab demselben Beginn, 3600 s Abschlussreserve. Zusätzlich fünf Sekunden Reserve des Terminalmoduls innerhalb der unveränderten Globalfrist. Keine weiteren Policyarbeiten in der Abschlussreserve.

## Neue Prüfungen

N01–N06 bestanden: Sperre vor jedem Forschungshash, zwei neutrale Rezept-/Referenzprüfungen, ausschließlich erlaubte Quelltextänderungen, fehlende/falsche Berechtigung, exklusives Ziel ohne Resume, tatsächlich fehlendes Forschungsziel und fehlende Berechtigung. tests.txt enthält den vollständigen Testlauf.

I01: Zwei echte Achtframe-Handfälle, vier verschiedene U/R-Arme, je Arm/Fall 24 äußere und 92 interne Ereignisse, vier Prognosen und drei beobachtete Ziele. Beide Archive PASS_DELTA_INTEGRITY. Workerbericht, result, closure und terminal gespeichert, alle Closurehashes geprüft; beide Fallquittungen, interner Cleanup und Datei-Cleanup bestätigt. 2.519431 s; Kernel-Jobpeak 47771648 Byte.

I02: Nach vollständig abgeschlossenem Fall 1 wird bei tatsächlichem Armstart in Fall 2 das restliche Exportbudget neutral belegt. Erste Ursache EXPORT_LIMIT, Fallquittung [1], aktiver Fall 2. Drei tatsächliche Arme angelegt; deren Cleanup bestätigt. Der reguläre Workerbericht scheitert ebenfalls. Supervisorbeleg gespeichert, Workerende und Entfernung der Test-Partialdatei bestätigt. 1.821098 s; Jobpeak 46411776 Byte.

I03: Derselbe reale Workerpfad mit vollständig belegter Verwaltung. Erste Ursache CATEGORY_LIMIT:admin; abgeschlossener Fall 1, aktiver Fall 2, drei Arme und interner Cleanup bestätigt. Workerbericht scheitert, Supervisorbeleg bleibt gespeichert. 1.657150 s; Jobpeak 47083520 Byte.

I04: Nach Fall 1 und tatsächlichem Armstart in Fall 2 wartet ausschließlich der neutrale Fehlerhook; Supervisor setzt die verkürzte neutrale Prüffrist von acht Sekunden durch. Workerende bestätigt, Fall 1 quittiert, Fall 2 aktiv; interner Cleanup UNCONFIRMED, Dateicleanup bestätigt. 8.027094 s; Jobpeak 46272512 Byte. Forschungsfrist bleibt 54000 s.

Eine frühere neutrale Exportprobe zeigte korrekt, dass der reguläre Serien-Cleanup die erste Partialdatei entfernt und damit Platz für worker.json freigibt. Die anfängliche Zusatzannahme 'Bericht muss dann ebenfalls scheitern' traf nicht zu. Dieser Entwicklungsbeleg bleibt in development-export-cleanup-observation erhalten. Nur der neutrale Fehlerhook wurde ergänzt, um vor dem Bericht erneut den freien Platz zu belegen; die abschließende I02 prüft dadurch auch das tatsächliche Berichtsversagen. Kein Forschungsversuch und keine verschwiegene Wiederholung.

## Übernommene Nachweise und Grenzen

Alle 346 Dateien der V2-Vorbereitung vor Übernahme hashgleich. Die bisherige Korrekturbindung ebenfalls vor Aktualisierung der Übersichten vollständig geprüft. P01–P08, O01–O04, T01–T08, große Größen-/Archivprüfungen und Statistikqualifikation werden übernommen und nicht als große Serie wiederholt. inherited-qualification.json dokumentiert Herkunft und Matrixgleichheit. Neue Forschung ist dadurch nicht automatisch freigegeben.

Die drei Übersichten waren nachträglich Teil der Korrekturbindung. Für die jetzt ausdrücklich beauftragte Aktualisierung sind ihre exakten alten Bytes unter historical-overviews gesichert und in inherited-qualification.json zugeordnet. Die alte Bindungsdatei selbst bleibt unverändert; ihre drei damaligen Dokumenthashes beziehen sich auf diese archivierten Fassungen, nicht auf die jetzt aktualisierten Übersichten. Alle gebundenen historischen Code- und Laufdateien bleiben am Ort unverändert. Neue Vorstartbindung schließt veränderliche Übersichten aus und bindet stattdessen diesen statischen Bericht und die archivierten Nachweise.

Alle unveränderten Byte-/Kategorie-/Tempgrenzen aus LIMITS gelten weiter. Die Vorbereitung einschließlich Matrix, ursprünglicher Überblickssnapshots, neutraler Archive, Budgetbelege und neuer Bindung bleibt unter 8 MiB und zählt später vollständig gegen 64 MiB Gesamtexport. Der Terminalslot zählt zur 1-MiB-Abschlusskategorie. Ressourcenplanung übernimmt die frühere konservative Kernschätzung und ergänzt 120 s für die neue terminale Anbindung: etwa 12.23 h einschließlich Abschlussreserve, etwa 3.77 h Restpuffer. Das ist eine Planung, keine Messung oder garantierte Schranke für 32 neue Geschichten.

Belegt sind kurze neutrale echte Policyfälle und Budget-/Fristfehler bei funktionsfähigem Dateisystem. Nicht geprüft: neue Forschungsquellen, vollständige neue Serie, Strom-/Datenträgerausfall oder beliebige Betriebssystemlatenz. Im Forschungszweig sind Fault-Hooks deaktiviert; keine größere Reihe zur Vorbereitung gestartet.

## Späterer exakter Aufruf und Entscheidung

Der verbindliche spätere argv steht vollständig in prestart.json unter call:
C:\Python314\python.exe -m tools.s2uc_ura1_prepare_v3 run C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\ura1-v3-preparation-20261015-01\prestart.json C:\Users\TV\Documents\MCM_FIELD_ORGANISM\workspace\reports\s2uc\ura1-v3-preparation-20261015-01\authorization.json

Dieser Aufruf wurde nicht ausgeführt. Der endgültige Vorstart-SHA steht in prestart.sha256. Nächster Schritt: Projektleiter prüft die vollständige Vorbereitung samt Quellenentscheidung und trifft erst danach eine gesonderte Entscheidung über genau einen Versuch auf diesem SHA. Bis dahin bleiben authorization.json, neues Forschungsziel und neue Forschungsquellen abwesend.
