# URA1 Gesamtzeitvertrag V2 – 16 Stunden

Version URA1_TIME_V2_57600, beschlossen im Vorbereitungsauftrag 2026-10-15.
Ersetzt ausschliesslich fuer einen kuenftigen separat beauftragten Vergleich die
alte 3600/3540-s-Zeitplanung. Keine Aenderung historischer Versuche oder Marker.

Die monotone globale Frist beginnt vor Bindungs-/Berechtigungspruefung im
Supervisor und endet nach geschriebenem und geprueftem Abschlussmanifest:
57600 Sekunden. Enthalten sind Quellenrezeptpruefung, Erzeugung und unabhaengige
Pruefung/Versiegelung aller 32 Quellen, 64 U/R-Arme, Referenzen, alle Ereignisse,
Archivierung und unabhaengige Archivpruefung, Statistik samt Referenz, Cleanup,
Abbruchbericht und Abschluss. Kein Nachholen ausserhalb der Frist, kein Teilstart.

Workerfrist: 54000 Sekunden ab demselben globalen Beginn, nicht ab jedem Fall
oder Workerstart. Reserve: 3600 Sekunden fuer Supervisorabschluss, Dateihashes,
Ergebnis-/Abbruchbericht, Cleanup und Abschlussmanifest. Statistik und saemtliche
Archivpruefungen muessen bereits innerhalb der Workerfrist fertig sein. Die
Reserve ist kein Zusatzbudget. Sie deckt auch unvorhergesehene Abschlusslatenz;
keine Armfortsetzung darin. Bei Ueberschreitung wird der Worker beendet; fehlende
Ergebnisse bleiben NICHT_AUSWERTBAR. Kein Retry, Resume oder Ersatz.

Unveraendert: gemeinsamer harter Windows-Job 536870912 Byte und maximal zwei
Prozesse; pro Fall gzip 524288 Byte, dekomprimiertes Format und Dictionary
4194304 Byte, Einzelrecord 262144 Byte; Tabellen 65536, Referenzkanten 262144,
Indizes 65536, Collections 16. Temporaer 67108864 Byte. Gesamtexport 67108864 Byte
inklusive Vorbereitung; Vorbereitung 8388608, Quellen 2097152/32768 je Fall,
Fallarchive 33554432, Verwaltung/Postpruefung 2097152, Abschluss 1048576 Byte.
U/R, unabhaengige Referenzen, Bestands-/Zell-/Ticketgleichheit, Erfassungsanker,
Ereignisvollstaendigkeit und wissenschaftlicher Statistikvertrag unveraendert.

Statistik: ein Primaerkontrast D:U-R, alle 256 Q-Ziele; exakte rationale
Weiterverarbeitung gespeicherter binary64-MAE. 10000 nach Orientierung geschichtete
Paarziehungen, 320000 Matrixbytes im festgelegten URA1-Bootstrapnamensraum.
95%-Quantile mit h=9999q, linear interpoliert; sekundäre Bilanzen deskriptiv.

Vorbereitung benutzt nur MCM-URA1/neutral/v1 und Handfaelle. Keine Erzeugung,
Besichtigung oder Auswahl von MCM-URA1/source/v1. Nur die Bootstrapmatrix ist
jetzt zur Erzeugung freigegeben. Forschung bleibt gesperrt, bis eine separate
Beauftragung exakt den neuen Vorstart-SHA freigibt. Eine authorization.json wird
in diesem Paket nicht erstellt. Forschungseintritt nur mit passender Einmal-
Berechtigung; exklusiver neuer Zielordner ura1-comparison-v2-time16h und START.
Alle Quellen werden im kuenftigen autorisierten Lauf unabhaengig rekonstruiert
und gemeinsam gehasht versiegelt, bevor irgendein Policyarm startet. Die heutige
Vorstartbindung bindet das Rezept und den gesperrten Generator, keine unbekannten
Quellenbytes. Dieses zweistufige Verfahren ist notwendig, um das heutige
Forschungsquellenverbot einzuhalten. Der Laufmarker ist schon vor der spaeteren
Quellenerzeugung verbraucht; Quellefehler erneuern ihn nicht.

Alle 32 Geschichten muessen vollstaendig sein; sonst kein Primaerurteil.
Kein Erfolg eines Vorbereitungstests ersetzt die gesonderte Forschungsbeauftragung.
