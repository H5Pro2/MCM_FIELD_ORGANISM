# S1-KW: B1/P_IK-C03-Auswahl und Ausfuehrungsvertrag

## Ergebnis

S1-KW waehlt als naechsten einzelnen technischen Fall exakt C03: die feste
B1-Adaptergegenbaseline unter dem registrierten Profil
`P_IK_INTERFERENCE` auf der offenen Dreiknotengeometrie. Die Auswahl ist
kein Interferenz-, Baseline- oder Kandidatenurteil und bindet kein erwartetes
Vorzeichen.

Gebunden sind r2, r4 und r8. Pro Refinement starten `P_IK_A_B_A` und
`P_IK_A_GAP_A` jeweils unabhaengig aus bitidentischen korrigierten B1-
Frischzustaenden. Feld und privater fester Adapter werden nur innerhalb der
je vier geordneten Intervalle einer Sequenz getragen. Zwischen Sequenzen und
Refinements wird kein Zustand getragen.

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

`B1_PIK_C03_SELECTED_THREE_REFINEMENT_TWO_SEQUENCE_DUAL_DIGEST_TWENTY_FOUR_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`9db475712bf914744e79b01ea1c930b517e339742071f1e03e1961ec68cef6d0`

## Grenzen

S1-KW implementiert keinen Runner und fuehrt nichts aus. C03, die
24-Fall-Matrix, B2/P_IK, weitere Rollen, Baseline- und Kandidatenurteile,
Runtimeintegration und Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KX darf ausschliesslich die drei gebundenen B1/P_IK-Runner-IDs
implementieren und r2, r4 sowie r8 je einmal innerhalb des 24-Intervall-
Budgets ausfuehren.
