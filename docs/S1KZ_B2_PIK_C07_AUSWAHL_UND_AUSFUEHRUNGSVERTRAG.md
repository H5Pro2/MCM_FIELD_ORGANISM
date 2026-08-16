# S1-KZ: B2/P_IK-C07-Auswahl und Ausfuehrungsvertrag

## Ergebnis

S1-KZ waehlt als naechsten einzelnen technischen Fall exakt C07: die
zustandsbehaftete B2-S2-Integratorgegenbaseline unter dem registrierten
Profil `P_IK_INTERFERENCE` auf der offenen Dreiknotengeometrie. Die Auswahl
ist kein Interferenz-, Baseline- oder Kandidatenurteil und bindet kein
erwartetes Vorzeichen.

Gebunden sind r2, r4 und r8. Pro Refinement starten `P_IK_A_B_A` und
`P_IK_A_GAP_A` jeweils unabhaengig aus bitidentischen korrigierten B2-
Frischzustaenden mit vollstaendigem Null-L-Zustand. Feld und L-Zustand werden
nur innerhalb der je vier geordneten Intervalle einer Sequenz getragen.
Zwischen Sequenzen und Refinements wird kein Zustand getragen.

Jeder atomare v2-Output muss zwei terminale Checkpoints, sechs signed
Komponenten und acht Adapterdiagnostikrecords enthalten. Alle Checkpoint-IDs
muessen ihrer Eltern-Replik-ID entsprechen. Nur die Vergleichsdigests muessen
ueber r2/r4/r8 bitidentisch sein.

## Endliches Budget

- drei Zielrepliken, je einmal;
- zwei unabhaengige Sequenzen je Replik;
- vier Intervalle je Sequenz und acht je Replik;
- hoechstens 24 neue Intervallaufrufe;
- kein Retry und keine Wiederholung.

Entscheidung:

`B2_PIK_C07_SELECTED_THREE_REFINEMENT_TWO_SEQUENCE_DUAL_DIGEST_TWENTY_FOUR_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`6a9bf425c073c53a3ac2270e0da3bccd22469ec96b047ec59583edd42c05ace5`

## Grenzen

S1-KZ implementiert keinen Runner und fuehrt nichts aus. C07, die
24-Fall-Matrix, weitere Rollen, Baseline- und Kandidatenurteile,
Runtimeintegration und Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-LA darf ausschliesslich die drei gebundenen B2/P_IK-Runner-IDs
implementieren und r2, r4 sowie r8 je einmal innerhalb des 24-Intervall-
Budgets ausfuehren.
