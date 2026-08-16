# S1-LC: B1/P_IN-C04-Auswahl und Ausfuehrungsvertrag

## Ergebnis

S1-LC waehlt als naechsten einzelnen technischen Fall exakt C04: die feste
B1-Adaptergegenbaseline unter dem registrierten Profil
`P_IN_RELEASE_REUSE` auf der offenen Dreiknotengeometrie. Die Auswahl ist
kein Freigabe-, Wiederverwendungs-, Baseline- oder Kandidatenurteil und
bindet kein erwartetes Vorzeichen.

Gebunden sind r2, r4 und r8. Pro Refinement starten `P_IN_RECOVERY_ON` und
`P_IN_RECOVERY_OFF` jeweils unabhaengig aus bitidentischen korrigierten B1-
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

`B1_PIN_C04_SELECTED_THREE_REFINEMENT_TWO_SEQUENCE_DUAL_DIGEST_TWENTY_FOUR_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`8aa472193fc6ec37912098a1d37c7d1c33a6d8bde5cca031f05645af276f9639`

## Grenzen

S1-LC implementiert keinen Runner und fuehrt nichts aus. C04, die 24-Fall-
Matrix, B2/P_IN, weitere Rollen, Baseline- und Kandidatenurteile,
Runtimeintegration und Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-LD darf ausschliesslich die drei gebundenen B1/P_IN-Runner-IDs
implementieren und r2, r4 sowie r8 je einmal innerhalb des 24-Intervall-
Budgets ausfuehren.
