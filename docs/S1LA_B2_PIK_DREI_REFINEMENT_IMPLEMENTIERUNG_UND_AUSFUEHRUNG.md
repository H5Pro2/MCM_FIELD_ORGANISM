# S1-LA: B2/P_IK-Drei-Refinement-Implementierung und Ausfuehrung

## Ergebnis

S1-LA erweitert den privaten Ein-Replik-Runner exakt um die drei in S1-KZ
gebundenen B2/P_IK-IDs r2, r4 und r8. Jede Replik wurde genau einmal
ausgefuehrt. Pro Replik starteten `P_IK_A_B_A` und `P_IK_A_GAP_A`
unabhaengig aus dem korrigierten B2-Dreiknoten-Frischzustand mit
vollstaendigem Null-L-Zustand. Insgesamt wurden 24 Intervalle materialisiert
und durch den vorhandenen B2-S2-Integrator verarbeitet.

Die Runnerhuelle akzeptiert fuer P_IK zwei terminale Checkpoints, sechs
signed Komponenten und acht Adapterdiagnostikrecords pro Replik. Die
Checkpoint-IDs stimmen mit ihren Eltern-Replik-IDs ueberein. Modellkern,
Fixturewerte und Integratorgleichung wurden nicht geaendert.

## Technische Ausgaben

Vollstaendige Provenienz-Digests:

- r2: `97a9467bb6bfad7446b61c942f2b5ecb4a4646e2633840e61ccffa1f0e2f3dca`
- r4: `f2a175c61745a0a5eabd19c8e6204837ab7fdfa75056f1f46dbcfef13c96ab80`
- r8: `3d964198adf5c2518d99930e39d99441d85f68b48fa1ec8be22bd41c94e43862`

Gemeinsamer Refinement-Vergleichsdigest:

`721ad5a47e562ac25d67c96224a8a70e81545c70c61c60187be247a889522e09`

Alle sechs signed Komponenten sind klein, nicht null und ueber r2/r4/r8
bitidentisch. Die terminalen Feld-, L- und Adapteroutput-Digests
unterscheiden sich zwischen A-B-A und A-Gap-A, sind aber ueber die drei
Refinements bitidentisch. Dies ist ein reproduzierbarer technischer B2-
Zustandsunterschied, aber kein Interferenz-, Schwellen-, Baseline- oder
Kandidatenurteil.

Entscheidung:

`B2_PIK_R2_R4_R8_IMPLEMENTED_TWENTY_FOUR_INTERVALS_COMPARISON_IDENTICAL_SET_ACCEPTED`

Receipt-Digest:

`40d7e333af46e9bcdfb476648d62dd589428cc4fae07ee233d55017de5d19d25`

## Grenzen

C07 wurde noch nicht als Falloutput zusammengesetzt. Weitere Rollen und
Profile, die 24-Fall-Matrix, Baseline- und Kandidatenurteile,
Runtimeintegration sowie Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-LB darf ausschliesslich den technischen C07-Fallrecord aus den drei
bereits gebundenen S1-LA-Ausgaben zusammensetzen. Keine neue Replik und kein
neues Intervall und noch keine weitere Fallauswahl.
