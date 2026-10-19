# Visuelle Eingangskonsistenz: begrenzte Vorbereitung

Nur statischer Plan, keine Ausführungsfreigabe oder neue Laufnummer.
Der Versuch `media-memory-video-20260912-01` ist unverändert geschlossen:
technisch vollständig, Fast-/Audiofortschreibung belegt, vier Enthaltungen.
Audio-Konkurrenz bleibt geschlossen; kein Retry und keine Regeländerung.

## Quelle und feste Auswahl

Dieselbe bereits untersuchte Datei:
`C:\Users\TV\Downloads\17138816-uhd_3840_2160_30fps.mp4`.
SHA-256: `df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
Keine andere Quelle oder Auswahl nach Bildinhalt. Fensterstarts 1,0 und
4,0 Sekunden; Auswahl weiterhin letzter Frame am oder vor 1,05 bzw. 4,05 s.
Native Zeitbasis 1/30000, Rate 30000/1001; keine Gleichsetzung mit 30 fps.

Zwei getrennte frische Videodekodierungen derselben Quelle ab Anfang:
Referenz und Wiederholung. Beide liefern die zwei festgelegten Frames.
Keine Übernahme dekodierter Frames zwischen den Durchgängen und kein
ergebnisabhängiges Suchen. Keine Audioanalyse, NJ-, Feld- oder Memoryaufrufe.

## Getrennte Vergleichsstufen

1. Quellenhash, Stream, Original-PTS/Zeitbasis, vorheriger ausgewählter und
   nächster Framezeitpunkt sowie Auswahlzentrum binden. Die beiden
   Auswahlentscheidungen je Zeitpunkt müssen getrennt nachvollziehbar sein.
2. Native Frameform, Pixelformat, Farbmetadaten und aktive Bildzeilen je
   Plane vergleichen. Padding nicht als Bildinhalt behandeln; Packvorschrift
   vor Ausführung festlegen. Keine RGB-Konvertierung als Rohframe ausgeben.
3. Bestehende Konvertierung unverändert: 1920x1080 rgb24, AREA,
   src/dst colorspace 1, MPEG nach JPEG. Konvertierte RGB-Bytes separat binden.
4. Je ausgewähltem Frame vollständige 288 Rezeptorwerte mit unverändertem
   VisualGridConfig erzeugen. Referenz/Wiederholung bitweise vergleichen;
   Zeit-/Snapshotidentitäten getrennt von numerischer Wertegleichheit halten.
5. Auf einer Kopie jedes konvertierten Frames exakt die bestehende
   Cue-Okklusion anwenden: Zell-/Kanalpositionen 32 bis 287 auf null.
   Danach erneut denselben Rezeptor anwenden. Nur Werte 0 bis 31 gegen
   den jeweiligen vollständigen Eingang vergleichen. Verdeckte Werte werden
   diagnostisch gespeichert, nicht als Teilhinweiseingang verwendet.

Keine Toleranz oder neue Distanzschwelle. Abweichende Positionen und gespeicherte
Binary64-Werte ausweisen; Fehlerursachen nicht allein aus Digestunterschieden
ableiten. Gleichheit gilt nur für die geprüften Stellen und Implementierung.
Eine Abweichung auf einer früheren Stufe bleibt sichtbar, auch wenn eine
spätere Projektion gleiche Werte ergibt.

## Umfang und Anschlusslücke

Zwei Decoderöffnungen, vier ausgewählte Frames, vier vollständige und vier
okkludierte visuelle Analysen: acht Analysen, 2.304 gespeicherte Rezeptorwerte.
576 Wertepaare für Wiederholung, 128 für sichtbare Okklusionserhaltung.
Decoderfortschritt und vier ausgewählte Frames getrennt zählen. Eine native
Framevorhaltung mit bestehendem Lookahead; höchstens zwei RGB-Puffer zugleich.
Keine Rohbildablage; nur Werte, Metadaten und Payloadbindungen aufzeichnen.

Bestehende Anschlüsse: `_s2oe_media_decoder.py` (Auswahl/Konvertierung),
`_s2oe_media_session.py` (Okklusion), `finite_video_path.py` (Rezeptor).
Der jetzige Decoder-Selektor koppelt Video und Audio. Benötigt wird ein
kleiner separater diagnostischer Videozugang mit denselben Auswahl- und
Konvertierungsregeln, nicht der unveränderte Memory-Haupteinstieg.
Native aktive Plane-Bytes sind bislang kein eigenständiger Beleg.
Diese beiden Anschlüsse sind noch nicht implementiert oder qualifiziert.
Vor Ausführung müssen ihre Quellenbindungen und vollständige Belegbilanz
innerhalb vorhandener Grenzen feststehen; keine neue Budgetfreigabe impliziert.

## Interpretation

Wiederholbarkeit und Okklusionserhaltung werden unabhängig bewertet.
Bestehen beide, ist damit weder Speichererhaltung noch Abruf zugesichert.
Scheitert eine Stufe, ist das eine lokale Eingangsabweichung, noch kein
Memoryfehler. Insbesondere ersetzt ein künftiger Kontrollwert keinen fehlenden
historischen Einzelwert. Keine Behauptung einer bereits nachgewiesenen Ursache.
Gates False; keine Ausführung, Fokusfunktion oder neue Repräsentation.
