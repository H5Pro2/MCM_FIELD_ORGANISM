# S1-EC47: Synthetische Common-Probe-Runnerintegration

## Ziel

EC47 integriert den EC45-Rollenvertrag und die vorregistrierte EC46-
Auswertung ausschliesslich mit typisierten synthetischen Probevektoren.
Es werden keine Feldkerne aufgerufen.

## Fixture

Die Fixture erzeugt fuer `r2`, `r4` und `r8` jeweils alle acht Rollen:

- P0-reset AB und BA;
- E1 aktiv AB und BA;
- E1-Probe-Rueckwirkungsablation AB und BA;
- E1-Bildungsablation AB und BA.

Damit werden insgesamt 24 Samples verarbeitet. Alle Samples besitzen dieselbe
geordnete synthetische Neuronengeometrie. Die drei Kontrollfamilien sind
exakt null. Das synthetische aktive Signal konvergiert von r2 nach r8 und
erfuellt absichtlich die EC46-Regel.

## Ergebnis

Die EC46-Funktion liefert fuer die konstruierten Fixturewerte:

`NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE`

Diese Ausgabe zeigt nur, dass Rollen, Kontrastbildung, Verfeinerungsreste und
Entscheidungsfunktion vollstaendig verbunden sind. Sie ist keine Messung und
keine Forschungsevidenz.

- 24 synthetische Samples;
- null reale Feldschritte;
- alle Rollen pro Verfeinerung vorhanden;
- gemeinsame Neuronenreihenfolge erhalten;
- keine Persistenz;
- keine Forschungsentscheidung und kein Claim.

15 fokussierte gemeinsame Tests bestehen.

Fixture-Digest:
`45fc3b5bf22451d4ca0aa49422d2523bd02b94558b10688085501fd99aec34f9`

## Grenze

EC47 belegt nicht, dass der reale E1-Rueckwirkungsweg dieselben typisierten
Probevektoren korrekt liefern kann. Insbesondere ist noch nicht statisch
geklaert, wie gebildete E1-Zustaende auf ein identisches zurueckgesetztes
Ausgangsfeld uebergeben werden, ohne den terminalen P0-Feldzustand
mitzunehmen.

## Naechster Schritt

Am besten geht es mit S1-EC48 weiter: rein statisch die vorhandenen E1-
Bildungs-, Reset-, Rueckwirkungs- und Probe-Kerne gegen die acht EC45-Rollen
auditieren. Noch keine reale Common-Probe-Ausfuehrung.
