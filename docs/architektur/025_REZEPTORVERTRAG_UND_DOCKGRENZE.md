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

`CommonFieldTime` trägt ein gemessenes technisches Koordinationsintervall auf
der Organismusuhr. Es belegt nicht automatisch Aufnahmebeginn,
Wahrnehmungsgültigkeit oder gleichzeitige Weltstütze mehrerer
Rezeptorzustände. Die Quelluhren werden nicht umgedeutet oder als gleich
angenommen.

Der Abschluss dieses Intervalls ist die gemessene kausale Übergabegrenze:
Der vollständig reduzierte Zustand darf ab dort vom Organismus gelesen
werden. Diese Grenze ist keine rekonstruierte Außenweltzeit, keine
Gültigkeitsdauer und kein automatischer Feldtakt. Der
[Technische Übergabevertrag 009](../gemeinsames_feld/TECHNISCHER_UEBERGABEVERTRAG_009.md)
hält diese Trennung verbindlich fest.

`ReceptorNeuronDockMap` bildet jeden Rezeptorträger genau auf ein Dock-Neuron
ab. Die Abbildung enthält keine Gewichte, Gewinnerregel, Fusion oder Semantik.

## Rezeptorenverteiler

Der `ReceptorDistributor` besitzt offene, stabile `ReceptorDock`-Identitäten.
Er prüft Herkunft und Geometrie, sortiert die Übergabe kanonisch und bleibt
nach einer Verteilung zustandslos.

Der [Rezeptorzustandsrollen-Abgleich 011](../gemeinsames_feld/TECHNISCHER_REZEPTORZUSTANDSROLLEN_ABGLEICH_011.md)
präzisiert den aktuellen Zustandsbesitz: Der auditive Rezeptor trägt ein
endliches rollendes Samplefenster, der visuelle Rezeptor keine Bildgeschichte.
Beide übergeben unveränderliche Snapshots; weder Dock noch Verteiler halten
den letzten Kontakt als gegenwärtigen Zustand fest.

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
MCM-Neuronenübergangsfunktion. Rezeptoreigene Quellfenster sind weiterhin
nicht auf die gemeinsame Organismusuhr abgebildet; für die kausale Übergabe
ist eine solche Rekonstruktion jedoch nicht erforderlich.

Die [Technische verlustfreie Vorschlagsübergabe 016](../gemeinsames_feld/TECHNISCHE_VERLUSTFREIE_VORSCHLAGSUEBERGABE_016.md)
bewahrt inzwischen mehrere abgeschlossene reduzierte Zustände je Dock und
Vorschlagsspanne vollständig. Diese passive Übergabe ist noch keine
Runtime-Freigabe: `ReceptorDistribution` und `MCMFieldPerception` können eine
solche variable Folge derzeit nicht ohne Auswahl oder Reduktion in einem
atomaren Feldvorschlag darstellen.

Die [Technische Feldeingangs-Kapazitätsfalsifikation 017](../gemeinsames_feld/TECHNISCHE_FELDEINGANGS_KAPAZITAETSFALSIFIKATION_017.md)
belegt diese Grenze an den tatsächlichen Verträgen. Sie gibt weder eine
Sequenzschnittstelle noch asynchrone lokale Feldwirkung frei; beide bleiben
als getrennte Architekturhypothesen zu falsifizieren.

Der [Technische Zeitträger-Architekturabgleich 018](../gemeinsames_feld/TECHNISCHER_ZEITTRAEGER_ARCHITEKTURABGLEICH_018.md)
trägt keine der beiden Hypothesen als Runtime. Vollständige Sequenznutzlast
bleibt in ihrer Größe ratenexponiert; der vorhandene serielle Wirkungspfad
bindet weiterhin vollständige Feldfortschritte an Sensorabschlüsse.

Der [Funktionale Zeitwirkungsvertrag 019](../gemeinsames_feld/FUNKTIONALER_ZEITWIRKUNGSVERTRAG_019.md)
legt daraufhin nur die Prüffunktionen für einen späteren Zeitträger fest. Der
synthetische Ground-Truth-Observer ist kein Bestandteil der Dock- oder
Feldruntime.

Die [Passive Zeitrepräsentations-Scheiterkarte 020](../gemeinsames_feld/PASSIVE_ZEITREPRAESENTATIONS_SCHEITERKARTE_020.md)
verwirft Segmentanzahl, Endpunkt und zeitgewichteten Mittelwert als gemeinsam
ausreichende Nullrepräsentationen. Die vollständige bekannte Stützbahn bleibt
variable Ground Truth; sie wird nicht zur Dock- oder Feldschnittstelle.

Die [Passive Kompaktzusammenfassungs-Kollision 021](../gemeinsames_feld/PASSIVE_KOMPAKTZUSAMMENFASSUNGS_KOLLISION_021.md)
zeigt zusätzlich, dass auch 13 feste Standardkennwerte zwei exakte
Zeitumkehrungen nicht unterscheiden. Die Dockgrenze erhält dadurch keine neue
Nutzlast; lediglich gerichtete Zeitinformation bleibt als offene
Prüfeigenschaft bestehen.

Der [Passive gerichtete Zeitmoment-Abgleich 022](../gemeinsames_feld/PASSIVER_GERICHTETER_ZEITMOMENT_ABGLEICH_022.md)
weist nach, dass eine feste gerichtete Projektion diese Zeitumkehr
unterscheiden kann, aber andere geordnete Bahnen kollidieren lässt. Auch dieses
Moment wird daher nicht Bestandteil der Dock- oder Feldschnittstelle.
