# S1-KQ: B1/P_IH-C02-Auswahl und Ausfuehrungsvertrag

## Ergebnis

S1-KQ waehlt als naechsten einzelnen technischen Fall exakt C02: die feste
B1-Adaptergegenbaseline unter dem registrierten Profil `P_IH_ATTENUATION`
auf der offenen Zweiknotengeometrie. Die Auswahl ist kein Baseline- oder
Kandidatenurteil und bindet kein erwartetes Vorzeichen.

## Gebundener Umfang

Gebunden sind die drei registrierten Repliken r2, r4 und r8. Jede startet aus
einem eigenen korrigierten B1-Frischzustand. Innerhalb einer Replik beginnt
die einzige Sequenz `P_IH_A_A_A` einmal frisch und traegt das vollstaendige
Feld sowie den privaten festen Adapter ueber drei geordnete A-Intervalle.
Zwischen Refinements wird kein Zustand getragen.

Jeder atomare v2-Output muss drei Checkpoints, acht signed Komponenten und
drei Adapterdiagnostikrecords enthalten. Alle Checkpoint-IDs muessen ihrer
Eltern-Replik-ID entsprechen. Nur die Refinement-Vergleichsdigests muessen
ueber r2, r4 und r8 bitidentisch sein.

## Endliches Budget

- genau drei Zielrepliken, je einmal;
- genau drei Intervallaufrufe je Replik;
- hoechstens neun neue Intervallaufrufe insgesamt;
- kein Retry und keine Wiederholung.

Entscheidung:

`B1_PIH_C02_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_NINE_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`34cc3254288da37a841d9f627383d38c2d40aad8f48cf9e350b40d0c4ac01f0e`

## Grenzen

S1-KQ implementiert keinen Runner und fuehrt weder Replik noch Intervall aus.
C02 und die 24-Fall-Matrix bleiben unpubliziert. B2/P_IH, weitere Rollen,
Baseline- und Kandidatenurteile, Runtimeintegration und Forschungslaeufe
bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-KR darf ausschliesslich die drei gebundenen B1/P_IH-Runner-IDs
implementieren und r2, r4 sowie r8 je einmal innerhalb des
Neun-Intervall-Budgets ausfuehren.
