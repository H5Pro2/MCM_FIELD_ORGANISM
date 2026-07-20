# Kausalvertrag der getrennten visuellen Weltwirkung

## Stand

Die digitale Effektorfläche und ihre begrenzte Bildschirmdarstellung sind
technisch geprüft. Eine direkte Aufnahme dieser Darstellung durch die Kamera
ist ausgeschlossen:

```text
MCM-Feld -> Bildschirm -> Kamera -> MCM-Feld
```

Dieser Pfad wäre Selbstbeobachtung der eigenen technischen Ausgabe. Er zeigt
keine Wirkung auf eine unabhängige Außenwelt.

## Zulässiger Kausalpfad

Der nächste reale Pfad lautet:

```text
abgeschlossener MCM-Feldsnapshot
-> feste visuelle Effektorabbildung
-> zwei räumlich getrennte Lichtkanäle
-> zwei passive äußere Zielflächen
-> Kamera sieht ausschließlich die Zielflächen
-> regulärer visueller Rezeptor
-> gemeinsames MCM-Feld
```

Die Zielflächen sind Teil der Außenwelt. Sie besitzen keine Berechnung, keine
Semantik und keinen eigenen Speicher.

## Minimale physische Anordnung

1. Der Bildschirm oder eine spätere Lichtquelle steht außerhalb des
   Kamerabildes.
2. Die linke und rechte Effektorhälfte werden durch zwei getrennte,
   lichtundurchlässig gegeneinander abgeschirmte Kanäle geführt.
3. Jeder Kanal beleuchtet genau eine matte, passive Zielfläche.
4. Zwischen den Zielflächen liegt ein sichtbarer räumlicher Abstand.
5. Die Kamera sieht beide Zielflächen vollständig, aber weder Effektor,
   Lichtkanalöffnung noch direkte Spiegelung des Effektors.
6. Kameraposition, Fokus, Belichtung und Weißabgleich bleiben während einer
   Prüfung fest.
7. Umgebungslicht darf vorhanden sein, wird aber während eines Vergleichs
   nicht absichtlich verändert.

```text
verdeckter Effektor
   |              |
Lichtkanal L   Lichtkanal R
   |              |
Zielfläche L   Zielfläche R
        \        /
          Kamera
```

## Technische Kanalabbildung

Die bereits geprüfte affine Abbildung bleibt unverändert:

```text
I_links  = 0,50 + 0,25 * activation
I_rechts = 0,50 - 0,25 * activation
```

Für die physische Anordnung werden die bisher benachbarten Werte lediglich in
zwei getrennte Raster umgeordnet:

```text
linkes Zielraster  = alle linken Werte in unveränderter Feldgeometrie
rechtes Zielraster = alle rechten Werte in unveränderter Feldgeometrie
```

Diese feste Umordnung:

- wählt keine Wirkung aus;
- führt keine Schwelle ein;
- verändert keine Intensität;
- speichert keinen Zustand;
- liest weder Bedeutung noch Provenienz;
- schreibt nicht in Kamera, Rezeptor oder Feld zurück.

Der neutrale Feldzustand erzeugt auf beiden Kanälen dieselbe technische
Mittelgrauwirkung.

## Observerseitige Aufbauprüfung

Vor einem realen Feld-Welt-Feld-Lauf muss ein Mensch im Kamerabild bestätigen:

- beide Zielflächen sind vollständig sichtbar;
- beide Zielflächen sind räumlich getrennt;
- Bildschirm und Lichtquelle sind nicht sichtbar;
- keine direkte Effektorreflexion ist sichtbar;
- die Kanalzuordnung links/rechts ist eindeutig;
- automatische Belichtung, automatischer Weißabgleich und Autofokus wurden
  nach der Startphase gesperrt.

Diese Bestätigung ist ausschließlich eine Freigabe des Aufbaus. Sie wird nicht
als Feldinformation übertragen.

## Kontrollen des ersten realen Laufs

Der erste reale Lauf benötigt mindestens:

```text
E0: neutraler Feldsnapshot
E1: nicht neutraler Feldsnapshot
B0: optischer Weg zu beiden Zielen blockiert
R0: Wiederholung von E0 und E1 bei unverändertem Aufbau
```

Die Kamera darf nur Pixel der äußeren Szene liefern. Effektorwerte, Digests,
Zeitrollen, Kanalnamen und Observerangaben dürfen nicht in den Rezeptorrahmen
gelangen.

## Abbruchbedingungen

Der reale Lauf wird nicht ausgewertet, wenn:

- der Effektor oder seine Spiegelung im Kamerabild erscheint;
- sich Kameraautomatik zwischen Vergleichsphasen verändert;
- ein Lichtkanal auf beide Zielflächen wirkt;
- die Zielflächen im Rezeptorraster räumlich nicht unterscheidbar sind;
- interne Effektorwerte den Kamerapfad umgehen;
- eine automatische Anpassung aus dem Kamerabild die Ausgabe verändert.

## Aussagegrenze

Ein erfolgreicher Aufbau kann zunächst nur zeigen:

```text
MCM-Feld
-> physische Weltwirkung
-> regulärer Rezeptorkontakt
-> aktuelle MCM-Feldlage
```

Er zeigt noch kein Memory, keine entwickelte Feldtopologie, keine Semantik,
keine Reflexion und keine Handlungsauswahl. Memory und Feldtopologie bleiben
als spätere Forschungsfragen offen.

## Implementierungsfreigabe

Freigegeben ist:

- die feste Aufteilung eines geprüften Effektorrahmens in zwei getrennte
  Lichtkanalraster;
- eine zeitlich begrenzte, statische Präsentation dieser Raster;
- ein manuelles Werkzeug zum Aufbau der äußeren Zielflächen.

Noch geschlossen bleibt:

- automatische Kamera-Rückführung;
- ein geschlossener Dauerlauf;
- adaptive Ausgabe;
- automatische Aufbaubewertung;
- jede Memory-, Semantik- oder Topologiemechanik.
