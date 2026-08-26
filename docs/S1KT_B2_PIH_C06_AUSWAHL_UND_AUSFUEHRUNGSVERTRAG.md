# S1-KT: B2/P_IH-C06-Auswahl und Ausfuehrungsvertrag

## Ergebnis

S1-KT waehlt als naechsten einzelnen technischen Fall exakt C06: die
zustandsbehaftete B2-S2-Integratorgegenbaseline unter dem registrierten
Profil `P_IH_ATTENUATION`. Die Auswahl bindet kein erwartetes Vorzeichen und
ist kein Baseline- oder Kandidatenurteil.

Gebunden sind r2, r4 und r8. Jede Replik startet aus einem eigenen
korrigierten B2-Frischzustand. Die einzige Sequenz `P_IH_A_A_A` traegt das
vollstaendige Feld und den vollstaendigen privaten L-Zustand ueber drei
geordnete A-Intervalle. Zwischen Refinements wird kein Zustand getragen.

Jeder atomare v2-Output muss drei Checkpoints, acht signed Komponenten und
drei Diagnostikrecords enthalten. Alle Checkpoint-IDs muessen ihrer
Eltern-Replik-ID entsprechen. Nur die Vergleichsdigests muessen ueber
r2/r4/r8 bitidentisch sein.

## Endliches Budget

- drei Zielrepliken, je einmal;
- drei Intervalle je Replik;
- hoechstens neun neue Intervallaufrufe;
- kein Retry und keine Wiederholung.

Entscheidung:

`B2_PIH_C06_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_NINE_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`2038b23de29a1e4336e8341fae939612295bf52163c9ccfdbe646c3350368675`

## Grenzen

S1-KT implementiert keinen Runner und fuehrt nichts aus. C06, die
24-Fall-Matrix, weitere Rollen, Baseline- und Kandidatenurteile,
Runtimeintegration und Forschungslaeufe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KU darf ausschliesslich die drei gebundenen B2/P_IH-Runner-IDs
implementieren und r2, r4 sowie r8 je einmal innerhalb des
Neun-Intervall-Budgets ausfuehren.
