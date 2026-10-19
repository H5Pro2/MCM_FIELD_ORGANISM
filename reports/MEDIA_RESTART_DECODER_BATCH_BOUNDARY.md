# Mediencheckpoint: belegte Decoder-Batchgrenze

2026-09-13, DATEIBETRIEB-CHECKPOINT-BEDIENUNG.
Bezugscommit 537109994cf777f8d36cda617aafe12226806c25 plus vorhandene Entwürfe.
Nur Quelltext-/Metadatenprüfung und Dokumentation; keine Bibliotheksimports,
keine Medienöffnung, keine Qualifikation und kein Decoderexperiment.

## Konkreter Aufrufpfad

Der Entwurf `tools/_media_restart_work.py`, `Decoder._frames`, ruft nach
einer Ein-Platz-Vorprüfung `packet.decode()` auf und zählt anschließend die
gesamte zurückgegebene Liste. Das erfüllt keine belegte Batchreservierung.

Die lokal installierten PyAV-Dateien unter `.venv/Lib/site-packages/av` zeigen:

- `codec/context.pyx:432`, `decode`: ruft `_send_packet_and_recv` auf und
  liefert eine Liste. Kein Argument für maximale Ausgabeanzahl.
- `codec/context.pyx:333`: `_send_packet_and_recv` sendet ein Paket und
  sammelt in einer Schleife alle verfügbaren Frames. Kein Aufruf unseres
  Python-Budgetprüfers zwischen den Ergebnissen.
- `codec/context.pyx:356`: `_recv_frame` verwendet `avcodec_receive_frame`;
  Abbruch der Ausgabe erfolgt bei EAGAIN oder EOF. Beide Funktionen sind
  `cdef`, keine regulär aufrufbaren Python-Methoden dieser Schnittstelle.
- `container/input.pyx:188`: nach dem Demuxende werden leere Pakete für
  die ausgewählten Streams ausgegeben. Das nachgelagerte `drain` erreicht
  daher auch verzögerte Decoderframes. Ein kleiner oder leerer Paketpayload
  begründet keine kleine Ausgabezahl.
- `video/codeccontext.pyi`: `decode(...) -> list[VideoFrame]`; kein
  Decoder-Gegenstück zur einzeln liefernden Encoderfunktion `encode_lazy`.

Lokale Dateien, SHA-256:

| Datei | Hash |
| --- | --- |
| codec/context.pyx | 9f8d1a18190cbbff7a31373a86f25edf7261c6fc7e96319c1f17d0a6fbe916bf |
| codec/context.cp314-win_amd64.pyd | e96fe3593a87ffbce4ecc5c96579d65c7aaf31350ba460ee9901c8da60fcdb52 |
| container/input.pyx | b296e1436cd055da3344db10849b2869febc78ba1b403a6700ead18089e27cda |

Die Paketmetadaten nennen PyAV 16.1.0. Quelltextbeilage und Binärdatei sind
separat identifiziert; dies ist kein reproduzierbarer Buildnachweis für die
Binärdatei. Die gleichen maßgeblichen Listen-/Receive-Schleifen stehen im
[offiziellen v16.1.0-Quelltext](https://github.com/PyAV-Org/PyAV/blob/v16.1.0/av/codec/context.pyx).

Die [FFmpeg-8.0-API-Beschreibung](https://ffmpeg.org/doxygen/8.0/group__lavc__encdec.html)
erlaubt null, eine oder mehrere Ausgaben pro Eingabe und verzögerte Ausgabe
beim Drain. Sie gibt hier keinen numerischen Batchdeckel vor. Daraus folgt
keine unbegrenzte reale Ausgabe, sondern eine fehlende nutzbare Vorabzahl.

## Genau fehlender Nachweis

Es fehlt eine für den gebundenen Bitstream UND Codeczustand bewiesene
Obergrenze der pro `decode()` zurückgegebenen Frames, separat für Audio,
Video und Flush. Dazu wären insbesondere Paket-/Access-Unit-Struktur,
verzögerter Bestand und tatsächlich verwendete Decoderkonfiguration zu
berücksichtigen. Die vorhandene Quellenform bindet Größe, Hash, Streams,
Zeiten, Bildmaße und mittlere Bildrate, aber keine solche Batchinvariante.
`thread_count=1`, Paketbytegrenze, Bildrate, Containerframezahl oder das
Prozess-RAM-Limit liefern sie für sich nicht. Eine gemessene maximale Liste
aus endlich vielen Testaufrufen wäre ebenfalls kein solcher Nachweis.

Ein äußerer Python-Wrapper kann die interne Schleife weder unterbrechen
noch ihre nächste Ausgabe vorab reservieren. Das bloße Reservieren des
gesamten Restbudgets macht eine größere Liste nicht unmöglich. Nachzählen,
Abschneiden oder Workerabbruch wären keine Erfüllung der verlangten Garantie.

## Entscheidungspunkt und übriger Stand

Der konkrete Blocker liegt an der bestehenden hochstufigen Decoder-API,
nicht an Memory oder der MCM-Architektur. Mit den derzeitigen Bindungen ist
eine belastbare Batchzahl nicht herleitbar. Es wird keine universelle
Unmöglichkeit eines codec-/bitstreamspezifischen Beweises behauptet.

Eine technisch andere Anschlussgrenze wäre einzeln budgetierter Empfang über
FFmpegs Send-/Receive-API. Das erforderte jedoch einen kontrollierten nativen
Bibliotheksanschluss oder eine Änderung am PyAV-Binding, nicht nur einen
lokalen Aufruf von `packet.decode()`. Dabei müsste ausdrücklich zwischen
ausgegebenen Frames und intern erledigter Decoderarbeit unterschieden werden.
Ein solcher Eingriff oder eine Änderung der Arbeitsdefinition wurde hier
nicht vorgenommen. Ebenso keine Decoderkonstante erfunden.

Die gemeinsame verlustfreie Referenzierung ist freigegeben und prinzipiell
lokal umsetzbar, aber noch nicht fertiggestellt oder qualifiziert. Sie löst
den unabhängigen Decoderblocker nicht. Die frühere 11,5-MB-Oberreservierung
bleibt ein Befund über vollständige Mehrfachkopien, keine Größenprognose
für eine noch nicht implementierte Referenzdarstellung.

Der Gesamtanschluss bleibt NOT_READY. Qualifikationsfreigabe unverbraucht;
MAIN_GATE und QUALIFIED im Entwurf bleiben False. Kein realer Videolauf.
Keine historischen Dateien oder Produktmodule in dieser Prüfung geändert.
