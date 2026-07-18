# Beobachtungsgrenze statt Feldtakt

## Status

Verbindliche Architekturentscheidung auf `E0 / CONTRACT_ONLY`.

Die gegenwärtige Architektur besitzt keinen begründeten natürlichen Feldtakt.
Sie darf deshalb weder eine Sensorfrequenz noch eine frei gewählte feste
Periode als organischen Rhythmus ausgeben.

## Warum kein Feldtakt ableitbar ist

Auditive und visuelle Rezeptoren schließen innerhalb derselben realen Dauer
unterschiedlich viele Zustände ab. Ein Feldschritt je Rezeptorabschluss würde
die schnellere technische Ausgaberate zur stärkeren Feldprägung machen.

Das gemeinsame Feld besitzt außerdem noch keine freigegebene kontinuierliche
Dynamik, aus der ein eigener Zustandsabschluss hervorgehen könnte. Ein solcher
Endpunkt darf daher nicht vor der Mechanik behauptet oder programmiert werden.

## Technische Beobachtungsgrenze

`MCMFieldStepTime` bezeichnet vorerst ausschließlich ein extern gemessenes
Intervall, über das ein Feldvorschlag technisch ausgewertet werden kann.

```text
gemessener Feldzustand bei t0
+ real verstrichene Organismusdauer t0 -> t1
+ alle bis t1 kausal abgeschlossenen lokalen Rezeptorzustände
-> beobachtbarer Feldvorschlag bei t1
```

Die Grenze `t1`:

- wird nicht von einem Rezeptorereignis ausgelöst,
- bezeichnet keinen biologischen Takt,
- trägt keine Bedeutung oder Priorität,
- speichert keinen letzten Kontakt,
- verändert nicht die native Reihenfolge der Rezeptorabschlüsse.

Ein technischer Aufrufer darf eine Auswertung anfordern. Diese Anforderung ist
jedoch Beobachtung und Berechnungsorganisation, keine Ursache der organischen
Feldentwicklung.

## Zeitteilungsinvarianz

Eine spätere Feldmechanik muss denselben kausalen Verlauf unabhängig davon
tragen, ob ein Beobachtungsintervall technisch gröber oder feiner unterteilt
wird.

```text
Entwicklung(t0 -> t2)
== Entwicklung(t1 -> t2, Entwicklung(t0 -> t1))
```

Dabei müssen dieselbe verstrichene Dauer und dieselben lokalen
Rezeptorabschlüsse erhalten bleiben. Zusätzliche leere Beobachtungsgrenzen
dürfen weder Aktivierung erzeugen noch Kontakt halten oder Entwicklung
beschleunigen.

Diese Forderung legt noch keine konkrete Differentialgleichung,
Relaxationsform oder Updatefunktion fest. Sie beschreibt nur eine notwendige
Eigenschaft jeder späteren lokalen Feldentwicklung.

## Abwesenheit und fortlaufende Zeit

Ein Intervall ohne neuen Rezeptorabschluss ist kein Nullkontakt. Es beschreibt
nur verstrichene Organismusdauer ohne neuen lokalen Weltzustand.

Diese Abwesenheit ist technisch ausführbar: `ReceptorDistribution` darf an
einer Beobachtungsgrenze eine leere Kontaktmenge tragen. Die Docks bleiben im
Feld bestehen und ihre Neuronen erhalten keinen skalaren Rezeptorkontakt.

Ob ein Feld in dieser Dauer stabil bleibt, relaxiert oder sich durch bereits
vorhandene innere Feldwirkung verändert, muss aus einer später geprüften
Feldmechanik folgen. Der Scheduler darf dieses Verhalten nicht vorgeben.

## Nicht freigegeben

- Feldschritt je Audio-, Video- oder Sensorereignis,
- feste Periode als behaupteter Organismusrhythmus,
- schnellste oder langsamste Modalität als Taktgeber,
- Warten auf einen vollständigen multimodalen Satz,
- Sample-and-Hold zwischen Beobachtungsgrenzen,
- Interpolation oder Mittelung fehlender Zustände,
- adaptive Taktwahl anhand von Aktivierung, Bedeutung oder Neuigkeit.

## Konsequenz

Die vorhandenen Transportverträge reichen aus, um beliebige gemessene
Beobachtungsintervalle verlustfrei vorzubereiten. Ein Live-Scheduler ist noch
nicht freigegeben und derzeit auch nicht erforderlich.

Die kleinste zulässige Informationsgrenze ist im Vertrag
[Minimale lokale Feldentwicklungsrolle](037_MINIMALE_LOKALE_FELDENTWICKLUNGSROLLE.md)
festgelegt. Vor einer Runtimefreigabe muss jeder spätere
Übergangskandidat insbesondere die Zeitteilungsinvarianz bestehen.
