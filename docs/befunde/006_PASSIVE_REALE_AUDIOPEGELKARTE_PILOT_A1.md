# Befund 006: Passive reale Audiopegelkarte, Pilot A1

## 1. Status

Dieser Befund dokumentiert nur einen Pilotlauf mit bereits laufendem externem
Audio. Die vollständige
[Methodik 006](../methodik/006_PASSIVE_REALE_AUDIOPEGELKARTE.md) ist damit
nicht ausgeführt und nicht bestätigt.

Unmittelbar vor dem Lauf wurden Dauer, Rohdatengrenze und die festen
Beobachtungspegel `0.001`, `0.002`, `0.005`, `0.010` und `0.020` angekündigt.

## 2. Ausführung

```text
Bedingung:      externes Audio läuft
Dauer:          5.0 Sekunden
Fenster:        500
Fensterdauer:   0.01 Sekunden
Abtastrate:     48000 Hz
Überläufe:      0
Rohdaten:       nicht gespeichert
```

## 3. Kontinuierliche R0-Aggregate

```text
Kanal     Minimum       Maximum       Mittel
200 Hz    0.00031534    0.08612553    0.02068105
400 Hz    0.00041950    0.21848443    0.02379415
800 Hz    0.00009098    0.04469291    0.00549490
```

Quantile:

```text
Kanal     q05       q25       q50       q75       q95       q99
200 Hz    0.00190   0.00484   0.01500   0.03387   0.05345   0.07699
400 Hz    0.00119   0.00382   0.00875   0.02588   0.11703   0.16149
800 Hz    0.00038   0.00115   0.00232   0.00768   0.02007   0.03193
```

## 4. Feste Pegelbeobachtung

Fenster oberhalb der jeweiligen Grenze:

```text
Grenze    200 Hz    400 Hz    800 Hz
0.001       495       482       396
0.002       470       445       283
0.005       371       327       165
0.010       291       236        94
0.020       216       157        26
```

Positive Übergänge:

```text
Grenze    200 Hz    400 Hz    800 Hz
0.001         5        17        71
0.002        28        40        66
0.005        41        44        37
0.010        31        39        37
0.020        29        34        19
```

## 5. Enger Befund

Das laufende externe Audio erzeugt eine breite, zeitlich wechselnde
kontinuierliche Frequenzlage. Der 400-Hz-Kanal erreicht die höchsten Spitzen,
der 200-Hz-Kanal den höchsten Median und der 800-Hz-Kanal bleibt schwächer,
aber klar aktiv.

Der bisherige synthetische Standardwert `0.5` liegt über sämtlichen beobachteten
Maxima und muss deshalb in diesem realen Lauf stumm bleiben. Das erklärt den
B2/B3-Nullbefund aus dem ersten Mikrofonkontakt.

## 6. Nicht gezeigt

Ohne A0 und A0R ist nicht bekannt, welcher Anteil auf Raumgrundpegel,
Mikrofonrauschen oder das abgespielte Audio entfällt. Ohne A1R ist die
Wiederholbarkeit nicht bekannt. Ohne A2/A2R ist keine Abstandsstabilität
gezeigt.

Insbesondere ist keine der fünf Pegelgrenzen als natürliche oder organische
Schwelle freigegeben.

## 7. Evidenz

**E1 für die technische Erfassung eines realen externen Audiokontakts.**

**E0** für robuste Ereignisgrenzen, MCM-Neuronen, auditive Feldkopplung und
Feldintelligenz.

## 8. Bester nächster Schritt

Das externe Audio wird vollständig gestoppt. Danach werden zwei getrennte
Fünf-Sekunden-Läufe A0 und A0R unter möglichst unveränderter Raum- und
Mikrofonlage aufgenommen. Erst dieser Gegenbefund zeigt, welche Teile der
Pilotverteilung tatsächlich über dem lokalen Grundpegel liegen.
