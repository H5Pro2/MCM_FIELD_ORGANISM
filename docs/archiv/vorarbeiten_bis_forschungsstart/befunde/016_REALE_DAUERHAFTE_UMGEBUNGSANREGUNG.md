# Befund 016: Reale dauerhafte Umgebungsanregung

## 1. Kurzurteil

Ein 20-sekündiger realer Mikrofonlauf bei laufenden Ventilatoren erzeugte eine
durchgehend aktive auditive Rezeptor- und Feldlage. Keine der 1.991
vollständigen Lagen war exakt null.

Der Lauf trägt E1 für eine stabile reale Umgebungsanregung. Er weist die
gemessene Wirkung nicht kausal allein den Ventilatoren zu.

## 2. Laufdaten

```text
Gerät:             Mikrofon (USB PnP Device(Echo-058))
Treiberpfad:       Windows WASAPI, Geräteindex 9
Abtastrate:        48.000 Hz
Rezeptorbänder:    48 logarithmische Bänder, 50 Hz bis 18 kHz
Dauer:             20 Sekunden
Audio-Chunks:      2.000
Rezeptorlagen:     1.991
Audioüberläufe:    0
active_zero:       0
active_energy:     1.991
```

Es wurden keine Rohsamples und keine Audiodatei gespeichert.

## 3. Gesamte Rezeptorwirkung

```text
Mittelwert: 0,066173
Median:     0,066614
Minimum:    0,039400
Maximum:    0,091962
```

Der Median liegt nahe am Mittelwert. Der 20-sekündige Kontakt war damit in
seiner gesamten Rezeptorbeanspruchung vergleichsweise kontinuierlich, aber
nicht konstant.

## 4. Stärkste mittlere Frequenzlagen

| Bandmitte | mittlere Energie |
|---:|---:|
| 50,0 Hz | 0,005118 |
| 288,7 Hz | 0,004251 |
| 56,7 Hz | 0,003554 |
| 154,3 Hz | 0,003343 |
| 64,2 Hz | 0,003103 |
| 136,2 Hz | 0,002728 |
| 327,2 Hz | 0,002670 |
| 72,8 Hz | 0,002660 |

Die stärksten mittleren Lagen befinden sich überwiegend im unteren
Frequenzbereich. Das ist mit Ventilator-, Raum- oder technischen
Grundwirkungen vereinbar, identifiziert ihre Quelle jedoch nicht.

## 5. Passive Nachhallkandidaten

| `tau` | mittlere gesamte Nachhallwirkung | letzte gesamte Nachhallwirkung |
|---:|---:|---:|
| 0,05 s | 0,065987 | 0,082032 |
| 0,20 s | 0,065468 | 0,071932 |
| 1,00 s | 0,062912 | 0,065246 |

Alle drei Kandidaten folgen weiterhin vollständig B1. Die unterschiedlichen
Endwerte zeigen nur verschiedene zeitliche Glättung des letzten Abschnitts.

## 6. Tatsächlich gezeigt

- Ein realer schwacher Umgebungskontakt stimuliert die auditive Feldkette
  fortlaufend.
- Technische Stille ist bei eingeschaltetem Mikrofon nicht automatisch
  gegeben.
- Die verteilte Frequenzlage bleibt erhalten und wird nicht zu einem einzelnen
  Lautstärkewert reduziert.
- Der sparsame Feldkandidat verarbeitet den Kontakt ohne zusätzliche Kopplung.

## 7. Nicht gezeigt

- dass ausschließlich die Ventilatoren die gemessene Wirkung verursachen,
- welche Anteile aus Raum, Mikrofon oder USB-Elektronik stammen,
- dass die tiefen Bänder eine semantische Geräuschklasse bilden,
- natürliche Nachhallwahl, Lernen oder organische Entwicklung,
- Beziehungsgeschichte, Reflexion oder Feldintelligenz.

## 8. Evidenz und Status

```text
reale dauerhafte Umgebungsanregung: E1
kausale Zuordnung zu Ventilatoren:   E0
zusätzliche MCM-Feldmechanik:        E0
```

## 9. Bester nächster Schritt

Die sensorische Unterbrechung wurde in Befund 017 durch ein automatisches
Live-Gate geprüft. Dadurch blieb die reale Umgebung unverändert, während der
MCM-Kontakt exakt ausgesetzt wurde. Eine kausale Zuordnung speziell zu den
Ventilatoren würde weiterhin einen separaten Lauf mit ausgeschalteten
Ventilatoren erfordern.
