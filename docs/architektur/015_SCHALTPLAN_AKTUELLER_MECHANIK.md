# Schaltplan der aktuellen Mechanik

![Schaltplan des gemeinsamen MCM-Feldes](../bilder/architektur/mcm_field_organism_gemeinsames_feld_schaltplan.png)

## Weltkontakt und Rezeptoren

```text
Kamera   -> visuelle Rezeptoren --\
Mikrofon -> auditive Rezeptoren ----> Rezeptorenverteiler
Sensor   -> taktile Rezeptoren ----/
```

Die Rezeptoren bleiben modalitätsspezifisch. Sie bewahren lokale Herkunft,
Geometrie und Quellzeit, erzeugen aber keine Objekte, Klassen oder Bedeutung.

## Rezeptorenverteiler und Docks

Der Rezeptorenverteiler erhält ausschließlich abgeschlossene
`ReceptorContactFrame`-Zustände. Er ordnet sie offenen Docks und einer
gemeinsamen Organismuszeit zu.

Er besitzt:

- kein Memory,
- keine Feldgleichung,
- keine Modalitätsgewichte,
- keine Fusion,
- keinen Musterprüfer.

Die visuellen, auditiven und später taktilen Docks sind technische
Andockbereiche desselben Feldes. Sie sind keine eigenen MCM-Felder.

## Eine MCM-Neuronenschicht

```text
Rezeptordocks
-> eine MCMNeuronLayer
-> ein vollständiger gemeinsamer Feldzustand
```

Alle Feldneuronen verwenden denselben lokalen Neuronenvertrag. Sie lesen
Rezeptorkontakt, eigenen schnellen Zustand und lokale Feldproben aus demselben
abgeschlossenen vorherigen Takt. Erst nach der vollständigen Berechnung wird
der nächste Feldzustand übernommen.

Die aktuelle Baseline projiziert nur Rezeptorkontakte. Sie ist keine
organische MCM-Neuronenfunktion.

## Feldtopologie und organisches Memory

Feldtopologie ist im Schaltplan innerhalb des gemeinsamen Feldes eingezeichnet,
weil eine spätere wirksame Beziehungsorganisation zum Organismuszustand
gehören müsste. Sie ist keine nachgeschaltete Datenbank.

Noch nicht implementiert sind:

- Entstehung wirksamer Beziehungen,
- Stabilisierung und Abschwächung,
- Lösung und Wiederbindung,
- endliche Beziehungsressourcen,
- funktionaler Wechsel nach neuer Weltgeschichte.

## Semantische Resonanz

Semantische Resonanz ist als mögliche entstehende Feldfähigkeit markiert. Es
gibt kein nachgeschaltetes Syntaxmodul und keinen multimodalen
Musterklassifikator. Eine innere Bezeichnung müsste aus wiederkehrender
Feldform und Beziehungsgeschichte entstehen.

Sprache darf später als weitere erfahrene Feldform andocken, aber keine festen
Klassen oder Bezeichnungen in das Feld schreiben.

## Reflexion und Offline-Erholung

Reflexion liegt außerhalb der direkten Weltursache. Ein späterer
Reflexionsvorgang müsste den gegenwärtigen Feldzustand wieder auf dieselbe
MCM-Neuronenschicht wirken lassen. Die Rückwirkung ist noch Forschung und
nicht programmiert.

Offline-Erholung ist ein Betriebsmodus desselben Feldes bei reduziertem
Weltkontakt. Sie ist kein Training, kein Replay und kein separates
Memory-System.

## Aktive Runtime-Grenze

```text
ReceptorContactFrame
-> ReceptorDistributor
-> ReceptorDock
-> ReceptorNeuronDockMap
-> SharedMCMField
-> MCMNeuronLayer
-> SharedMCMFieldSnapshot
```

Die frühere Kette

```text
SensorMCMField
-> MCMDistributor
-> MCMFieldWindow
-> MultimodalPatternChecker
```

ist keine aktuelle Architektur mehr. Sie bleibt nur als direkt importierbare
historische Versuchsbaseline für frühere Befunde erhalten.
