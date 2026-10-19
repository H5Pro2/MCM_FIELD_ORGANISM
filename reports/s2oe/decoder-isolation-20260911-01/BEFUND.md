# Decoder-Isolationsvergleich: Speicherabhängigkeit gestützt

## Umfang und Abschluss

`decoder-isolation-neutral-20260911-01`: genau einmal **6/6 bestanden**.
Danach unter `decoder-isolation-20260911-01` je Arm genau ein
`select(1, 0)`, frische Worker nacheinander. Anschließend genau eine
unabhängige read-only Vergleichsprüfung: **EVIDENCE_VALID**.

Referenz: Prozess und Job jeweils 512 MiB. Diagnosegegenarm: beide jeweils
1024 MiB. Überlappende Grenzen, kein addiertes 2-GiB-Budget. Der Default
`COMMIT_BYTES` bleibt 536.870.912; bestehende Systemaufrufer wählen keinen
Diagnosearm. Keine Player- oder Systemzulassung durch diesen Vergleich.

Einheitlicher Decoder: PyAV **16.1.0**, FFmpeg **8.0.1**, in beiden Workern
dieselben gebundenen Bibliotheksversionen. Ein Video-Decoderthread, dieselben
Container, Puffer und RGB-Konvertierungen. Keine Optimierung eingebaut.
`_s2oe_media_decoder.py` blieb gegenüber der vorherigen Diagnose unverändert.

## Ergebnisse getrennt

| Befund | 512 MiB | 1024 MiB |
| --- | --- | --- |
| Status | NOT_EVALUABLE | DECODER_WINDOW_COMPLETE |
| letzte Phase | VIDEO / packet_decode | OUTPUT / write_shared_slot |
| native Fehlermeldungen | get_buffer() failed; no frame! | keine ERROR/FATAL-Meldungen |
| ursprüngliche Ausnahme | av.error.InvalidDataError | keine |
| errno | 1094995529 | entfällt |
| Prozesslimitmeldung (9) | vorhanden | keine |
| Joblimitmeldung (10) | keine | keine |
| Peak Process Commit | 528.822.272 Byte | 563.306.496 Byte |
| Peak Job Commit | 535.404.544 Byte | 569.888.768 Byte |
| Pakete | 4 | 12 |
| native Videoframes | 1 | 3 |
| Audioframes / Audiosamples | 0 / 0 | 5 / 5120 |
| ausgewählte AV-Fenster | 0 | 1 |

512 MiB: FFmpeg-Komponente `libav.h264` meldet zuerst `get_buffer() failed`,
danach `no frame!`. Der Originaltext der Ausnahme lautet
`Invalid data found when processing input`; Stack über Paketdecoder und
`_send_packet_and_recv`. Diese Meldung ist kein Nachweis einer beschädigten Datei.

1024 MiB: 4800 Mono-Float32-Samples (19.200 Byte) und ein RGB-Frame
1920 × 1080 × 3 (6.220.800 Byte) wurden geliefert, nur ihre Hashes und
Größen gespeichert. Frame-PTS **1001**, nächster PTS **2002**, Zeitbasis
1/30000; der Mittelpunkt 50 ms liegt dazwischen. Native 30000/1001 fps
wurden nicht in 30 fps umgedeutet.

## Aussage und Grenze

Erfolg ausschließlich mit höherem Limit, Prozesspeak oberhalb der bisherigen
Grenze und die Bufferfehlermeldung stützen **Speicherabhängigkeit dieses
Decoderpfads beim ersten Fenster**. Die fehlgeschlagene konkrete native
Allokation, deren Größe und die gesamte Codec-Pufferbelegung sind weiterhin
nicht rekonstruiert. Der beobachtete Peak ist keine universelle Bedarfsgrenze.

Eine reine Quellenbeschädigungsbehauptung ist nicht begründet. Ebenso wenig
ist bewiesen, dass das Weglassen zwischenzeitlicher RGB-Konvertierungen den
Engpass beseitigt. Dieser Kandidat bleibt getrennt; es wurde keine solche
Optimierung getestet. Aus dem Diagnosegegenarm folgt keine Freigabe für
größeren Speicher im Systembetrieb oder einen vollständigen Medienlauf.

Der nächste kleinste Korrekturschritt müsste den Decoderbedarf unter dem
bestehenden Systemlimit verringern und Auswahl/Pixelwerte erhalten. Welche
konkrete Änderung dafür ausreicht, ist mit diesem Vergleich noch offen.
Keine zusätzliche Speicherstufe oder automatische Folgeprüfung vorgesehen.

## Diagnosequalität und Qualifikation

Neutral erreicht: unveränderter Default, Ablehnung einer dritten Speicherstufe,
beide tatsächlich gesetzten und vom Worker bestätigten Grenzpaare,
native Fehlerweitergabe, ursprünglicher Fehlertext, abruptes Ende mit
erhaltener Meldung/Phase und explizite Logüberschreitung. Keine historischen
Testserien wiederholt.

Native ERROR/FATAL-Protokollierung in beiden Armen identisch über PyAVs
Logginganschluss; Wiederholungen nicht dedupliziert. Grenzen: 32 Meldungen,
32.768 Byte, Überschreitung ausdrücklich als unvollständige Diagnose markiert
und technisch abgewiesen. Hier kein Überlauf. Der PyAV-Anschluss selbst
formatiert Meldungen begrenzt; kein Anspruch auf vollständigen nativen
Debugtrace. [Gebundene PyAV-Implementierung](https://github.com/PyAV-Org/PyAV/blob/v16.1.0/av/logging.pyx).

## Ressourcen und Herkunft

Vorbedingungen vor neutraler Prüfung sowie vor beiden Medienarmen geprüft:
mindestens 3 GiB freier Commitspielraum und 2 GiB verfügbarer RAM.
Vor dem realen Referenzarm: 14.002.470.912 / 7.247.196.160 Byte;
vor dem Gegenarm: 13.087.711.232 / 7.201.476.608 Byte (Commitspielraum / RAM).
Das ist eine momentane Rechnerprüfung, keine zugesicherte Reservierung.

Je Arm 171.256.136 bestätigte Container-Lesebytes bei 83.498.438 Byte
Dateibestand. Beim fehlgeschlagenen Arm ist dies wegen unvollständiger
Zählerbestätigung nur ein Mindeststand; beim erfolgreichen Arm sind die
Lesecounter vollständig. Beide Zugänge prüfen den unveränderten Payloadhash
vor Containerverarbeitung. Keine Rohpayloadablage.

Code und vollständige Abschlussreserven vorab gebunden: **238.394 Byte**.
Ist vor Verifikationsdatei und Bericht: **68.514 Byte**, einschließlich
48.011 Byte aktiver Dateien und 10.159 Byte gemeinsamer Quellenbindung.
Verifikation und Bericht haben zusammen 24.576 Byte Reserve.

Bindungs-SHA-256:
`97ce7b1480c5e107964fc2a109a787e6e31d6ee8fdd498b3a94d31ae9518bcfd`.
Referenzbeleg:
`5df218d77ff217175a9a0bd077c9d84cd0668cea30dd32ff9bd2a6bb6c448e6c`.
Gegenarmbeleg:
`65a1036bd027e47f5ee4dde263141d9315f1e2b388707b0a37a30df52a09dd77`.

Beide Worker kontrolliert geschlossen. Exitcode 1 entsteht auch beim Erfolg
durch den bestehenden Jobabschluss, nicht als behaupteter Crash.
Keine Rezeptoren, NJ, Feld, Memory oder Runtime; keine Gates geöffnet.
Die unabhängige Prüfung liest nur Belege und Quellen-/Codebindungen, keine
Medien oder Decoder; keine numerische Pixel-/PCM-Rekonstruktion.
Historische Fehlerbelege bleiben unverändert. Beide Einmalaufrufe sind verbraucht.

**RÜCKMELDUNG ERFORDERLICH:** Entscheidung über den begrenzten nächsten
Decoder-Korrekturschritt; keine Systemgrenzänderung und kein Lernlauf freigegeben.
