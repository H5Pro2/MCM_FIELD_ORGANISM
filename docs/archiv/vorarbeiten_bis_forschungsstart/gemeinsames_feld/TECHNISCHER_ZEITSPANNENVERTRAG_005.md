# Technischer Zeitspannenvertrag 005

## Status

Passiver Runtimevertrag vor `GF_001`.

Der Vertrag ergänzt keine MCM-Übergangsgleichung. Er macht einem explizit
übergebenen Neuronenübergang lediglich die gemessene Zeitspanne eines atomaren
Feldvorschlags zugänglich.

## Vertrag

`MCMFieldStepTime` enthält ausschließlich:

- technische Organismusuhr,
- Starttick,
- Endtick,
- offen ausgewiesene Ticks pro Sekunde.

Daraus sind nur `elapsed_ticks` und `elapsed_seconds` ableitbar.

Der Vertrag enthält keine Aktivität, keinen Rezeptorkontakt, keinen Nachhall,
keine Gewichtung, keine Beziehung, kein Memory und keine Semantik.

## Einbindung

Ein `MCMNeuronLayer.advance(...)` kann optional genau einen Zeitvertrag für
den gesamten atomaren Vorschlag erhalten. Derselbe unveränderliche Vertrag
wird an jeden `MCMNeuronDrive` dieses Schritts weitergereicht.

```text
vorheriger Neuronenzustand
+ aktuelle lokale Wahrnehmung
+ optionale gemessene Schrittzeit
-> explizit übergebener Übergang
```

Die Zeitspanne wird nicht:

- in `MCMNeuron` gespeichert,
- in den Neuronendigest aufgenommen,
- automatisch in Aktivierung oder Nachhall umgerechnet,
- aus einer Modalität abgeleitet,
- als Feldtickzähler interpretiert.

## Kontrollen

Fünf Kontrollen zeigen:

1. Nanosekundenintervalle werden ohne Rundung als Sekunden lesbar,
2. alle Neuronenvorschläge erhalten dasselbe Vertragsobjekt,
3. bestehende Übergänge liefern mit und ohne Zeitvertrag denselben Digest,
4. Zeitrücklauf, Nullintervalle und ungültige Tickraten werden abgewiesen,
5. der öffentliche Vertrag besitzt keine Aktivitäts-, Beziehungs- oder
   Memoryrolle.

## Wichtige Grenze

Der gemeinsame `SharedMCMField`-Pfad erzeugt den Zeitvertrag noch nicht
automatisch. Damit ist noch nicht entschieden:

- wann ein Feldschritt stattfindet,
- ob ein Sensorereignis einen vollständigen Feldschritt auslöst,
- wie überlappende Rezeptor-Reads zeitlich eingeordnet werden,
- ob und wie eine spätere MCM-Dynamik Zeit verwendet.

Diese Trennung verhindert, dass die technische Notwendigkeit realer Dauer
bereits als Feldmechanik ausgegeben wird.

## Befund

Die MCM-Neuronenschicht kann reale verstrichene Zeit als neutralen,
atomar gleichen Übergangskontext tragen, ohne ihren Zustand oder vorhandene
Baselines zu verändern.

Das ist E1 für den technischen Vertrag und weiterhin E0 für eine zeitabhängige
MCM-Felddynamik.

## Konsequenz für GF_001

`GF_001` bleibt geschlossen.

Als nächstes muss rein technisch geklärt werden, wie aus der realen Folge
asynchroner Rezeptorabschlüsse eine lückenlose Folge von Feldzeitspannen
entsteht. Dabei dürfen weder Audioereignisse die Schrittfolge dominieren noch
visuelle Zustände gehalten, ausgewählt oder rekonstruiert werden.

Die nachfolgende
[Technische Feldzeitpartition 006](TECHNISCHE_FELDZEITPARTITION_006.md)
erzeugt eine solche lückenlose Zeitdarstellung, zeigt aber, dass deren Grenzen
weiterhin nahezu vollständig den nativen Sensorabschlüssen folgen. Sie ist
daher noch keine Feldschrittfolge.

Feldkopplung, Topologie, Memory, Semantik, Reflexion und Selbstregulation
bleiben geschlossen.
