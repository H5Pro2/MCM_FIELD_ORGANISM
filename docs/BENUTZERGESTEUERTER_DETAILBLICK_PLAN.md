# Detailblick: begrenzter Darstellungsvergleich

Stand 2026-09-12. Nur Planung; keine Medienzugriffe, Tests oder Berechnungen.
Der vorherige Diagnosezweig ist geschlossen: reproduzierbarer visueller
Eingang, unmittelbar möglicher A-Abruf, e04 außerhalb der visuellen
PPB-Matchgrenze und deshalb keine Verstärkung der vorhandenen Spuren.
Keine weiteren Übergangsdiagnosen und keine Anpassung der Grenze 0,01.

## Frage und feste Eingänge

Welche räumliche Information zeigt der unveränderte Rasterrezeptor bei
Übersicht und Detail? Ein Ausschnitt ist weder Objekt noch Lernbindung.
Geprüft werden Darstellung und Informationsverluste, nicht Memoryerhaltung.

Quelle bleibt die bereits verwendete lokale Datei
`C:/Users/TV/Downloads/17138816-uhd_3840_2160_30fps.mp4`, SHA-256
`df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
Sie ist ein bereits untersuchtes Medium, kein unabhängiger Bestätigungskorpus.
Keine Rückkehr zum YouTube-Eingang, keine andere Quelle und keine Inhaltssuche.

Zehn Auswahlzeiten: 0,05; 0,55; …; 4,55 Sekunden. Jeweils letzter Frame am
oder vor dieser Zeit, gebunden mit seinem Nachfolger, Original-PTS und
Zeitbasis 1/30000. Native 30000/1001 fps bleiben erhalten. Beide Arme erhalten
denselben ausgewählten Originalframe. Keine zweite Decoderfolge pro Arm.

**Vorgeschlagene Benutzerwahl:** mittiges Rechteck im Original 3840×2160,
Ursprung oben links, x=960, y=540, Breite=1920, Höhe=1080, halboffene Grenzen
`[960,2880) × [540,1620)`. Vor einer späteren Analyse muss der Benutzer diese
geometrische Wahl bestätigen oder einmal anders festlegen. Danach unveränderlich;
keine Verfolgung, Auswahl anhand von Messergebnissen oder Nachjustierung.

| Arm | Originalbereich | Rezeptoreingang |
| --- | --- | --- |
| Übersicht | vollständige 3840×2160 | AREA-Verkleinerung auf 1920×1080 |
| Detail | festes Originalrechteck | 1920×1080, kein zusätzliches Hochskalieren |

Beide Ansichten werden aus demselben kanonischen Original-RGB-Frame gebildet:
gebundene BT.709-/MPEG-nach-JPEG-Konversion, anschließend räumliche Projektion.
Diese explizite Reihenfolge ist **nicht automatisch bytegleich** zum bisherigen
kombinierten YUV-Verkleinerungs-/RGB-Konversionspfad. Neuer Projektionsbeleg,
keine Umetikettierung alter Übersichtsergebnisse. Keine vergrößerte Kopie
des bisherigen 1920×1080-Übersichtsbilds als Originaldetail ausgeben.

## Gleiche Rezeptorarbeit, getrennte Informationskontrolle

Je Arm zehn Medienanalysen mit unverändertem `VisualGridConfig` und 288 Werten.
Vollständige Vektoren und ihre Originalraum-Zellrechtecke getrennt speichern.
Gleiche Rasterindizes bezeichnen zwischen den Armen **nicht dieselbe Bildfläche**;
kein unkommentierter Index-für-Index-Abstand und keine Anwendbarkeitsschwelle.
Berichten: räumliche Abdeckung, Werte, Gleichheiten und verlorene Außenbereiche.
Eine mögliche ruhigere Darstellung ist zunächst nur eine Beobachtung.

Separate, vorab festgelegte Informationsverlustkontrolle: zwei neutrale
3840×2160-RGB-Bilder. Bild K0 hat vertikale periodische Streifen von 160 Pixeln:
erste 80 schwarz, nächste 80 weiß; K1 vertauscht schwarz und weiß. Alle drei
Kanäle identisch, alle Zeilen gleich. Keine realen Videopixel dafür verändern.
Beide Bilder durch beide Projektionen: vier zusätzliche Analysen.

Vorhersage: unterschiedliche Pixelbilder können dieselben Zellmittelwerte
liefern. Die Kontrolle bindet Pixelungleichheit getrennt von Rezeptorgleichheit;
beides später tatsächlich prüfen, nicht nur aus dem Rezept behaupten.
Sie zeigt eine konkrete mögliche Informationsgrenze, keine Objektidentität.
Ein Kollaps darf nicht als erfolgreiche Stabilisierung gelten. Umgekehrt
beweist Nichtkollaps dieser Kontrolle keine allgemeine Informationserhaltung.

## Kleinster Anschluss und endliche Grenzen

Vorhanden: `tools/_s2oe_media_decoder.py:Decoder._select_video` für PTS-Auswahl;
`tools/_s2oe_decoder_worker.py` und `_s2oe_uhd_profile.py` für isolierte, begrenzte
Übertragung; `mcm_field_organism/finite_video_path.py:LocalChannelGridReceptor.analyze`
für unveränderte lokale Mittelwerte. Native Framebindung ist teilweise vorhanden,
aber noch kein qualifizierter räumlicher Detailarm.

Fehlt: ein expliziter visueller Diagnoseanschluss, der den ausgewählten nativen
Frame einmal konvertiert, beide Projektionen nacheinander liefert und ihren
räumlichen Beleg bindet: Quelldigest, PTS/Zeitbasis, Auswahlzeit, Originalmaße,
Rechteck, Zielmaße, Farb-/Filterreihenfolge, Projektionsversion und Payloadhash.
Die 30-fps-Rezeptorindexierung bleibt gegebenenfalls eine separate technische
Präsentationszeit, keine Behauptung nativer 30 fps. Keine Runtimezeit benötigt.

Kein Aufruf des AV-Sitzungsmaterialisierers: dessen Audio-/NJ-Verarbeitung ist
hier unnötig. Vorhandene visuelle Decoder-/Rezeptorbausteine wiederverwenden,
keine neue Laufplattform. Start bestätigt die feste Bindung, Status liest nur
Fortschritt, Stopp schließt kontrolliert; kein neuer Blick während des Laufs.

Budget: **12 gleich große Rezeptoreingänge je Arm, insgesamt 24 Analysen und
6.912 Werte**, keine Memory-/Feldoperation. Nur die zwei Kontrollvektoren je Arm
bitweise vergleichen: höchstens 576 Komponenten primär und 576 unabhängig.
Keine neuen zeitlichen Distanzreihen. Decoderfortschritt separat, höchstens
400 Videoframes/2.048 Pakete; bestehende Zeit-, Prozess- und Leselimits bleiben.

Rezeptorarbeitsbudget ist gleich; Crop und AREA sind nicht CPU-identische
Operationen. Vorverarbeitung wird separat gezählt, nicht als kostenlose oder
gleiche Arbeit ausgegeben. Im Worker höchstens ein Original-RGB-Puffer und
zwei Ausgabepuffer; keine vollständige Framefolge vorhalten. Der Originalframe
passt nicht in den vorhandenen 6.240.000-Byte-Übertragungsslot: Er bleibt im
Worker, nur jeweils ein 1920×1080-RGB-Bild wird übertragen. Prozessgrenzen
bleiben 1 GiB; diese Puffervorgabe ersetzt keinen späteren Ressourcenbeleg.

Keine Rohbildablage im Ergebnis. Neue Metadaten höchstens 65.536 Byte,
gemeinsame Zusatzhülle 262.144 Byte, Gesamt einschließlich aktiver Referenzen,
Wertetabellen und alternativer Fehlerabschlüsse höchstens 4.194.304 Byte.
Die vollständige konkrete Quellen-/Artefaktbilanz ist vor Qualifikation noch
zu binden; dieser Plan behauptet keine geprüfte Größenkonformität.

Jetzt keine Implementierung, Qualifikation oder Ausführung. Historische
Decoderstände nicht als heutige Zulassung übernehmen. Gates False;
ME/MI gesperrt, Prognosezweig ruhend. Keine neue Memoryregel oder Fokuslösung.
