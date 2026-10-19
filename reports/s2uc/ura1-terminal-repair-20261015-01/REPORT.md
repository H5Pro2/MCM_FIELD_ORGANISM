# URA1-V2: Unterbrechung und terminale Korrektur

Stand 2026-10-15. Abnahme zurückgestellt. Keine Forschungsfreigabe.

## Tatsächlicher Versuch

Der noch laufende Worker PID 13188 wurde auf ausdrücklichen Projektleiterauftrag mit Stop-Process beendet. Der vorhandene Supervisor PID 13444 schloss danach selbst ab. Beide Prozesse sind beendet. Der alte Supervisor speicherte TECHNICAL_ABORT mit WORKER_EXIT:4294967295 nach 6295.248 Sekunden. Dieser Exitcode ist die technische Folge des angeordneten Stopps; Anlass war der bestätigte Abschlussfehler und die zurückgestellte Abnahme.

25 Fallarchive und 25 Erfassungsmanifeste liegen vor. Mindestens Fälle 1–24 haben nach dem sequenziellen gebundenen Kontrollfluss vollständig zurückgegeben, bevor Fall 25 archiviert wurde. Das ist eine aus Ablauf und Dateistand abgeleitete Untergrenze, keine erneute Archivprüfung. Ob Fall 25 vollständig abgeschlossen oder Fall 26 schon begonnen hatte, ist nicht belegt. Exakter Fortschritt bleibt unbekannt, nicht null. Es fehlen persistente Abschlussquittungen pro Fall im historischen Code.

32 Quellen waren bereits erzeugt. Ihre Inhalte und die Archivleistungen wurden nicht besichtigt oder ausgewertet. Zur Beweissicherung wurden vorhandene Dateien ausschließlich binär gehasht und mit Größen inventarisiert. START, authorization, Quellen, Archive sowie alte result/closure bleiben unverändert. Kein Neustart, Resume, Ersatzmaterial oder statistisches Urteil.

Worker- und Supervisorende sowie keine verbliebenen Partialdateien bestätigt. Interner Arm-/Store-Cleanup des unterbrochenen Falls UNBESTÄTIGT; Prozessende ersetzt diesen Nachweis nicht. Prozessressourcen wurden mit Prozessende freigegeben. interruption.json enthält Grund, Grenzen und vollständiges Dateiinventar.

## Ursache und getrennte Korrektur

Im historischen Worker schreibt finally den Fehlerbericht erneut über Ledger.write. Im Supervisor scheitern ledger.check und anschließende result/closure-Schreibvorgänge ebenfalls an dem bereits erschöpften Budget. Zusätzlich konnte der Supervisor die erste Workerursache durch einen Folgefehler ersetzen. Diese Defekte sind statisch bestätigt; beim angeordneten Stopp war das tatsächliche Exportbudget noch nicht erschöpft und der alte Abschluss wurde gespeichert.

Neue Datei tools/_s2uc_ura1_terminal_v3.py: 16384 Byte fester terminal.json-Slot vor Workerzulassung, vollständig innerhalb der unveränderten Export- und Abschlusskategorie. Reguläre Schreibvorgänge prüfen benötigten Platz vor dem Schreiben. Der Slot ist bereits belegt und bleibt damit auch bei vollständigem Verbrauch des übrigen Exports verfügbar. Speichern/Flush/fsync/Readback des terminalen Datensatzes benutzen keinen regulären Ledger und benötigen keine temporäre Zusatzdatei. Verwaltung darf vollständig erschöpft sein, da der Beleg der Abschlusskategorie zugeordnet ist.

Globale Grenze 57600 s und Workergrenze 54000 s unverändert. Zusätzlich beendet der reguläre Ledger seine Arbeit fünf Sekunden vor der globalen Grenze; diese Sekunden liegen innerhalb des bisherigen Vertrags. Der Supervisor beendet und wartet auf den Worker vor seinem terminalen Abschluss. Tatsächliche nicht löschbare Partialdateien bleiben als Fehler und offener Cleanup sichtbar.

Erste Workerursache wird vor dem regulären Workerbericht gesichert. Folgefehler werden getrennt und begrenzt gespeichert. Fortschrittsquittungen entstehen ausschließlich nach Rückkehr des vollständig geprüften Fallaufrufs mit bestätigtem Cleanup. Beim Beginn des nächsten Falls wird dessen Cleanup wieder unbestätigt. Workerende, Dateicleanup und interner Cleanup sind getrennte Felder.

worker_adapter bindet ausschließlich Ledger und Fallabschlussquittungen in den unveränderten historischen Worker ein. supervisor_adapter stellt den getrennten Abschlussweg mit Job-Mitgliedschaftsprüfung und Gate bereit. Der bestehende Forschungsaufruf wurde NICHT umgeschrieben; die alte Bindung bleibt intakt. Das Korrekturmodul bietet bewusst keinen Forschungs-CLI, keine neue Berechtigung und keinen Startmarker. Eine spätere Forschungsentscheidung benötigt eine neue vollständige Aufruf-/Ziel-/Quellenentscheidung und darauf abgestimmte Forschungs-Vorstartbindung; der hier gelieferte SHA bindet nur das Korrekturpaket.

## Neutrale Prüfung

T01–T08 bestanden: Export vollständig belegt, Verwaltung vollständig belegt, gespeicherter Fristabbruch, erste Ursache/Fortschritt, fehlender Workerbericht, Reserve bei Zulassung, globale Zeitreserve, Workeradapter mit vor dem Bericht gesicherter Fehlerursache. Kurze Tests ohne Quellen oder Policies.

Zusätzlich drei echte Supervisor-/Workerproben im unveränderten harten Zwei-Prozess-/512-MiB-Job mit Original-Bytegrenzen: Exporterschöpfung, Verwaltungserschöpfung und verkürzte neutrale Workerfrist (0.3 s). Jede Probe wurde bis zum gespeicherten und zurückgelesenen terminal.json geprüft. Die beiden Budgetproben lassen den regulären Workerbericht tatsächlich scheitern. Erste Ursache NEUTRAL_INITIAL_FAILURE bleibt bestehen; Fortschritt [1], aktiver Fall 2 und unbestätigter interner Cleanup bleiben erhalten. Dies sind künstliche Quittungen, keine Policyfälle. Fristprobe bestätigt erzwungenes Workerende. Partials wurden nach Workerende entfernt. Details und Zeiten in probe-results.json; alle drei PASS, jeweils unter einer Sekunde. Keine unveränderte große Qualifikation wiederholt.

## Grenzen und nächster Schritt

Belegt sind die angeforderten Budget-/Fristfehlerpfade bei funktionsfähigem Dateisystem, nicht Stromausfall, Datenträgerausfall oder eine Garantie gegen beliebige Betriebssystemlatenz. Die neue Anbindung wurde mit neutralem Workerersatz geprüft, nicht durch einen Forschungsneustart. Keine Leistungsbewertung der unterbrochenen Serie.

Empfehlung: Projektleiter prüft Korrekturbindung und Fehlerproben. Anschließend muss er fachlich entscheiden, wie mit den bereits erzeugten 32 Forschungsquellen und dem verbrauchten Start umzugehen ist. Keine automatische Wiederholung und keine erneute Nutzung der historischen Freigabe. Eine positive technische Abnahme allein autorisiert keinen Forschungsstart.
