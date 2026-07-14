# Befund 008: Erster realer Breitband-Audiokontakt

## 1. Bezug

Dieser Lauf folgt der Architekturfreigabe aus
[Befund 007](007_BREITE_LOGARITHMISCHE_AUDIOREZEPTORFLAECHE_BEFUND.md).

Ein realer Fünf-Sekunden-Audioabschnitt wurde bei unverändertem Aufnahmepegel
parallel durch 24, 48 und 64 logarithmische Bänder geführt. Es wurden keine
Schwellen, Spikes oder Feldkopplungen verwendet.

## 2. Ausführung

```text
Gerät:               Mikrofon (USB PnP Device(Echo-058))
Host-API:            Windows WASAPI
Abtastrate:          48000 Hz
Eingabe-Chunks:      500 x 10 ms
Analysefenster:      100 ms
Ausgaben je Geometrie: 491
Bandzahlen:          24 / 48 / 64
Überläufe:           0
Rohdatenspeicherung: keine
```

Der Stream wurde nach fünf Sekunden geschlossen.

## 3. Rechenzeit

Alle drei Geometrien wurden pro Eingabe-Chunk nacheinander berechnet:

```text
gesamte Rezeptorrechenzeit:       2.3368 Sekunden
mittlere Zeit pro 10-ms-Chunk:    4.6736 ms
```

Der gemeinsame passive Vergleich blieb in diesem Lauf innerhalb der
10-ms-Eingabezeit. Das ist ein technischer Machbarkeitsbefund auf diesem PC,
keine allgemeine Echtzeitgarantie.

## 4. Normalisierter Geometrievergleich

Da überlappende Bandzahlen Spektralanteile unterschiedlich verteilen und
duplizieren, dürfen ihre absoluten Gesamtenergien nicht direkt verglichen
werden. Für den Geometrievergleich wurden ausschließlich normierte mittlere
Spektrallandschaften auf eine gemeinsame logarithmische Achse interpoliert.

Korrelationen:

```text
24 gegen 48 Bänder: 0.9745
24 gegen 64 Bänder: 0.9332
48 gegen 64 Bänder: 0.9514
```

Damit tragen alle drei Geometrien eine ähnliche grobe mittlere
Spektrallandschaft. Sie sind nicht identisch.

## 5. Spektraler Schwerpunkt

Geometrischer Schwerpunkt der jeweiligen verteilten Bandlage:

```text
Bänder    q05       Median     q95
24        185.9 Hz  328.9 Hz   592.3 Hz
48        195.3 Hz  338.0 Hz   616.3 Hz
64        197.8 Hz  338.8 Hz   617.2 Hz
```

Der Schwerpunkt ist über die drei Auflösungen vergleichsweise stabil. Er ist
eine passive Observermessung und keine Zentrumseigenschaft des Feldes.

## 6. Instabilität des stärksten Einzelbandes

Die Medianlage des jeweils stärksten Bandes war deutlich weniger stabil:

```text
24 Bänder: 232.2 Hz
48 Bänder: 154.3 Hz
64 Bänder:  60.3 Hz
```

In allen drei mittleren Spektren gehörte der untere Rand bei `50 Hz` zu den
stärksten Bändern. Bei 64 Bändern war zusätzlich `60.3 Hz` stark vertreten.

Der reale Lauf kann nicht trennen, ob dies stammt aus:

- dem abgespielten Audio,
- Raum- oder Körperschall,
- elektrischem oder gerätebezogenem Brummen,
- Mikrofoncharakteristik,
- Fenster- und Randleckage,
- der unterschiedlichen Breite der unteren Bänder.

Deshalb ist die dominante Einzelbandlage noch kein stabiler Trägerbefund.

## 7. Verteilungsbreite

Die mittlere normierte Beteiligung der Bänder betrug:

```text
24 Bänder: 0.4900
48 Bänder: 0.4468
64 Bänder: 0.3983
```

Der Wert sinkt mit feinerer Unterteilung. Das kann allein aus der Geometrie und
der konzentrierteren Verteilung über mehr Kanäle folgen. Es wird daraus keine
zunehmende Spezialisierung oder Organisation abgeleitet.

## 8. Enger Befund

Gezeigt ist:

```text
realer Mikrofonkontakt
-> breite verteilte Frequenzlage von 50 Hz bis 18 kHz
-> ähnliche grobe Landschaft über 24 / 48 / 64 Bänder
```

Nicht stabil gezeigt ist:

```text
bestimmtes dominantes Einzelband
oder
eine richtige endgültige Bandgeometrie
```

Die breite Fläche trägt damit mehr reale Frequenzinformation als die frühere
Drei-Sonden-Referenz. Sie erzeugt noch kein auditives MCM-Feld.

## 9. Evidenz

**E1 für einen endlichen realen Breitband-Audiokontakt.**

**E1 für grobe geometrieübergreifende Spektrallandschaft unter diesem einen
Lauf.**

Weiterhin **E0** für:

- robuste dominante Träger,
- natürliche Wahl von 24, 48 oder 64 Bändern,
- MCM-Neuronen und auditive Feldkopplung,
- Musterbildung, Hören und Feldintelligenz.

## 10. Architekturentscheidung

Die breite Rezeptorfläche bleibt passiv freigegeben. Keine Bandzahl wird als
endgültige Geometrie ausgewählt. Die untere Randdominanz blockiert vorerst jede
Weitergabe an eine Feldkopplung.

## 11. Bester nächster Schritt

Bei unverändertem Aufnahmepegel und vollständig gestopptem externem Audio wird
derselbe parallele 24/48/64-Lauf als Breitband-Stillebaseline wiederholt.

Entscheidend ist:

```text
Bleibt 50–60 Hz in Stille dominant?
```

Falls ja, muss die Wirkung zuerst als lokale Umwelt-, Geräte- oder
Rezeptorgrundlage verstanden werden. Falls sie mit dem Audio verschwindet, ist
sie Teil dieses äußeren Kontakts. In beiden Fällen bleibt eine harte
Unterdrückung oder automatische Normalisierung gesperrt.
