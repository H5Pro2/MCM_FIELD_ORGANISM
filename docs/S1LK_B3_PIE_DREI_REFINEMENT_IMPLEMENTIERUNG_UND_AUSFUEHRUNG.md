# S1-LK: B3/P_IE-Drei-Refinement-Implementierung und Ausfuehrung

## Ergebnis

S1-LK erweitert den privaten Ein-Replik-Runner exakt um die drei in S1-LJ
gebundenen B3/P_IE-IDs r2, r4 und r8. Die Frischzustandsrekonstruktion bildet
jetzt den vollstaendigen M-Zustand und den gebundenen Local-Leaky-Arm ab und
weist jede Digestabweichung vor dem ersten Intervall ab.

Jede Replik wurde genau einmal ausgefuehrt. Pro Replik starteten
`P_IE_F_HIGH` und `P_IE_R_HIGH` unabhaengig aus dem registrierten
B3-Zweiknoten-Frischzustand. Insgesamt wurden zwoelf Intervalle
materialisiert und durch den vorhandenen B3-Adapter verarbeitet.

## Technische Ausgaben

Vollstaendige Provenienz-Digests:

- r2: `9c0ebf0342764a340e724246d6966ec89c07a832a7bfc417dec07156a964d54f`
- r4: `93bbe47d45d6fd2891eb78bdd07ea04da2fc7b21cc602ee995b645ff97a281a1`
- r8: `c076735240e70c07af9f3e122f3ee295c147179778b33f5910e470cd61042b2a`

Refinement-Vergleichsdigests:

- r2: `e33475196e7ed50f5c3f8d175ef3515f17c1730dbb0d1835e919a024f7a73f62`
- r4: `3450b4a97a92455e03a560564ba46005906ddeeeb1f9ee843046ecdbff72ddf7`
- r8: `d12877344d259dd9e03ba81f765c73700641a1cc4e7232bf0613a4cda458c3e8`

Alle acht signed F-High-minus-R-High-Komponenten sind in r2, r4 und r8
null. Innerhalb eines Refinements besitzen die beiden unabhaengigen
Sequenzen bitidentische Checkpointdigestpaare. Die vollstaendigen Inhalte
und Digests unterscheiden sich aber zwischen r2, r4 und r8. Das ist fuer
B3 zulaessig und wird nicht als Baseline- oder Kandidatenurteil gewertet.

Entscheidung:

`B3_PIE_R2_R4_R8_IMPLEMENTED_TWELVE_INTERVALS_DISTINCT_REFINEMENT_OUTPUTS_ACCEPTED`

Receipt-Digest:

`ac97bedfa3811a8e41240c9b1b3a1a8288c5f40f05b678e6074d71852617c7c2`

## Grenzen

C09 wurde noch nicht als Falloutput zusammengesetzt. Weitere Rollen und
Profile, die 24-Fall-Matrix, Baseline- und Kandidatenurteile,
Runtimeintegration sowie Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-LL darf ausschliesslich den technischen C09-Fallrecord aus den drei
bereits gebundenen S1-LK-Ausgaben zusammensetzen und die vorregistrierten
r2-r4- sowie r4-r8-Komponentenreste berechnen. Keine neue Replik und kein
neues Intervall.
