# Visuelle Diagnoseanbindung: zwölf neutrale Gruppen bestanden

Genau ein Aufruf, 12/12 bestanden. Keine MP4 geöffnet, keine PyAV-
Dekodierung, Rezeptor-, NJ-, Memory- oder Feldausführung. Gates False.
Quelleninventar vor dem Aufruf gebunden und danach unverändert.
Repository-Basis: 537109994cf777f8d36cda617aafe12226806c25, schmutziger
Arbeitsstand; konkrete Dateien siehe Vorregistrierung, kein Commit behauptet.

Die AV- und Diagnoseroutine teilen Decoder._select_video samt Konvertierung.
Die historischen Ergebnisdateien bleiben unverändert; die alten Codehashes
qualifizieren den geänderten Decoder-/Workerstand nicht automatisch.
Der neue Zugang bindet das bestehende COMMIT_1024-Profil; Defaultlimits
wurden nicht verändert. Native aktive yuv420p-Planezeilen ohne Padding
werden getrennt von konvertierten RGB-Bytes gebunden. Andere native Formate
scheitern ausdrücklich, ohne Ersatzformat.

Geprüft: beide festen Auswahlzentren, gemeinsame Routine, getrennte synthetische
Zustände, genaue Konvertierungsargumente, Zeit-/Abdeckungsfehler, unverändertes
Original bei Okklusion, numerische Gleichheit und Abweichung, ungültige Werte,
Gate-/Profilübergabe, Paddingunabhängigkeit und geschlossene/falsche Aufrufe.

## Konkrete Bindung

Quelle und Auswahl siehe docs/VISUELLER_DIAGNOSEANSCHLUSS.md, im Inventar
digestgebunden. Vier frische Öffnungen: zweimal window=2, zweimal window=8.
Auswahlzentren 21/20 und 81/20 s, historische Frame-PTS 31031 und 121121
bei Zeitbasis 1/30000. Fensterbeginn ist nicht Framezeit. Vier Frames,
acht spätere Analysen. Keine reale Lauf-ID oder Autorisierung angelegt.

Vorregistrierung SHA-256:
3d4a97e338a837a9951ab4bff0b29416f75eb083b31baad9a44bd46d6dc85851.
Ergebnis SHA-256:
d1cd4bb3ef33208769b6a5af50c9322bbc2b24f6dd3f1c9955292bf0ee377298.

## Bilanz und ausdrücklich offene Abdeckung

Vorbindung: Quellen 71.731, administrative/numerische Reserve 114.688,
Gesamt 186.419 Byte. Grenzen 327.680 Quellen, 131.072 Metadaten,
393.216 Zusatzhülle, 4.194.304 Gesamt unverändert. Tatsächlich entstanden
vor diesem Bericht: Vorregistrierung 1.800, Claim 4, Log 1.347,
Ergebnis 1.575 Byte. Bericht innerhalb der gebundenen 16.384-Byte-Reserve.

Diese Rechnung ist eine Reservierung, noch kein Nachweis der vollständigen
späteren Serialisierung. Die Vergleichsfunktion liefert ausgefaltete
Einzelvergleiche zusätzlich zu vollständigen Hexwerten. Deren gesamte
Ausgabeform wurde nicht gegen die 57.344-Byte-Tabellenreserve erzeugt/geprüft.
Auch der neue video_point-Befehl im tatsächlichen Workerprozess wurde nicht
durchlaufen; geprüft wurden die Routinen und die gemockte UHD-Übergabe.
Das unveränderte OS-Limit ersetzt diesen neuen Protokollnachweis nicht.
Die globale 400-Frame-Grenze über vier Worker ist bisher nur geplant;
vorhandene Zähler begrenzen jeweils einen Worker, nicht den Gesamtversuch.

Deshalb: lokale Tests QUALIFIED, gesamter Diagnose-Ausführungsanschluss
noch nicht vollständig qualifiziert. Keine zweite Testserie, keine nachträgliche
Codeänderung nach dem Aufruf und kein realer Vergleich gestartet.
Gleichheit/Abweichung bleiben gleichberechtigte Ergebnisse, keine neue Schwelle.
Nötige Rückmeldung betrifft diese konkreten Anschluss-/Hüllenlücken,
nicht eine Wiederholung historischer Qualifikationen.
