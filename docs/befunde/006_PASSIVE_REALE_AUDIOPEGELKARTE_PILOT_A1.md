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

## 10. Bester nächster Schritt

Bei unverändertem aktuellem Windows-Aufnahmepegel wird das externe Audio erneut
gestartet und als A1R aufgenommen. Nur A1R gegen A0/A0R ist der gültige erste
Audio-gegen-Stille-Vergleich. Danach folgt eine unabhängige Audiowiederholung,
bevor der Abstand verändert wird.
