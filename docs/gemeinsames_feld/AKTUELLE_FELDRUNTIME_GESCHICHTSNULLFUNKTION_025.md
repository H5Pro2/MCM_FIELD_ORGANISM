# Aktuelle Feldruntime-Geschichtsnullfunktion 025

## Status

Diese Untersuchung ist ein passiver Lauf der aktuellen gemeinsamen
Ein-Feld-Runtime. Sie verwendet ausschließlich:

- den neutralen Rezeptorenverteiler,
- zwei offene Docks im selben Feld,
- die gemeinsame MCM-Neuronenschicht,
- die vorhandene zustandslose Rezeptorprojektionsbaseline,
- vorhandene lokale Vorfeldproben.

Es wurde kein Geschichtsträger, Reset, Zustandskopieren oder Writeback ergänzt.

## Frage

Erzeugen zwei verschiedene Kontaktgeschichten nach vollständiger natürlicher
Angleichung des vorhandenen Feldzustands unter derselben späteren Probe noch
eine verschiedene Feldantwort?

## Kontrollaufbau

Zwei unabhängig aufgebaute gemeinsame Felder erhalten auf dem auditiven Dock:

```text
A: 0,2 -> 0,8 -> 0,5
B: 0,5 -> 0,8 -> 0,2
```

Beide Geschichten enthalten dieselben drei Kontaktwerte, aber in anderer
Reihenfolge und mit verschiedenem Endkontakt. Das visuelle Kontrolldock erhält
in beiden Zweigen durchgehend `0,3`.

Die Felder werden anschließend nicht zurückgesetzt. Sie erhalten nacheinander:

```text
Neutralisierung 1: auditiv 0,0 / visuell 0,0
Neutralisierung 2: auditiv 0,0 / visuell 0,0
identische Probe:  auditiv 0,6 / visuell 0,4
```

Alle Schritte laufen regulär durch Verteiler, Docks und gemeinsame
Neuronenschicht.

## Warum zwei Neutralisierungsschritte nötig sind

Nach dem ersten neutralen Takt gilt in beiden Zweigen exakt:

```text
activation = (0,0; 0,0)
afterimage = (0,0; 0,0)
```

Die vollständigen Layerdigests sind dennoch verschieden.

Grund: Jede aktuelle Neuronenwahrnehmung enthält lokale Feldproben aus dem
vorherigen abgeschlossenen Takt. Nach nur einem neutralen Takt tragen diese
Proben noch die verschiedenen terminalen Feldlagen.

Nach dem zweiten neutralen Takt stammen auch die lokalen Proben aus der bereits
angeglichenen Nullfeldlage. Erst dann kollidieren die vollständigen
Layerdigests exakt.

Damit wurde Zustand nicht nur über `activation` und `afterimage`, sondern
einschließlich lokaler Wahrnehmung angeglichen.

## Ergebnis

```text
Geschichten verschieden:                         ja
Kontaktmultimengen gleich:                       ja
terminale vollständige Layerzustände verschieden: ja

nach Neutralisierung 1:
  schnelle Vektoren gleich:                      ja
  vollständige Layerzustände gleich:             nein

nach Neutralisierung 2:
  vollständige Layerzustände gleich:             ja

nach identischer Probe:
  vollständige Layerzustände gleich:             ja
  funktionaler Unterschied:                      nein
```

Die Probe erzeugt in beiden Zweigen:

```text
activation = (0,6; 0,4)
afterimage = (0,0; 0,0)
```

Auch die vollständigen Layerdigests sind identisch.

## Tragfähiger Befund

Die aktuelle Rezeptorprojektionsbaseline trägt keine funktionale
Geschichtswirkung über die vorhandene endliche lokale Gegenwart hinaus.

Korrekte Aussage:

> Sobald Aktivierung, Nachhall und die nachlaufende lokale Vorfeldwahrnehmung
> vollständig durch reguläre Weltkontakte angeglichen sind, sind die geprüften
> Geschichten unter derselben späteren Probe funktional äquivalent.

Die lokale Vorfeldprobe ist realer Bestandteil des Neuronenzustands und darf
nicht übersehen werden. Sie trägt hier jedoch nur den unmittelbar vorherigen
abgeschlossenen Feldtakt und wird durch die nächste angeglichene Feldlage
vollständig ersetzt.

## Nicht gezeigt

Der Befund zeigt nicht:

- dass jede mögliche Geschichte nach zwei Takten gleich wird,
- dass keine andere zulässige lokale Feldfunktion Geschichte tragen könnte,
- dass ein neuer langsamer Zustand nötig ist,
- dass Memory programmiert werden darf,
- dass die Rezeptorprojektionsbaseline eine geeignete organische Feldmechanik
  ist.

Das Ergebnis ist innerhalb der vorhandenen zustandslosen Leserform zu erwarten:

```text
aktuelle Rezeptorkontakte
-> aktuelle Aktivierung
```

Die lokale Vorfeldwahrnehmung wird der Transition zwar kausal angeboten, von
dieser Baseline aber nicht zur Feldwirkung verwendet.

## Evidenzgrenze

```text
vollständige Zustandsangleichung:              E1
Nullfunktion der aktuellen Rezeptorprojektion: E1
geschichtsvermittelte Feldwirkung:             E0
organisches Memory:                            E0
```

Feldintelligenz wird in dieser Reihe nicht als Ziel oder eigene Evidenzachse
geprüft. Sie wäre höchstens eine mögliche spätere Interpretation offener
Feldentwicklung.

## Stopplinie

Der Nullbefund gibt keine Mechanik frei. Nicht freigegeben sind:

- Geschichtsträger oder langsame Spur,
- Nachhall- oder Integrationsgleichung,
- feste Rekurrenz,
- Beziehung, Ressource oder Topologie,
- Reflexion, Offline-Wirkung oder Lernen.

## Nächster Prüfpunkt

Die konkrete Funktionslücke liegt jetzt vor:

```text
Lokale Vorfeldproben sind kausal verfügbar,
haben in der aktuellen Transition aber keine Wirkung.
```

Vor einem neuen Runtime-Kandidaten muss deshalb ein minimaler
Zulässigkeitsvertrag für lokale Feldwirkung festlegen:

- nur aktuelle eigene Rezeptoraufnahme und lokale Vorfeldproben,
- atomare Wirkung erst im nächsten vollständigen Zustand,
- räumliche Spiegel- und Reihenfolgeinvarianz,
- keine Semantik, Richtung oder Zielantwort,
- keine zusätzliche Geschichte oder Memoryvariable,
- zwingende Trennung gegen reine Rezeptorprojektion und feste Rekurrenz.

Erst danach darf `GF_001` als isolierter synthetischer Feldwirkungsversuch
vorregistriert werden.

Der [Zulässigkeitsvertrag minimale lokale Feldwirkung 026](ZULAESSIGKEITSVERTRAG_MINIMALE_LOKALE_FELDWIRKUNG_026.md)
setzt diese Grenze. Der erste Kandidat darf nur aktuellen Rezeptorkontakt,
lokale Vorfeldproben und deren relative Geometrie lesen. Eigenzustand,
Nachhallupdate, Geschichte, Beziehung und Topologie bleiben ausgeschlossen.
