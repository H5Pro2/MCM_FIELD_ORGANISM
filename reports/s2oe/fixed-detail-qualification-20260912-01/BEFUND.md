# Fester Detailblick: Anschluss neutral qualifiziert

2026-09-12. `fixed-detail-qualification-20260912-01`: **16/16**, genau ein
Testaufruf; keine historischen Tests wiederholt. Quellenhashes nach dem
Aufruf unverändert. Die ausgewählte MP4 wurde weder geöffnet noch verarbeitet.

## Verbindliche Kontrollansicht

Die Position wurde vom Analysten festgelegt, nicht vom Benutzer ausgewählt
und nicht automatisch erkannt: Original 3840×2160, Rechteck
`[960,2880) × [540,1620)`, Ausgabe 1920×1080, unverändert für zehn Frames.
Keine Objektannahme, Aufmerksamkeit oder Lernbindung.

`tools/_s2oe_fixed_detail.py` enthält den neuen privaten Anschluss. Der
vorhandene Worker wird über seinen bereits vorhandenen `video_point`-Transport
und seine Decoderfactory wiederverwendet. Die Transport-Anfragenummer ist
ausdrücklich von Auswahlfenster und Ansicht getrennt. Keine Änderungen an
`_s2oe_media_decoder.py`, `_s2oe_decoder_worker.py` oder am Rezeptor.

Reihenfolge: nativen Frame nach unveränderter PTS-Regel auswählen, Detail
aus dessen vollaufgelöstem RGB ausschneiden, anschließend die Übersicht mit
dem **bisherigen direkten AREA-/RGB-Aufruf auf dem nativen Frame** erzeugen.
Die Übersicht wird nicht aus dem vollaufgelösten Detail-RGB herunterskaliert.
Damit ist die frühere Planoption eines gemeinsamen RGB-Zwischenbildes für
beide Arme durch die spätere Vorgabe ersetzt; historische Übersicht bleibt
im Code unverändert. Pixelherkunft, Originalmaße, Rechteck, Maßstab, Farbe,
Profilversion, PTS/Zeitbasis, Auswahlzeit und Hash werden je Ansicht gebunden.

## Tatsächlich erreichte Prüfdeckung

- Feste Koordinaten, Bool-/negative/überschreitende/fremde Rechtecke abgewiesen;
  Originalpixel an beiden Ausschnittgrenzen unabhängig kontrolliert.
- Alle zehn Auswahlpositionen und 20 Ansichtsschritte mit neutralen Frames;
  gemeinsame PTS, Reihenfolge, fehlende Frames und unzulässige Zeiten geprüft.
- Unveränderte Übersichtskonversionsparameter und Auswahl gegenüber der
  vorhandenen Funktion mit neutralen Fixtures verglichen.
- **Nativer Worker erreicht:** PyAV 16.1.0, gebundene FFmpeg-Bibliotheken,
  neutral im Speicher erzeugte YUV420P-Frames; echte Konversion, Übertragung
  und zwei Rezeptoranalysen. Kein Mediencontainer und kein Audiozugriff.
- Bildrückgaben read-only markiert, Belege als abgetrennte Kopien; Status ohne Zustandsmutation, wiederholtes
  Schließen und weiterer Zugriff nach Stopp geprüft. Zwei von 20 Ansichten
  bedeuten `CLOSED_INCOMPLETE`, nicht vollständigen Vergleichserfolg.
- Geschlossenes Startgate und fehlende Codebindung abgewiesen. Neuer Einstieg
  verbraucht sein Gate; er setzt es vor weiterer Prüfung wieder False.
- 24-positionige Ausgabehülle sowie Überschreitungen geprüft. Konservative
  Einzelkappen gelten zusätzlich; keine Obergrenze nur aus einer kleinen
  erfolgreichen Beispielgröße abgeleitet.

Der native Worker hatte Peak-Process-Commit **525.185.024 Byte**, Peak-Job-Commit
**531.759.104 Byte**, jeweils unter 1.073.741.824 Byte. Ein Übertragungsslot
6.240.000 Byte, Queue 1, 30 Sekunden Anfragegrenze und fünf Sekunden Stoppgrenze
unverändert. `worker_exit_code=1` folgt dem vorhandenen terminierenden
Close-Pfad; er wird nicht als regulärer vollständiger Vergleich ausgegeben.
Die neutral erzeugten Frames waren keine dekodierten Containerframes:
Containerbytes, Pakete und Video-Decoderzähler sind folgerichtig null.

## Getrennte Informationsverlustkontrolle

K0 und K1: fest gebundene invertierte Schwarz-/Weiß-Streifen, Periode 160,
Halbperioden je 80 Pixel, gleiche RGB-Kanäle. Zwei unterschiedliche Pixelhashes
wurden beobachtet; **alle 288 Rezeptorwerte waren jeweils gleich**, sowohl
in Übersicht als auch im Detail. Vollständige Werte in `information-control.json`.
Dieser diagnostische Ausgang war kein technisches Bestehensgate.

Das belegt einen konkreten Gleichheitsverlust bei diesen Mustern, keine
allgemeine Informationserhaltung oder Aussage über die ausgewählte Videoszene.
Gleichbleibende Rezeptorwerte allein dürfen deshalb nicht als Stabilisierung
eines identischen Inhalts ausgegeben werden.

## Vergleichsbindung und Bilanz

`preregistration.json` bindet Quelle, Geometrie, aktuelle Codehashes und den
konkreten späteren Vergleich unter `comparison`:
zehn Auswahlzeiten 0,05; 0,55; …; 4,55 Sekunden, je letzter Frame am oder
davor; native Zeitbasis 1/30000 und Bildrate 30000/1001 unverändert.
Je Frame Übersicht, dann Detail aus demselben Ursprung. Zusätzlich K0/K1
in beiden Ansichten: **zwölf Analysen pro Arm, 24 insgesamt, 6.912 Werte**.
Gleiches Rezeptorbudget, nicht behauptet gleiche CPU-Kosten der Vorverarbeitung.
Für den späteren Kontrollvergleich sind 576 Komponenten plus 576 unabhängige
Prüfkomponenten gebunden. Keine zeitliche Distanzreihe und keine Memoryaufrufe.

Vorbilanz einschließlich aller Softwaredateien, Tests, Workerfixture, Bericht
und Fehlerlogreserve: **794.037 / 4.194.304 Byte**. Metadatenreserve
**61.445 / 65.536 Byte**, räumliche Zusatzbelege maximal 57.344 / 262.144 Byte.
Softwaredateien physisch vollständig: 339.376 Byte, in der Gesamtsumme enthalten.
Keine Erhöhung einer Runtime- oder Memorygrenze.

Istgrößen: vollständige neutrale Ausgabehülle 192.802 Byte; native Ansichten
14.989 Byte; Informationskontrolle 26.795 Byte; Workerbeleg 1.037 Byte;
Qualifikationslog 1.672 Byte. Abschließende Istbilanz: `final-balance.json`.

Bindungs-SHA-256:
`1c9070945a0669d02eebe4cf6027b2406928e4f37a78982441f6f046b66b0fd6`.
Anschlussmodul-SHA-256:
`04e4ed9581415ab8917826a5730fefd737783262dbd05debafbcfa940824d188`.

## Verbleibende Grenzen

Kein realer Medienvergleich und kein Memorylauf. Historische Decoderqualifikationen
werden nicht als unveränderte aktuelle Softwareidentität ausgegeben; die
aktuellen Abhängigkeiten stehen im neuen Inventar. Der reale 24-Ansichten-
Gesamtabschluss samt unabhängiger Prüfung ist hier nicht ausgeführt und wird
nicht durch die native Zweierfixture ersetzt. Seine endgültige Lauf-ID,
Einmalzulassung und Abschlussbindung bleiben separat erforderlich.

Eine frei bedienbare Benutzerwahl ist nicht implementiert. Keine Aussage über
Objektidentität, visuelle Erhaltung oder bessere Stabilisierung. Gates False;
historische Belege unverändert. Keine automatische Folgeausführung.
