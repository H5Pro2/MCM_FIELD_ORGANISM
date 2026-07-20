# Lauf 106

## Öffentliche visuelle Außenwelt: Wahrnehmungsbefund

## Frage

Kann eine längere reale öffentliche Bildfolge ausschließlich über Pixel,
visuelle Rezeptoren und das bestehende gemeinsame MCM-Feld verarbeitet
werden, ohne Audio, Titel, Labels, Metadaten oder Rohbildspeicherung?

Dieser Lauf ist ein Wahrnehmungslauf. Er ersetzt nicht den getrennten Zweig
der physischen Effektor-Welt-Rückkopplung.

## Außenweltquelle

Verwendet wurde die reale 35-sekündige Bildspur
[Street traffic](https://commons.wikimedia.org/wiki/File:Street_traffic.webm)
von Wikimedia Commons.

Observerseitige Quellenangaben:

- Urheberangabe: `Editor`;
- Lizenz: [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/);
- Originalauflösung: `1920 × 1080`;
- dekodierte Bildzahl: `1.050`.

Diese Angaben dienten nur Auswahl, Lizenzprüfung und Dokumentation. Sie
gelangten nicht in Rezeptor oder MCM-Feld.

## Verarbeitungsweg

```text
öffentliche reale Bildspur
-> OpenCV-Pixeldekodierung ohne Audio
-> feste Zeitabtastung aus beobachteten Frame-Zeitstempeln
-> bestehende lokale visuelle Rezeptorfläche 8 × 6 × 3
-> visueller Dock
-> bestehende MCM-Neuronenschicht
-> gemeinsames MCM-Feld
```

Die Containerangabe von `1000 fps` war technisch falsch. Deshalb wurde sie
nicht verwendet. Die tatsächlichen Frame-Zeitstempel stiegen in ungefähr
`33 ms` großen Schritten.

Die feste Rezeptorabtastung betrug:

```text
125 ms = 8 Hz
```

Damit entstanden aus 35 Sekunden:

```text
280 zeitgeordnete visuelle Rezeptorzustände
```

Jeder ausgewählte Frame wurde unmittelbar auf lokale Kanalwerte reduziert.
Rohframes wurden weder im Ergebnis noch im Repository behalten.

## Kontrollen

### R0 - exakte Wiederholung

Die vollständige Datei wurde unabhängig zweimal dekodiert und reduziert.

Beide reduzierten Sequenzen hatten denselben Digest:

```text
f147109d3ac2c411328b0a514119df8fd18abd0bded487056d4a6502bc70780f
```

### B0 - statische Bildbaseline

Dieselbe Zahl von Rezeptorintervallen und dieselbe Feldzeit wurden verwendet.
Anstelle der wechselnden Bildfolge wurde in allen 280 Intervallen nur der
erste reduzierte Rezeptorzustand wiederholt.

Diese Baseline prüft:

```text
zeitlicher Ablauf allein
gegen
zeitlicher Ablauf mit wechselnder visueller Außenwelt
```

### Ausschlüsse

- kein Audio;
- kein Titel oder Dateiname im Rezeptor;
- keine Beschreibung oder Objektinformation;
- kein Transkript;
- keine Video- oder Seitenmetadaten im Rezeptor;
- kein künstliches Rauschen;
- keine Objekt- oder Wortlabels;
- keine adaptive Abtastung;
- keine Auswahl anhand späterer Feldantworten;
- keine Rohbildablage;
- keine neue Memory- oder Topologiemechanik.

## Ergebnis

### Visuelle Rezeptorlage

Größte Spannweite eines lokalen Rezeptorkanals über die Bildfolge:

```text
0,6645475672
```

Die reale Bildfolge erzeugte damit deutlich wechselnde lokale
Rezeptorkontakte.

### Gemeinsames MCM-Feld

Feldlage nach der vollständigen realen Bildfolge:

```text
activation:  0,2100632279 bis 0,6460159929
afterimage:  0,2140940278 bis 0,6345833965
```

Maximale Differenz zur statischen Bildbaseline:

```text
activation:  0,1429486114
afterimage:  0,1439472231
```

Damit gilt:

```text
wechselnde reale Bildfolge
-> wechselnde lokale Rezeptorkontakte
-> andere aktuelle MCM-Feldlage als bei statischem Bildkontakt
```

## Befund

Die öffentliche Außenweltquelle erreicht reproduzierbar den bestehenden
visuellen Rezeptorpfad und das gemeinsame MCM-Feld. Das Feld bildet nicht nur
die Dauer des Kontakts ab; seine aktuelle Lage unterscheidet sich kausal von
einem gleich langen statischen Bildkontakt.

Der Befund ist vollständig durch vorhandene Mechanik erklärbar:

```text
wechselnde Pixel
-> wechselnde lokale Rezeptorwerte
-> feste lokale Feldaufnahme
-> feste Diffusion
-> schneller Nachhall
```

## Nicht gezeigt

Lauf 106 zeigt nicht:

- weltbezogenes Memory;
- Verdichtung einer Erfahrung;
- entwickelte MCM-Feldtopologie;
- Wiedererkennen;
- semantische Resonanz;
- innere Bezeichnung;
- Reflexion oder inneren Dialog;
- Handlung;
- Feld-Welt-Feld-Rückkopplung;
- Feldintelligenz.

Insbesondere ist die Abweichung zur statischen Baseline kein Memory-Hinweis.
Sie entsteht während fortlaufend unterschiedlicher aktueller Weltkontakte.

## Richtungsentscheidung

Öffentliche reale Videowelten sind als reproduzierbare Außenwelt für die
weitere Wahrnehmungsentwicklung geeignet. Sie erlauben längere, kontrollierte
Form-, Bewegungs-, Oberflächen- und Raumverläufe ohne physische
Kamerainszenierung.

Sie ersetzen nicht:

- eine veränderbare Außenwelt;
- einen Effektor;
- reale Konsequenzen eigener Wirkung;
- die spätere Prüfung von Lösung, Wiederbindung oder Memory.

Der getrennte Effektor-Zielflächen-Zweig bleibt deshalb offen.

## Wie es am besten weitergeht

Als nächster Wahrnehmungsschritt wird dieselbe reale Bildfolge in klar
getrennte, zusammenhängende Zeitabschnitte zerlegt. Beobachtet wird nur, wie
sich lokale Feldlagen während fortlaufender Weltveränderung bilden,
überlappen und im schnellen Nachhall ablösen.

Dabei wird noch keine Verdichtung programmiert. Erst die Verlaufskarte muss
zeigen, welche lokale Feldinformation über die aktuelle Projektion hinaus
für eine spätere weltbezogene Organisation überhaupt fehlt.
