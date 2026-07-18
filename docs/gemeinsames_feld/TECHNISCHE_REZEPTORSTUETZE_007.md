# Technische Rezeptorstütze 007

## Status

Technische Voruntersuchung vor `GF_001`.

Diese Prüfung trennt für Audio und Video:

1. das Quellfenster des reduzierten Zustands,
2. die nominelle Ausgaberate,
3. die gemessene Dauer des technischen Reads,
4. eine bisher nicht belegte zeitliche Weltstütze auf der Organismusuhr.

Es wird kein Feldschritt ausgeführt und keine Gültigkeits- oder Halteregel
ergänzt.

## Auditive Rezeptorstütze

Der auditive Zustand entsteht aus einem rollenden FFT-Analysefenster:

| Rolle | Wert |
|---|---:|
| Sample-Rate | 48.000 Hz |
| Quellfenster | 4.800 Samples = 100 ms |
| Ausgabeschritt | 480 Samples = 10 ms |
| Fensterüberlappung | 90 % |
| realer Read, Minimum | 0,9853 ms |
| realer Read, Median | 1,8915 ms |
| realer Read, Maximum | 32,2742 ms |

Das Quellfenster beschreibt tatsächlich 100 ms Audiosamples. Sein genauer
Beginn und sein Ende auf `organism.monotonic_ns` sind jedoch nicht gemessen.
Der kurze technische Read liefert gepufferte Samples und ist deshalb nicht
die zeitliche Stütze des analysierten Weltkontakts.

## Visuelle Rezeptorstütze

Der visuelle Zustand entsteht aus genau einem gelieferten Kameraframe:

| Rolle | Wert |
|---|---:|
| Quellrolle | Frame-Identitätsintervall |
| nominelle Frameperiode | 33,333 ms |
| belegte Belichtungsdauer | keine |
| realer Read, Minimum | 35,4138 ms |
| realer Read, Median | 197,1143 ms |
| realer Read, Maximum | 210,7136 ms |

`frame_index .. frame_index + 1` ist nur eine technische Identität. Die
nominelle Frameperiode ist keine gemessene Belichtungsdauer. Auch der deutlich
längere blockierende Kamera-Read belegt weder Aufnahmebeginn noch
Wahrnehmungsgültigkeit des gelieferten Bildes.

## Kontrollen

Sechs synthetische Kontrollen zeigen:

1. Audiofenster, Schrittweite und Überlappung werden korrekt rekonstruiert,
2. die visuelle Frameperiode wird nicht als Belichtungsstütze ausgegeben,
3. Read-Dauer wird nie zur Weltstütze erklärt,
4. instabile Quellschritte werden abgewiesen,
5. falsche Quelluhren werden abgewiesen,
6. der öffentliche Vertrag enthält keine Halte- oder Feldwirkungsrolle.

## Befund

Audio besitzt eine bekannte zeitliche Stütze auf seiner Sample-Uhr, aber noch
keine belastbare Abbildung dieser 100 ms auf die Organismusuhr.

Video besitzt derzeit weder auf der Frame-Uhr noch auf der Organismusuhr eine
belegte Belichtungs- oder Gültigkeitsdauer.

```text
Quellfenster
!= Read-Dauer
!= Feldwirkungsdauer
```

Die frühere Bezeichnung `CommonFieldTime` darf daher nur als gemessenes
technisches Koordinationsintervall gelesen werden. Sie beweist keine
gleichzeitige oder gleich lange Weltstütze mehrerer Rezeptorzustände.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Vor weiterer Feldzeitmechanik muss geprüft werden, welche Zeitinformationen
die realen Audio- und Kameraadapter tatsächlich liefern können:

- Aufnahme- oder ADC-Zeitstempel,
- Gerätepuffer- und Latenzinformation,
- Frame-Erfassungszeit oder Belichtungsmetadaten,
- Stabilität dieser Angaben über wiederholte Läufe.

Wenn ein Adapter diese Informationen nicht liefert, muss die Unsicherheit
offen bleiben. Sie darf nicht durch nominelle Rate, Read-Dauer oder Halten des
letzten Zustands ersetzt werden.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.
