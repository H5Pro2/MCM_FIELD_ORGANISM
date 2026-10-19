# Decoder-Isolation: Prozess- und Joblimit getrennt freigeben

Statische Vorprüfung des neuen Isolationsauftrags. Keine Codeänderung,
Qualifikation, Medienverarbeitung oder Diagnoseausführung.

## Vorhandene Bindung

`tools/_s2oe_media_decoder.py:20–25` verlangt PyAV **16.1.0** und folgende
FFmpeg-Bibliotheksversionen: libavutil 60.8.100, libavcodec 62.11.100,
libavformat 62.3.100, libavdevice 62.1.100, libavfilter 11.4.100,
libswscale 9.1.100, libswresample 6.1.100. Keine neue Importmessung durchgeführt.

Video: ein Decoderthread, native 3840 × 2160, 30000/1001 fps, Zeitbasis
1/30000. Zwei getrennte Container für Video/Audio; Audio 48 kHz stereo.
RGB-Konvertierung auf 1920 × 1080 mit AREA und fest gebundener Farbumrechnung.
Diese Einstellungen bleiben für beide vorgeschlagenen Arme unverändert.

`tools/_s2oe_decoder_worker.py:107–117` aktiviert **beide** voneinander
unabhängigen Commitgrenzen: Prozess und Job, jeweils 536.870.912 Byte.
Der Worker bestätigt beide Grenzen zusätzlich vor Medienzugriff.

## Bedeutung der gespeicherten Meldung

Die letzte Diagnose enthält ausschließlich Meldung **9**. Das ist
`JOB_OBJECT_MSG_PROCESS_MEMORY_LIMIT`; Meldung **10** bezeichnet dagegen
`JOB_OBJECT_MSG_JOB_MEMORY_LIMIT`.

Quellen: [Microsoft-Konstanten](https://github.com/microsoft/hcsshim/blob/main/internal/winapi/jobobject.go)
und [Microsoft-Dokumentation der Jobmeldungen](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_associate_completion_port).

Die bisherige Bezeichnung „Job-Limitmeldung“ bezeichnete den Transport
über den Jobkanal, nicht präzise die verletzte Grenzart. Die Meldung betrifft
hier das **Prozesslimit**. Ihr kausaler Zusammenhang mit dem gespeicherten
`av.error.InvalidDataError` bleibt weiterhin unbelegt.

## Notwendige Entscheidung vor Ausführung

Die aktuelle Freigabe nennt 1024 MiB **Job-Commit**, erhöht aber nicht
ausdrücklich das separate Prozesslimit. Ein Arm mit 512 MiB Prozesslimit
und 1024 MiB Joblimit ließe die tatsächlich gemeldete Prozessgrenze unverändert.
Er würde nur die Jobgrenze isolieren; daraus wäre kein geeigneter Gegenversuch
zur beobachteten Prozesslimitmeldung ableitbar.

Vorschlag: diagnostisch zwei feste Paare binden:

- Referenz: Prozess **512 MiB**, Job **512 MiB**.
- Gegenarm: Prozess **1024 MiB**, Job **1024 MiB**.

Nur frische, nacheinander ausgeführte Diagnoseworker, je ein erster
Fensteraufruf. Systemdefaults bleiben 512 MiB. Vor der späteren Ausführung
verfügbaren Commitspielraum und RAM prüfen; die Rechnerverträglichkeit ist
jetzt noch nicht gemessen. Native Fehlerdiagnostik erst anschließend
implementieren und neutral prüfen. Keine Freigabe aus dieser Notiz ableiten.

**RÜCKMELDUNG ERFORDERLICH:** Darf ausschließlich im höheren Diagnosearm
auch das Prozess-Commitlimit auf 1024 MiB gesetzt werden? Bis zur Antwort
keinen der beiden Einmalaufrufe verbrauchen. Historische Belege unverändert.
