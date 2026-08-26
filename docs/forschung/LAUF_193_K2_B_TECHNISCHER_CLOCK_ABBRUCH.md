# Lauf 193

## Status

```text
decision: TECHNICALLY_ABORTED_BEFORE_MEASUREMENT
result artifact: keines
fachlicher Befund: keiner
```

## Ursache

Der K2-B-Quellenvertrag verwendete korrekt die neue gemeinsame Clock
`organism.mcm_f3_k2b`. Der fuer die passive Trajektorienbeobachtung
wiederverwendete E3-Helfer erzeugte den Vorschlagsschritt jedoch fest mit
`organism.mcm_f3_history`.

Der Handoff lehnte die verschiedenen Clocks vor der ersten F3-Fortsetzung ab.
Es wurden keine Checkpointmessungen, Kontraste oder Entscheidungen erzeugt.

## Erlaubte Korrektur

Der passive Helfer leitet die Schritt-Clock kuenftig direkt aus der bereits
validierten `ReceptorTimeSequence.clock_id` ab. Fuer die alten E3-Sequenzen ist
dies weiterhin exakt `organism.mcm_f3_history`; fuer K2-B ist es
`organism.mcm_f3_k2b`.

Unveraendert bleiben:

- alle Quellen und Digests;
- F3- und Baselinegleichungen;
- Parameter und Refinement;
- Pfade, Checkpoints und Probeintervalle;
- Metriken, Schwellen und Entscheidungen.

Die korrigierte einmalige Ausfuehrung erhaelt Laufnummer 194.
