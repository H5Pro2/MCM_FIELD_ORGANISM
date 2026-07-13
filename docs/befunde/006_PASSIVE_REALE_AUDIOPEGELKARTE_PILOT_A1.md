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

Nach diesem Pilotlauf wurde der Windows-Aufnahmepegel abgesenkt. Dadurch ist
Pilot A1 zusätzlich von allen späteren Läufen bei niedrigerem Pegel technisch
getrennt. Seine absoluten Werte dürfen nicht als Audio-gegen-Stille-Vergleich
verwendet werden.

Insbesondere ist keine der fünf Pegelgrenzen als natürliche oder organische
Schwelle freigegeben.

## 7. Evidenz

**E1 für die technische Erfassung eines realen externen Audiokontakts.**

**E0** für robuste Ereignisgrenzen, MCM-Neuronen, auditive Feldkopplung und
Feldintelligenz.

## 8. Nachfolgende Stilleläufe A0 und A0R

Der erste Versuch, A0 und A0R aufzunehmen, fiel mit der manuellen Änderung des
Windows-Aufnahmepegels zusammen und wurde deshalb nicht gewertet. Danach blieb
der abgesenkte Aufnahmepegel unverändert und beide Läufe wurden vollständig
wiederholt.

```text
Bedingung   Fenster   Überläufe   Mittel 200 Hz   Mittel 400 Hz   Mittel 800 Hz
A0             500            0      0.00001805      0.00001175      0.00000895
A0R            500            0      0.00001739      0.00001193      0.00000897
```

Maxima:

```text
Bedingung   200 Hz       400 Hz       800 Hz
A0          0.00005920   0.00003471   0.00002811
A0R         0.00007655   0.00003783   0.00002833
```

In beiden Läufen lagen sämtliche 500 Fenster aller drei Kanäle unter der
niedrigsten Beobachtungsgrenze `0.001`. Entsprechend entstanden an allen fünf
festen Grenzen exakt null positive und null negative Übergänge.

Die Mittelwerte der unabhängigen Stilleläufe unterscheiden sich um:

```text
200 Hz: 3.64 Prozent
400 Hz: 1.55 Prozent
800 Hz: 0.28 Prozent
```

Damit ist die technische Stillelage bei unverändertem Aufnahmepegel über zwei
Läufe eng reproduziert. Die unterschiedlichen Digests zeigen erwartungsgemäß,
dass die einzelnen Rauschfenster nicht identisch waren.

## 9. Aktualisierte Evidenz

**E1 für eine wiederholbare lokale Stillelage bei festem Aufnahmepegel.**

Noch keine Evidenz für die Trennung von Stille und externem Audio bei genau
diesem Pegel, weil Pilot A1 vor dessen Absenkung aufgenommen wurde.

## 10. Nachfolgende Audioabschnitte A1S1 und A1S2

Bei demselben unveränderten Aufnahmepegel wie A0/A0R lief externes Audio
kontinuierlich weiter. Zwei getrennte Streams erfassten zwei aufeinanderfolgende
Fünf-Sekunden-Abschnitte. Die zunächst technischen Laufbezeichnungen A1R und
A1R2 werden methodisch als A1S1 und A1S2 geführt, weil der Audioausschnitt
nicht an denselben Startpunkt zurückgesetzt wurde.

```text
Bedingung   Fenster   Überläufe   Mittel 200 Hz   Mittel 400 Hz   Mittel 800 Hz
A1S1            500            0      0.05215636      0.02890193      0.01079956
A1S2            500            0      0.06618502      0.03585016      0.01764080
```

Maxima:

```text
Bedingung   200 Hz       400 Hz       800 Hz
A1S1        0.34441030   0.19774881   0.12769694
A1S2        0.32071559   0.14427600   0.15572529
```

Fenster oberhalb der niedrigsten festen Beobachtungsgrenze `0.001`:

```text
Bedingung   200 Hz   400 Hz   800 Hz
A0               0        0        0
A0R              0        0        0
A1S1           497      498      470
A1S2           500      492      488
```

Damit trennt `0.001` in diesen vier Läufen technische Stille deutlich von den
beiden Abschnitten des externen Audios. Das ist noch keine natürliche Schwelle:
Die Grenze stammt aus der vorab festgelegten Beobachtungsfamilie und wurde noch
nicht gegen Abstand, andere Audios, Geräteeinstellungen oder unabhängige Tage
geprüft.

Die Audiomittelwerte unterscheiden sich zwischen A1S1 und A1S2 um rund 27,
24 und 63 Prozent. Das ist mit den unterschiedlichen Inhalten der fortlaufenden
Abschnitte vereinbar und darf nicht als mangelnde technische Reproduzierbarkeit
des Rezeptors ausgegeben werden.

## 11. Aktualisierte Evidenz

**E1 für die klare technische Trennung der gemessenen Stille- und
Audioabschnitte bei festem Aufnahmepegel.**

Noch **E0 bis E1** für die Wiederholung desselben äußeren Audiomusters, weil
kein identischer Ausschnitt wiederholt wurde.

Weiterhin **E0** für eine natürliche Spikegrenze, auditive Feldkopplung und
Feldintelligenz.

## 12. Bester nächster Schritt

Das Audio wird an einen bekannten Startpunkt zurückgesetzt und derselbe
Fünf-Sekunden-Ausschnitt zweimal gestartet. Aufnahmepegel, Lautstärke, Abstand
und Mikrofonlage bleiben unverändert. Erst danach folgt derselbe Ausschnitt bei
kontrolliert verändertem Abstand.
