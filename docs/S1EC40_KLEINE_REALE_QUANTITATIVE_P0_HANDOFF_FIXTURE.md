# S1-EC40: Kleine reale quantitative P0-Handoff-Fixture

## Zweck

S1-EC40 implementiert die in EC39 fehlende unmittelbare reale P0-Snapshot-
Uebergabe. Die Ausfuehrung ist auf die bestehende kleine n2/r2-Fixture mit
vier Supports und acht Schritten je P0-Arm begrenzt.

## Ablauf

1. `p0_repeated` und `p0_continuous` starten von getrennten Kopien desselben
   Anfangsfeldes.
2. Jeder Arm verarbeitet vier AV-Supports in acht Feldschritten.
3. Beide terminalen Felder werden unmittelbar als typisierte Snapshots
   erfasst.
4. Die Snapshots werden vor dem Verwerfen der Felder an EC36 uebergeben.

## Technisches Ergebnis

- ausgefuehrte Feldschritte: `16`
- Aktivierungs-Linf: `0.004439790780415592`
- Nachhall-Linf: `0.008155675046400305`
- quantitativer Paardigest:
  `49e8610ce8e031e8a835d55a7ddceb14a3d7ac8ee5db4ecbf072ee985917ea01`
- Fixture-Digest:
  `489bbebc403634d501daecea102b19860413e4b5b0c46dc7b743551888c8d26e`
- fokussierte gemeinsame Tests: `29 passed`

Die Werte bestaetigen nur, dass der kleine P0-Pfad eine komponentenweise
messbare Feldzustandsdifferenz an EC36 uebergibt. Sie sind wegen reduzierter
Supports und nur einer Verfeinerung keine Vollpilot-, Konvergenz-,
Wiederholungs- oder Memory-Evidenz.

## Schutzgrenze

Der Vollpilot wurde nicht ausgefuehrt. Keine Autorisierung wurde konsumiert,
nichts wurde persistiert und keine Ergebnisentscheidung oder Claim erzeugt.

## Naechster Schritt

S1-EC41 sollte EC39 nach der realen Handoff-Abnahme statisch neu bewerten und
den noch fehlenden Vollrunner-Integrationsschritt abgrenzen. Eine neue
Einmallauffreigabe darf erst nach dieser technischen Abnahme angefordert
werden.

