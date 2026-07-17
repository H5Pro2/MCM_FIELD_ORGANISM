# Rezeptorvertrag und Dockgrenze

## Verbindlicher Pfad

```text
Sensorquelle
-> sensorspezifische Rezeptorfläche
-> abgeschlossener ReceptorContactFrame
-> neutraler ReceptorDistributor
-> stabiler ReceptorDock
-> ReceptorNeuronDockMap
-> eine gemeinsame MCMNeuronLayer
```

Die Rezeptorfläche darf technische Energie lokalisieren, normalisieren und in
eine endliche Trägergeometrie überführen. Der abgeschlossene Kontakt enthält
keine Rohbilder, Audiodaten, Objekte, Klassen oder Bedeutung.

## Gemeinsame Verträge

`ReceptorContactFrame` bewahrt:

- Modalitätsherkunft,
- Rezeptorgeometrie,
- stabile Trägeridentitäten,
- Quellzeitfenster,
- normalisierte Kontaktwerte.

`CommonFieldTime` ordnet gleichzeitig verfügbare Rezeptorkontakte einem
gemeinsamen Intervall der Organismusuhr zu. Die Quelluhren werden nicht
umgedeutet oder als gleich angenommen.

`ReceptorNeuronDockMap` bildet jeden Rezeptorträger genau auf ein Dock-Neuron
ab. Die Abbildung enthält keine Gewichte, Gewinnerregel, Fusion oder Semantik.

## Rezeptorenverteiler

Der `ReceptorDistributor` besitzt offene, stabile `ReceptorDock`-Identitäten.
Er prüft Herkunft und Geometrie, sortiert die Übergabe kanonisch und bleibt
nach einer Verteilung zustandslos.

Er darf nicht:

- Kontaktwerte zwischen Modalitäten verrechnen,
- einen multimodalen Mustervektor erzeugen,
- Memory oder Nachhall tragen,
- Modalitäten bewerten oder priorisieren,
- fehlende Modalitäten durch Nullwerte ersetzen.

## Übergang in das Feld

Alle Docks gehören zu derselben `SharedMCMField`-Instanz und adressieren
Neuronen derselben `MCMNeuronLayer`. Die Dockbereiche bewahren technische
Herkunft, sind aber keine getrennten MCM-Felder.

Jeder Dockbereich erhält eindeutige Positionen innerhalb derselben
Feldgeometrie. Eine künstliche Modalitätsachse mit ausschließlich
spurinterner Wahrnehmung ist nicht zulässig. Benachbarte Positionen
verschiedener Docks dürfen daher in den normalen lokalen Feldproben
auftauchen, ohne dass dafür eine feste crossmodale Kante gespeichert wird.

Eine Feldaktualisierung ist atomar: Alle vorhandenen Kontakte und lokalen
Feldproben werden aus demselben vorherigen Zustand verarbeitet. Erst danach
entsteht der nächste vollständige Feldzustand.

## Freigabestatus

Implementiert und geprüft sind die technischen Verträge, verlustfreie
Verteilung, gemeinsame Zeit, Reihenfolgeunabhängigkeit und fehlende
Modalitäten.

Nicht freigegeben sind Feldtopologie, Beziehungsmemory, semantische Resonanz,
Reflexionsrückwirkung, Offline-Dynamik und eine organische
MCM-Neuronenübergangsfunktion.
