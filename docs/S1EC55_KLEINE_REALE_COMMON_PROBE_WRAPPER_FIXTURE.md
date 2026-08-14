# S1-EC55: Kleine reale Common-Probe-Wrapper-Fixture

## Umfang

EC55 fuehrte ausschliesslich drei Slots fuer `n2/r2` in-memory aus:

1. `p0-reset-ab`;
2. `e1-active-ab`;
3. `e1-probe-feedback-ablated-ab`.

Ein aktiver AB-Zustand wurde einmal real gebildet und anschliessend auf zwei
getrennten, anfangs identischen Probefeldern mit demselben Common-Probe-
Stimulus verwendet. In einem Slot war die Rueckwirkung aktiv, im anderen
deaktiviert.

## Technischer Rohbefund

- Bildungsschritte: 402;
- Probeschritte: 200 je Slot;
- Gesamtschritte: 1.002;
- Aktiv/Rueckwirkungsablation Aktivierungs-Linf:
  `2.8709257103076702e-05`;
- Aktiv/Rueckwirkungsablation Nachhall-Linf:
  `1.7290444112694203e-05`;
- alle drei Ausgangsfelder digest-identisch und objektgetrennt;
- eingefrorener E1-Zustand in beiden E1-Slots unveraendert;
- vorbereitete Eingabeobjekte erhalten;
- keine Persistenz.

Ergebnisdigest:
`dbc057ec06ace7c30b0fe15bfe26244fd27184cf2ea3ef0d34ec292c11c2e1b0`

## Technische Interpretation

Der neue Wrapper erreicht den realen E1-Rueckwirkungsweg. Bei identischem
gebildetem AB-Zustand, identischem Probefeld und identischem Probeimpuls
erzeugt das gezielte Abschalten der Rueckwirkung eine messbare terminale
Felddifferenz in Aktivierung und Nachhall.

## Nichtnachweis

EC55 vergleicht weder AB mit BA noch n1 mit n2 und enthaelt keine
Bildungsablation. Der Lauf prueft daher nur die technische Funktion des
Wrappers und des Rueckwirkungsschalters. Er ist kein Nachweis fuer Memory,
Feldzeit, Organisation oder KI und keine Common-Probe-Forschungsentscheidung.

Die volle 48-Slot-Matrix wurde nicht ausgefuehrt.

## Naechster Schritt

Am besten geht es mit S1-EC56 weiter: den EC55-Rohbefund statisch gegen die
Fixture-Grenzen auditieren und daraus den kleinsten naechsten Kontrollumfang
festlegen. Keine unmittelbare Vollmatrix.
