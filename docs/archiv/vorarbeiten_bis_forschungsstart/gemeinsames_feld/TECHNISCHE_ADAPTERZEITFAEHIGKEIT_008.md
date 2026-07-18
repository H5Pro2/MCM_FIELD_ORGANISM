# Technische Adapterzeitfähigkeit 008

## Status

Technische Voruntersuchung vor `GF_001`.

Die Prüfung fragt ausschließlich, welche Zeitinformationen die konkret
verwendeten Audio- und Video-Backends an der angeschlossenen Hardware
tatsächlich liefern. Drei unabhängige endliche Läufe wurden ausgeführt. Pro
Lauf wurden 30 Audio-Callbacks und 10 Kameraframes geprüft.

Es wurde kein Feldschritt ausgeführt, kein Rohsignal gespeichert und keine
zeitliche Stütze geschätzt.

## Audio

Verwendete Strecke:

```text
Mikrofoneingang
-> PortAudio
-> sounddevice callback
```

PortAudio meldet eine Eingangslatenz von `30 ms`. Im Callback werden die
Felder `inputBufferAdcTime` und `currentTime` exponiert. Ihre bloße Existenz
reicht jedoch nicht als Quelluhr.

In allen drei Läufen zeigte `inputBufferAdcTime` wiederholt:

```text
0,00 s -> 0,01 s -> 0,02 s -> 0,00 s
```

Damit betrug der kleinste Folgeschritt `-20 ms`; die Folge war in keinem Lauf
streng monoton. `currentTime` blieb im Callback bei `0`. Beide Angaben sind in
dieser konkreten Backendstrecke daher nicht als fortlaufende Aufnahmeuhr
verwendbar.

Der derzeitige produktive Audioadapter arbeitet zudem blockierend mit
`InputStream.read()`. Er erhält `inputBufferAdcTime` überhaupt nicht.

## Video

Verwendete Strecke:

```text
Kamera
-> DirectShow
-> OpenCV
```

In allen drei Läufen galt:

| Metadatum | Beobachtung | Zeitlich verwendbar |
|---|---:|---|
| `CAP_PROP_POS_MSEC` | `-1` | nein |
| `CAP_PROP_PTS` | `-1` | nein |
| `CAP_PROP_EXPOSURE` | `-4` | nein, nur Einstellwert |
| Belichtungsdauer | nicht geliefert | nein |

Die technischen `read()`-Dauern lagen über alle Läufe zwischen `177,577 ms`
und `216,807 ms`; die Laufmediane lagen zwischen `196,340 ms` und
`199,926 ms`. Diese Dauer beschreibt den blockierenden Softwarezugriff, nicht
Beginn und Ende der Bildaufnahme.

## Kontrollen

Sechs synthetische Kontrollen zeigen:

1. monotone Audiozeiten werden als technisch nutzbar erkannt,
2. rückspringende Audiozeiten bleiben trotz exponiertem Feld unbrauchbar,
3. konstante Streamzeit wird nicht als Uhr ausgegeben,
4. negative Videozeitwerte gelten nicht als Zeitstempel,
5. konstante Videozeit ist nicht monoton,
6. der öffentliche Vertrag enthält keine Feldwirkung, Halteregel oder
   Bedeutung.

## Befund

Die reale Hardwarestrecke liefert derzeit keine belastbare, fortlaufende
Erfassungszeit, mit der Audio- oder Videozustände auf
`organism.monotonic_ns` gestützt werden können.

```text
exponiertes Zeitfeld
!= verwendbare Quelluhr
!= Weltstütze auf der Organismusuhr
```

Die gemeldete Audiolatenz darf ohne verwendbare Quelluhr nicht rückwärts vom
Read-Ende abgezogen werden. Ebenso dürfen nominelle Bildrate,
Kamera-Lesedauer oder Belichtungseinstellung nicht als Aufnahmeintervall
eingesetzt werden.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Die nächste Prüfung muss deshalb nicht weitere Zeitmetadaten aus denselben
Backends suchen. Sie muss klären, ob ein transparenter äußerer
Erfassungszeitvertrag aus bekannten Audio-Sampleblöcken und explizit
abgeschlossenen Kameraframes möglich ist, ohne Gleichzeitigkeit oder
Gültigkeitsdauer zu erfinden.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.
