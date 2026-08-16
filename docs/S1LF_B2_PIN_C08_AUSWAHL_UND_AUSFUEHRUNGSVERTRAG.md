# S1-LF: B2/P_IN-C08-Auswahl und Ausfuehrungsvertrag

## Ergebnis

S1-LF waehlt als naechsten einzelnen technischen Fall exakt C08: die
zustandsbehaftete B2-S2-Integratorgegenbaseline unter dem registrierten
Profil `P_IN_RELEASE_REUSE` auf der offenen Dreiknotengeometrie. Die Auswahl
ist kein Freigabe-, Wiederverwendungs-, Baseline- oder Kandidatenurteil und
bindet kein erwartetes Vorzeichen.

Gebunden sind r2, r4 und r8. Pro Refinement starten `P_IN_RECOVERY_ON` und
`P_IN_RECOVERY_OFF` jeweils unabhaengig aus bitidentischen korrigierten B2-
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

`B2_PIN_C08_SELECTED_THREE_REFINEMENT_TWO_SEQUENCE_DUAL_DIGEST_TWENTY_FOUR_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`472311d23946537738173e5ae31fe25ea4fd9d3fc49f9a69e406c6647cc66625`

## Grenzen

S1-LF implementiert keinen Runner und fuehrt nichts aus. C08, die
24-Fall-Matrix, weitere Rollen, Baseline- und Kandidatenurteile,
Runtimeintegration und Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-LG darf ausschliesslich die drei gebundenen B2/P_IN-Runner-IDs
implementieren und r2, r4 sowie r8 je einmal innerhalb des 24-Intervall-
Budgets ausfuehren.
