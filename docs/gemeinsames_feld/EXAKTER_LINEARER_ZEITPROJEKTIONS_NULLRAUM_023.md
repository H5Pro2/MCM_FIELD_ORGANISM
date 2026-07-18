# Exakter linearer Zeitprojektions-Nullraum 023

## Status

Diese Untersuchung ist ein passiver, exakt rational gerechneter
Architekturabgleich vor `GF_001`. Sie ergänzt keine Runtime-Mechanik und keine
Feldwirkung.

Der [Passive gerichtete Zeitmoment-Abgleich 022](PASSIVER_GERICHTETER_ZEITMOMENT_ABGLEICH_022.md)
hat gezeigt, dass ein gerichtetes erstes Moment Zeitumkehr unterscheiden kann,
aber nicht jede geordnete Bahn eindeutig abbildet.

## Frage

Kann eine feste endliche Bank linearer Zeitprojektionen eine beliebig reicher
werdende Kontaktgeschichte eindeutig bewahren?

## Kontrollraum

Geprüft wird eine achtteilige, stückweise konstante Kontaktbahn. Die feste Bank
enthält sechs lineare Beobachtungen:

1. erster Kontakt,
2. letzter Kontakt,
3. Zeitmoment null,
4. Zeitmoment eins,
5. Zeitmoment zwei,
6. Zeitmoment drei.

Alle Koeffizienten, Ränge, Nullvektoren und Projektionen werden mit exakten
rationalen Zahlen berechnet.

## Rang-Nullitäts-Prüfung

Für die Projektionsmatrix gilt:

```text
Geschichtsdimension = 8
Projektionsanzahl    = 6
Matrixrang           = 6
exakte Nullität      = 8 - 6 = 2
```

Damit existieren nichttriviale Änderungen der Kontaktbahn, die alle sechs
Beobachtungen unverändert lassen.

Ein exakt berechneter Nullvektor lautet:

```text
(0, 1, -4, 6, -4, 1, 0, 0)
```

Er wird symmetrisch und begrenzt um den Kontakt `0,5` gelegt. Dadurch entstehen
zwei verschiedene gültige Bahnen innerhalb des normierten Kontaktraums:

```text
A = (0,5; 0,541666...; 0,333333...; 0,75;
     0,333333...; 0,541666...; 0,5; 0,5)

B = (0,5; 0,458333...; 0,666666...; 0,25;
     0,666666...; 0,458333...; 0,5; 0,5)
```

Anfang und Ende sind gleich. Alle sechs Projektionen kollidieren exakt:

```text
(1/2, 1/2, 1/2, 1/4, 1/6, 1/8)
```

## Allgemeiner linearer Befund

Für jede feste lineare Abbildung von einem `n`-dimensionalen Verlaufsraum in
`m` Projektionen gilt bei `n > m`:

```text
Nullität >= n - m > 0
```

Eine feste endliche lineare Projektionsbank kann deshalb nicht injektiv auf
allen beliebig länger oder feiner werdenden Kontaktbahnen sein. Werden weitere
Momente ergänzt, kann die Geschichtsdimension erneut größer als deren feste
Anzahl gewählt werden.

## Kritische Begrenzung

Der Befund gilt für feste lineare Projektionen auf einem vollen
Verlaufsraum. Nicht widerlegt sind:

- nichtlineare Darstellungen,
- begrenzte Klassen zulässiger Weltverläufe,
- endliche Genauigkeit mit bewusst akzeptierter Gleichsetzung,
- ein dynamischer Feldzustand, der Geschichte durch Wirkung statt Archivierung
  trägt,
- funktionale Äquivalenz verschiedener Verläufe.

Insbesondere zeigt der Nullraum nicht, dass jedes Detail einer Kontaktbahn
bewahrt werden muss. Er zeigt das Gegenteil der bisherigen impliziten Suche:

> Vollständige, eindeutige Bewahrung beliebig reicher Geschichte kann nicht
> durch eine feste endliche lineare Zusammenfassung erreicht werden.

## Stopplinie

`GF_001` bleibt geschlossen. Nicht freigegeben sind:

- die geprüfte Momentenbank,
- eine größere feste Momentenbank,
- Sequenzspeicherung,
- ein Integrator oder lokaler Zeitwirkzustand,
- Feldkopplung, Memory, Topologie oder Lernen.

## Konsequenz für die Forschungsrichtung

Der Repräsentationszweig ist an dieser Stelle ausreichend abgesichert. Weitere
feste Kennwertbanken würden die gleiche Grenze nur verschieben.

Als nächstes muss vor jeder Mechanik ein funktionaler Vertrag geklärt werden:

```text
Welche Geschichtsunterschiede müssen überhaupt erhalten bleiben,
weil sie eine spätere lokale Feldwirkung kausal verändern?
```

Erst eine solche funktionale Äquivalenzgrenze kann verhindern, dass das
gemeinsame MCM-Feld zu einem statischen Archiv von Weltverläufen wird.

Der [Funktionale Geschichtsäquivalenzvertrag 024](FUNKTIONALER_GESCHICHTSAEQUIVALENZVERTRAG_024.md)
setzt diese Grenze. Verschiedene Verläufe müssen nur dann getrennt bleiben,
wenn bei kontrollierter Gegenwart eine spätere lokale Feldwirkung kausal mit
der Geschichte mitwandert. Der Vertrag führt selbst keinen Träger ein.
