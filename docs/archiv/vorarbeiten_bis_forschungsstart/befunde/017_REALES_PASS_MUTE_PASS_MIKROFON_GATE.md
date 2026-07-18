# Befund 017: Reales Pass/Mute/Pass-Mikrofon-Gate

## 1. Kurzurteil

Das automatische Live-Gate führte denselben laufenden Mikrofonstream durch:

```text
20 Sekunden Pass
-> 20 Sekunden Mute für die Rezeptoren
-> 20 Sekunden Pass
```

Die Ventilatoren und die reale Umgebung liefen unverändert weiter. Das Gate
unterbrach ausschließlich den sensorischen Kontakt zur MCM.

Die auditive Kette folgte dieser Intervention kausal: Nach neun
Übergangsfenstern wurde die Rezeptorlage exakt null, der B1-Nachhall relaxierte
und nach erneuter Öffnung erschien nahezu dieselbe verteilte reale
Umgebungslandschaft wieder.

## 2. Technischer Aufbau

```text
Gerät:                 Mikrofon (USB PnP Device(Echo-058))
Treiberpfad:           Windows WASAPI, Geräteindex 9
Abtastrate:            48.000 Hz
Chunk:                 480 Samples / 10 ms
Rezeptorfenster:       100 ms
Rezeptorbänder:        48 logarithmische Bänder
Phasen:                20 s Pass / 20 s Mute / 20 s Pass
Gesamtchunks:          6.000
vollständige Lagen:    5.991
Audioüberläufe:        0
```

Während Mute wurden die realen Hardwarechunks weiter gelesen, sofort verworfen
und durch exakte Nullchunks ersetzt. Es wurden keine Rohsamples gespeichert.

## 3. Rezeptorantwort

| Passphase | Lagen | mittlere aktuelle Rezeptorenergie |
|---|---:|---:|
| Pass 1 | 1.991 | 0,066397 |
| Pass 2 | 2.000 | 0,066437 |

Die Mute-Phase wird getrennt ausgewiesen:

| Schicht | Umfang | aktuelle Rezeptorwirkung |
|---|---:|---:|
| Gate-Ausgabe | 2.000 Chunks | exakt null |
| Übergang des 100-ms-Rezeptorfensters | 9 Lagen | Mittelwert 0,043497 |
| stabile Rezeptorlage | 1.991 Lagen | exakt null |

Die Übergangslagen sind zeitlich begrenzte Fensterreste. Während der stabilen
Mute-Lage existiert keine aktuelle Rezeptorwirkung.

## 4. Wiederkehr der realen Umgebungslandschaft

Die mittleren verteilten Pass-Spektren waren sehr ähnlich:

```text
Kosinus der beiden mittleren 48-Band-Lagen: 0,999573
mittlere absolute Banddifferenz:             0,00003146
maximale Banddifferenz:                      0,00026702 bei 50 Hz
```

Die stärksten mittleren Träger lagen in beiden Passphasen erneut überwiegend
bei 50 bis etwa 330 Hz. Pass 1 und Pass 2 müssen nicht exakt gleich sein, weil
es sich um eine fortlaufende reale Umgebung und nicht um eine gespeicherte
Wiederholung handelt.

## 5. Nachhallantwort

Mittlere gesamte Nachhallwirkung in den Passphasen:

| `tau` | Pass 1 | Pass 2 |
|---:|---:|---:|
| 0,05 s | 0,066269 | 0,066289 |
| 0,20 s | 0,065774 | 0,065798 |
| 1,00 s | 0,063147 | 0,063062 |

Während der stabilen Mute-Rezeptorlage relaxiert ausschließlich der getrennt
ausgewiesene B1-Feldnachhall.

Am Ende der Mute-Phase verblieben:

| `tau` | gesamte Restspur |
|---:|---:|
| 0,05 s | `4,20e-175` |
| 0,20 s | `3,23e-45` |
| 1,00 s | `1,42e-10` |

Die Relaxation wird vollständig durch B1 erklärt. Es trat keine zusätzliche
Offline-, Reflexions- oder Beziehungsspur auf.

## 6. Tatsächlich gezeigt

- Derselbe reale Hardwarestream kann ohne Neustart automatisch geöffnet,
  für die MCM gemutet und erneut geöffnet werden.
- Der Stream wird auch während Mute vollständig drainiert.
- Die Rezeptorlage folgt der technischen Kontaktunterbrechung nach exakt ihrer
  100-ms-Fensterreichweite.
- Der lokale Feldnachhall relaxiert während der Unterbrechung B1-gemäß.
- Nach Öffnung kehrt eine nahezu gleiche verteilte reale Umgebungslandschaft
  zurück.
- Die MCM benötigt dafür keine Geräuschklasse und keine gespeicherte Episode.

## 7. Nicht gezeigt

- dass die Außenwelt während Mute tatsächlich still war,
- dass das Gate biologischer Schlaf oder Offline-Erholung ist,
- eine natürliche Auswahl der Nachhallzeit,
- Beziehungsgeschichte oder entwickelte Topologie,
- Wiedererkennung, Semantik, Reflexion oder Handlung,
- organische Entwicklung oder Feldintelligenz.

## 8. Kritischer Einwand

Der gesamte Befund folgt aus:

```text
binäres technisches Eingangsgate
-> 100-ms-Rezeptorfenster
-> unabhängiger B1-Nachhall
```

Diese Erklärung genügt vollständig. Der Lauf gibt keine zusätzliche
Feldmechanik frei.

## 9. Evidenz und Status

```text
Live-Gate-Invarianten:                E1
kausale sensorische Unterbrechung:    E2
Wiederkehr verteilter Umweltwirkung:  E1 bis E2
zusätzliche MCM-Feldmechanik:         E0
organische Entwicklung:              E0
```

## 10. Bester nächster Schritt

Die auditive Schnellfeldgrenze ist für Gegenwart, Unterbrechung, Nachhall und
Wiederkehr ausreichend kartiert. Weitere binäre Gate-Läufe würden überwiegend
denselben B1-Befund wiederholen.

Als nächstes sollte der visuelle Sensorast dieselben Zustandsgrenzen erhalten.
Erst dann kann geprüft werden, wie zwei gleichzeitig fortlaufende, getrennt
erhaltene Sinnesfelder eine multimodale Gegenwart bilden.
