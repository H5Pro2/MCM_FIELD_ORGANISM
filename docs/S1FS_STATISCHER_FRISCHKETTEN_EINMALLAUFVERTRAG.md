# S1-FS: Statischer Frischketten-Einmallaufvertrag

## Gebundener Lauf

S1-FS beschreibt genau einen neuen, nicht persistenten Same-session-Lauf:

```text
kontrollierte AV-Reihenfolge
-> 15 frische Formation-Arme in r2/r4/r8
-> Capture und Formationskontrolle
-> 30 objektgetrennte gemeinsame Probe-Arme
-> eine atomare In-memory-Rueckgabe
-> erst danach EC46- und Fixed-Adapter-Auswertung
```

Gebundene Obergrenzen:

```text
Formation                    15 Aufrufe / 14.000 Feldschritte
Probe                        30 Aufrufe / 14.000 Feldschritte
Gesamt                       45 Aufrufe / 28.000 Feldschritte
freier RAM                   mindestens 4 GiB
Wandzeit                     maximal 1.800 Sekunden
```

## Formationsgate

Die Probe darf nur beginnen, wenn alle 15 Formationsergebnisse vollstaendig
erfasst sind und Identity-, Formationsablations-, Ressourcen-, Zustands- und
Konvergenzkontrollen bestehen. Bei einem Fehler endet der Versuch vor der
ersten Probe ohne Teilentscheidung.

## Probe und Rueckgabe

Jeder Probearm erhaelt ein wertidentisches, aber objektgetrenntes frisches
Feld. Der zugeordnete Formationszustand bleibt waehrend der Probe eingefroren.
Zur atomaren Rueckgabe gehoeren insbesondere alle r2/r4/r8-Ordungsvektoren,
die drei Kontrollfamilien, beide Fixed-Adapter-Vergleiche, Zustands- und
Felddigests sowie die exakte Schrittbilanz.

EC46 und die Fixed-Adapter-Erklaerung werden erst nach der vollstaendigen
Rueckgabe getrennt ausgewertet. Ein Teilresultat, Retry oder eine
Nachparametrierung darf keine Entscheidung erzeugen.

## Status und Grenzen

Entscheidung:
`FRESH_CHAIN_ONE_SHOT_BOUND_AWAITING_PREFLIGHT_AND_EXPLICIT_OWNER_AUTHORIZATION`.

S1-FS autorisiert und implementiert keinen realen Runner. Historische
Zustaende und alte Freigaben sind nicht wiederverwendbar. Persistenz und
Memory-, Feldzeit-, Reaktivierungs-, Organisations-, Semantik-,
Selbstregulations- oder KI-Claims bleiben geschlossen.

## Bester naechster Schritt

S1-FT soll den Eingabe-, Ressourcen-, Reihenfolge- und atomaren
Rueckgabepreflight mit typisierten synthetischen Objekten implementieren und
fail-closed abnehmen. Noch keine reale Runnerimplementierung, keine
Besitzerautorisierung und keine Ausfuehrung.
