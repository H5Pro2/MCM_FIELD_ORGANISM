# Befund 019: Reales Pass/Mute/Pass bei laufendem Ton

## 1. Kurzurteil

Das Live-Mikrofon-Gate wurde bei laufendem externem Ton wiederholt:

```text
20 Sekunden Tonkontakt
-> 20 Sekunden technisches Mute vor den Rezeptoren
-> 20 Sekunden fortlaufender Tonkontakt
```

Die beiden Passphasen trugen eine deutlich stärkere und breitere auditive
Landschaft als der vorherige Ventilator-/Raumkontakt. Mute unterbrach die
Rezeptorwirkung erneut exakt und der fortlaufende Kontakt erschien danach
wieder.

## 2. Laufdaten

```text
Gerät:                 Mikrofon (USB PnP Device(Echo-058))
Treiberpfad:           Windows WASAPI, Geräteindex 9
Abtastrate:            48.000 Hz
Rezeptorbänder:        48 logarithmische Bänder
Phasen:                20 s Pass / 20 s Mute / 20 s Pass
Audio-Chunks:          6.000
vollständige Lagen:    5.991
Audioüberläufe:        0
```

Es wurden keine Rohsamples und keine Audiodatei gespeichert.

## 3. Rezeptorantwort

| Passphase | Lagen | mittlere aktuelle Rezeptorenergie |
|---|---:|---:|
| Pass 1 | 1.991 | 0,306580 |
| Pass 2 | 2.000 | 0,269386 |

Die Mute-Phase wird getrennt ausgewiesen:

| Schicht | Umfang | aktuelle Rezeptorwirkung |
|---|---:|---:|
| Gate-Ausgabe | 2.000 Chunks | exakt null |
| Übergang des 100-ms-Rezeptorfensters | 9 Lagen | Mittelwert 0,217694 |
| stabile Rezeptorlage | 1.991 Lagen | exakt null |

Die neun Übergangslagen sind Fensterreste des vorherigen Tonkontakts. Während
der stabilen Mute-Lage existiert keine aktuelle Rezeptorwirkung.

Gegenüber Befund 017 mit laufenden Ventilatoren und ohne zusätzlich
bezeichneten Ton war die mittlere Gesamtwirkung etwa vier- bis fünfmal höher.
Dies ist ein Laufvergleich, keine kalibrierte Lautstärkemessung.

## 4. Verteilte Frequenzlage

Die stärksten mittleren Träger lagen in beiden Passphasen vor allem zwischen
etwa 175 und 476 Hz. Besonders getragen waren Bereiche um:

```text
198 Hz
225 Hz
327 Hz
371 Hz
420 Hz
```

Die mittleren 48-Band-Lagen beider Passphasen hatten einen Kosinus von
`0,990111`. Die Struktur war damit ähnlich, aber nicht identisch.

```text
mittlere absolute Banddifferenz: 0,001071
maximale Banddifferenz:          0,004746 bei etwa 198 Hz
```

Da das reale Audioprogramm während Mute weiterlief, entsprechen Pass 1 und
Pass 2 nicht demselben gespeicherten Ausschnitt. Die Differenz darf deshalb
nicht als Memorywirkung interpretiert werden.

## 5. Nachhallantwort

Mittlere gesamte Nachhallwirkung in den Passphasen:

| `tau` | Pass 1 | Pass 2 |
|---:|---:|---:|
| 0,05 s | 0,305500 | 0,268508 |
| 0,20 s | 0,303157 | 0,265754 |
| 1,00 s | 0,290608 | 0,253426 |

Während der stabilen Mute-Rezeptorlage relaxiert ausschließlich der getrennt
ausgewiesene B1-Feldnachhall.

Am Ende von Mute verblieb:

| `tau` | gesamte Restspur |
|---:|---:|
| 0,05 s | `2,35e-174` |
| 0,20 s | `1,72e-44` |
| 1,00 s | `7,00e-10` |

Auch der stärkere reale Tonkontakt wird vollständig durch die vorhandene
Rezeptor- und B1-Mechanik getragen.

## 6. Tatsächlich gezeigt

- Die auditive Kette trägt eine stärkere reale Außenwirkung verteilt über
  mehrere Frequenzträger.
- Das Live-Gate unterbricht auch diesen Kontakt exakt.
- Nach Öffnung erscheint erneut eine ähnlich strukturierte reale Feldlage.
- Die Feldlage bleibt verteilt und wird nicht auf Gesamtlautstärke reduziert.
- Keine Ton-, Sprach-, Musik- oder Bedeutungsrolle ist erforderlich.

## 7. Nicht gezeigt

- welcher konkrete Ton oder Inhalt lief,
- Wiedererkennung desselben Audiomusters,
- dass Pass 1 und Pass 2 denselben Ausschnitt enthielten,
- natürliche Nachhallwahl oder Beziehungsgeschichte,
- Semantik, Reflexion, Handlung oder Feldintelligenz.

## 8. Evidenz und Status

```text
stärkerer realer auditiver Weltkontakt: E1
kausale Gate-Unterbrechung:             E2
Wiederkehr ähnlicher verteilter Lage:   E1 bis E2
zusätzliche MCM-Feldmechanik:           E0
```

## 9. Bester nächster Schritt

Die binäre auditive Kontaktunterbrechung ist sowohl für schwache
Umgebungswirkung als auch für stärkeren Tonkontakt getragen. Weitere
Pass/Mute/Pass-Läufe würden voraussichtlich nur dieselbe Rezeptor- und
B1-Grenze erneut bestätigen.

Der nächste neue Erkenntnisraum liegt im realen visuellen Sensorast und später
in der zeitgleichen, aber getrennt erhaltenen auditiv-visuellen Gegenwart.
