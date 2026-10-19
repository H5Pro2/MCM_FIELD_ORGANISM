# URA1_STATE_DELTA_V1: Vertrag des genau einmaligen neutralen 1024-Frame-Grenztests

Beauftragt am 2026-10-15: Vorbereitung und genau eine technische Ausführung.
Kein Forschungsversuch, keine Materialsuche, Bootstrapmatrix oder Serie.

Material: vorhandene 16 D_ITEMS-Blöcke exakt 16-mal wiederholt, unveränderte
blocks-Funktion, 1024 Frames. Genau U/R getrennt und nacheinander im selben
Worker, jeweils mit eigener unabhängiger Referenz. Keine Interpretation
des Leistungsabstands. Alle internen und äußeren Ereignisse bleiben erhalten.
Die bestehende 128-Frame-Kleinfallhülle und sämtliche U/R-Kernregeln bleiben
unverändert. Der separate Einstieg akzeptiert nur den exakt gebundenen Fall.

Vor Start werden Code, Materialrezept und Materialhash, Interpreter/Runtime,
Grenzen, Qualifikationsbelege und der exakte Aufruf in prestart.json gebunden.
Das Dokument erhält eine SHA-256-Begleitdatei. Der Supervisor verifiziert
vor Reservierung, der Worker nach Reservierung erneut. START.json wird exklusiv
mit create-new erstellt und bindet den Vorstart-SHA. Der Start ist damit auch
bei Startfehler oder technischem Abbruch verbraucht: kein Retry, Resume oder
Ersatzfall. Ein vorhandener Marker wird niemals überschrieben.

Gemeinsamer harter Windows-Job: 536.870.912 Byte Commit, maximal zwei Prozesse
(Supervisor und ein Worker), keine Breakaway-Ausnahme. Gesamtfrist 3600 s ab
Supervisorbeginn einschließlich Bindungsprüfung; Workerfrist 3540 s. Bei
Fristüberschreitung wird der Worker beendet und dessen Ende bestätigt.

Unveränderte Grenzen: 524.288 Byte gzip; 4.194.304 Byte dekomprimiertes Format
und serialisierte Dictionaryknoten; 262.144 Byte je Record; 65.536 Knoten,
262.144 Referenzkanten, 65.536 Recordindizes, 16 Collections; temporäre Daten
höchstens 67.108.864 Byte. Gesamtexport einschließlich Vorbereitung/Abschluss
höchstens 64 MiB; Vorbereitung 8 MiB, Quellen 2 MiB/32 KiB je Fall,
Verwaltung/Postprüfung 2 MiB, Abschluss 1 MiB. Material wird als kleines
festes Rezept gebunden, nicht als neue Forschungsquelle erzeugt.

Während der Erfassung werden kanonische Originalrecords unabhängig vom
Referenzencoder normalisiert und gehasht. Acht geordnete Folgen (Ereignisse,
interne Ereignisse, Prognosen, Feedback je U/R) erhalten Hash, Bytezahl und
Recordanzahl. Der Hash wird nur nach erfolgreicher Aufnahme eines vollständigen
Records fortgeschrieben. Die übrige Recordstruktur erhält einen eigenen
kanonischen Hash mit Platzhaltern für diese Anker. Der unabhängige Decoder
rekonstruiert jede Folge und die übrige Struktur und vergleicht beides gegen
die vor der Archivkodierung gespeicherten Anker. Der zusätzliche vollständige
Archivhash allein ist ausdrücklich nicht der Integritätsnachweis.

Vorabtests mit höchstens acht Frames prüfen exakte Bindung, Markerexklusivität,
Startfehler, beide Fristen, Referenz-/Ereignisprüfungen, Integrität trotz neu
gehashtem manipuliertem Encoderoutput, Dictionaryabbruch, Fortschritt und
Cleanup. Diese Tests verbrauchen nur ihre separaten Testmarker, niemals den
1024-Frame-Marker.

Terminal bei erster Bindungs-, Material-, Referenz-, Bestands-, Hypothesen-,
Ticket-, Zell-, Integritäts-, Speicher-, Zeit-, Tabellen-, Record- oder
Exportabweichung. Abbruchbericht nennt erste beobachtete Verletzung, Phase,
pro Arm begonnenen und vollständig referenzgeprüften Frame, Recordanzahlen,
Ressourcen und Cleanup. Teilanker belegen ausschließlich den erfassten Präfix;
sie sind kein bestandener Größenlauf und keine Leistungswertung.

COMPLETE_NEUTRAL_SIZE setzt vollständige 1024 Frames je Arm, sämtliche
Referenz-/Gleichheitsprüfungen, unabhängige Ankerrekonstruktion, Grenzen und
Cleanup voraus. Ein Erfolg belegt nur diesen einen periodischen Handfall.
TECHNICAL_ABORT ist ein verwertbarer technischer Befund, keine erfolgreiche
Qualifikation. Kein Ergebnis dieses Auftrags ist eine Forschungsfreigabe.

Separater Delta-Auftrag, Pruefpaket 238cd874-eaf1-4447-8871-8ecf29997543.
Ziel: reports/s2uc/ura1-delta-size-neutral-20261015-01.
Einstieg: tools.s2uc_ura1_delta_size_once. Format gemaess
docs/S2UC_URA1_ZUSTANDSDELTA_FORMAT_20261015.md; Dictionarybudget umfasst
Werte, Pfade und Deltas gemeinsam. Alle urspruenglichen Grenzen gelten.
Der fruehere ura1-size-neutral-Marker bleibt verbraucht und unveraendert.
Die Fortsetzungsnachricht erneuert keine Einmalfreigabe.
