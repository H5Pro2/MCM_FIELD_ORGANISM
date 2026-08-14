# S1-EA0: E1 siebenarmiger eingefrorener Probe-Runner

## Status

Der private siebenarmige Probe-Runner ist mit synthetischen E1-
Bildungszustaenden und einer kleinen kontrollierten AV-Geometrie ausgefuehrt
und abgenommen. Er ist an die S1-DZ-Ergebnisoberflaeche angeschlossen. Der
kanonische S1-DY-Einstieg und alle registrierten S1-EA-Dateipfade bleiben
gesperrt.

## Implementierung

```text
mcm_field_organism/e1_refined_seven_arm_probe_runner.py
tests/test_e1_refined_seven_arm_probe_runner.py
```

Normalisierter Implementierungsdigest:

```text
c48ecf2322b82c7cf215eeefc4f12083fc7be9b921906d1c5b1ebccadd1516db
```

## Probeablauf

Fuer genau ein bereits gebildetes E1-Ergebnis erzeugt der Runner sieben
frische, wertidentische und objektgetrennte Felder:

```text
P0
AB aktiv
BA aktiv
AB Rueckwirkungsablation
BA Rueckwirkungsablation
AB fester Adapter
BA fester Adapter
```

Alle Rezeptorsupports werden ueber den vorhandenen completion-basierten
Handoff genau einmal zugeordnet. E1 bleibt waehrend jedes Schritts als
dasselbe AB- beziehungsweise BA-Objekt eingefroren. Der feste Adapter eines
Schritts wird direkt aus dem passenden aktiven Arm desselben Schritts
uebernommen.

Der Runner gibt nur die sieben Feldendigests, aktive S/H-Vektoren,
Nach-Probe-Zustandsdigests, Supportkontrolle sowie Probeablations- und
Fixed-Adapter-Rest an S1-DZ zurueck.

Der geometrieneutrale private Kern und der explizit synthetische Wrapper
sind seit S1-EA2 getrennt benannt. Dadurch verwendet die kanonische
Verdrahtung keine synthetisch benannte Schnittstelle.

## Abnahme

In der synthetischen Abnahme gelten:

- Probeablation gegen P0: exakt `0.0`;
- aktiver Arm gegen passenden festen Adapter: exakt `0.0`;
- AB- und BA-Zustandsobjekte bleiben unveraendert;
- unvollstaendiger Zeithorizont wird abgewiesen;
- wiederverwendete statt frischer Feldobjekte werden vor der Probe
  abgewiesen;
- alle drei Verfeinerungsrollen lassen sich zum S1-DX-Container komponieren.

```text
5 fokussierte Tests
375 Tests im vollstaendigen E1-Verbund
OK
```

## Aussagegrenze

Die Abnahme verwendet keine kanonische 84-Knoten-AV-Welt und liefert keine
kanonischen Effektwerte. Sie begruendet keinen Bildungs-, Transfer-, Memory-,
Semantik-, Organisations-, Topologie-, Selbstregulations- oder KI-Befund.

## Anschluss

S1-EA1 implementiert nun den kanonisch gebundenen Fuenfarm-Bildungsadapter
und nimmt seinen Kern mit ersetzten synthetischen Eingaben ab. Die
Gesamtverdrahtung zur kanonischen Probe bleibt offen.
