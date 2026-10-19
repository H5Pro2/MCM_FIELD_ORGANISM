# Lokaler Videozugang: Quellenprüfung und Anschlussgrenze

## Tatsächlich geprüft

Repository-HEAD erneut gelesen:
`537109994cf777f8d36cda617aafe12226806c25`. Vorhandener Arbeitsstand bleibt
zusätzlich relevant; keine Sicherung als Commit ausgegeben.

- Datei: `C:\Users\TV\Downloads\17138816-uhd_3840_2160_30fps.mp4`
- Aktuelle Größe: **83.498.438 Byte**.
- SHA-256: `df0986f384e156c4dfec234e94b6f6baa3d0f8a9cfd7ba81f14aadf0313450aa`.
- Vorab gebundener Ausschnitt: **[0, 5) Sekunden**, ohne Rezeptorbewertung.
- Containerdauer: 26.751.667 Mikrosekunden laut Demuxer.
- Video, Stream 0: H.264, 3.840 x 2.160, YUV420P, Zeitbasis 1/30000,
  mittlere Bildrate **30000/1001**, 801 deklarierte Frames, Start-PTS 0.
- Audio, Stream 1: AAC, Stereo, 48.000 Hz, FLTP, Zeitbasis 1/48000,
  Start-PTS 0; 1.284.080 deklarierte Audioticks.

Decoderzugang ist vorhanden in `.venv/Scripts/python.exe`: PyAV 16.1.0,
libavcodec 62.11.100, libavformat 62.3.100, libavutil 60.8.100,
libswscale 9.1.100, libswresample 6.1.100. Im zuvor verwendeten globalen
`C:/Python314/python.exe` fehlt hingegen das Paket `av`; keine Installation
oder globale Umstellung vorgenommen.

Eine begrenzte Zugangsprobe erreichte nach 18 demuxten Paketen je einen
ausgegebenen Video- und Audioframe bei PTS 0. Das Audiopaket ergab 1.024
Samples; das Video meldete Colorspace 1 und Color-range 1. Die Probe war
auf 64 Demuxpakete begrenzt und wurde nach beiden Modalitäten beendet.
Keine RGB-/PCM-Ausgabe erzeugt, kein vollständiges Fünf-Sekunden-Intervall
dekodiert. Interne Codec-Reorder-/Referenzpuffer sind dadurch nicht vermessen.
Keine Rezeptoren, NJ-, Memory-, Feld- oder Runtimeaufrufe. Dies ist eine
Quellen-/Decoderprobe, keine Anschlussqualifikation.

## Konkret vorbereitete Umsetzung

Quelle vor Start erneut gegen Hash prüfen; ausschließlich Stream 0 und 1
verwenden. Kanalzuordnung und PTS aus dem Container erhalten, keine Zeitbasis
aus dem Dateinamen ableiten. Vorgesehen: RGB24 bei 1.920 x 1.080 durch fest
gebundene Flächenverkleinerung; Farbkonversion und Decoderidentität separat
binden. Audio ohne Lautheitsnormalisierung: explizit `0.5 * (L + R)`, danach
einmal Float32-Ausgabe, 48.000 Hz unverändert, in 4.800-Sample-Fenstern.
Kein Clipping oder Ersatzsignal. Details sind Anschlussvorgaben, nicht bereits
numerisch qualifizierte Konversionen.

Begrenzte Puffer vorsehen: ein ausgegebener Quellframe, ein RGB-Zielframe,
höchstens zwei fertige Audiofenster; keine Liste des ganzen Videos. Codec-
internen Speicher und Paketgrößen zusätzlich begrenzen und messen, bevor eine
vollständige Speicherobergrenze behauptet wird. Ein Framezähler allein genügt
dafür nicht. Start öffnet nur diese Datei, Status liest Fortschritt, Stopp
schließt Container/Decoder und verwirft unverarbeitete Puffer ohne Neustart.

## Konkreter Blocker für den bestehenden Systemanschluss

**Die Datei ist nicht das Problem. Die vorhandene native Zeitbindung passt
nicht unmittelbar zu ihren tatsächlichen Zeitstempeln.**

`tools/_s2ob_private_caller_binding.py:90` und `bind_input` verlangen exakt
30-Hz-Videofenster und 200-ms-Ereignisschritte. Die Quelle liefert laut
Streambindung 30000/1001 Bilder pro Sekunde. Original-PTS dürfen nicht als
30-Hz-Indizes umetikettiert werden. Erforderlich ist eine getrennt versionierte
Zuordnung von Medienzeit zu Systemzeit; deren Ereignisauswahl muss vorab stehen.

Auch jede 200-ms-Stelle des gesamten Fünf-Sekunden-Ausschnitts als Formation
zu verwenden wäre keine zulässige Abkürzung: Das wären 25 Formationen schon
im ersten Durchlauf, gegenüber aktuell maximal 20 für die ganze Sitzung.
Hinweise und zweiter Durchlauf kämen hinzu. Der Auftrag hebt diese Grenzen
nicht auf. Eine dünnere Abtastung wäre möglich, aber dann keine lückenlose
Verarbeitung aller Videoframes und Audiofenster; diese Unterscheidung muss
explizit gebunden werden. Medienweiterlauf und Memory-Ereignisrate sind
verschiedene Größen.

Der historische Containerhelfer
`mcm_field_organism/public_av_container_source.py:99` sammelt zudem Frames und
Audiowerte in Listen. Er ist daher kein ungeprüft wiederzuverwendender
fortlaufender Decoder für den geforderten begrenzten Pufferbetrieb.

## Nächster zulässiger Anschluss

Kleinste Richtung: zeitgestempelten Dateieingang von der begrenzten
Memory-Abtastung trennen. Original-PTS bleiben Herkunft; eine neue feste
Auswahl-/Zeitzurechnung führt nur vorab bestimmte Stellen in den bestehenden
Halbprofilpfad. Kein Anheben der Kernlimits, kein historischer Validatorwechsel.
Vor neutraler Qualifikation müssen diese Auswahl und ihre Zuordnung zu den
beiden Durchläufen eindeutig feststehen. Die frühere Acht-Stellen-Skizze ist
noch kein vollständiger Zeitvertrag für diese konkrete Datei.

**Status:** Quelle und Decoderzugang bestätigt; native Anschlussqualifikation
noch nicht ausgeführt. Keine frühere Passzahl übertragen und kein Lernlauf
gestartet. RÜCKMELDUNG ERFORDERLICH: die explizite Medienzeit-/Ereignisauswahl
als kleinste notwendige Anschlussentscheidung festlegen, nicht den Dateipfad
erneut anfragen.
