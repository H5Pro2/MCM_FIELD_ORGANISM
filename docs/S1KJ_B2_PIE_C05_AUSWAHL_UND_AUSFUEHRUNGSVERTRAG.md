# S1-KJ: B2/P_IE-C05-Auswahl und Ausfuehrungsvertrag

## Ergebnis

S1-KJ waehlt als naechsten einzelnen technischen Fall exakt `C05`: die
zustandsbehaftete Gegenbaseline `B2_S2_LINEAR_INTEGRATOR` unter dem bereits
registrierten Profil `P_IE_CAUSAL_TWO_SUBSTEP` auf der offenen
Zweiknotengeometrie. Die Auswahl ist noch kein Baseline- oder
Kandidatenurteil.

## Gebundener Umfang

Gebunden sind die drei registrierten Repliken r2, r4 und r8. Jede Replik
startet aus einem eigenen korrigierten B2-Frischzustand. Innerhalb jeder
Replik starten `P_IE_F_HIGH` und `P_IE_R_HIGH` ebenfalls getrennt frisch. Der
vollstaendige private L-Zustand darf nur zwischen den zwei geordneten
Intervallen derselben Sequenz getragen werden.

Der korrigierte Frischzustand besitzt zwei kanonisch geordnete L-Eintraege
mit Wert null. Feld- und Privatdigest sind fest gebunden. Outputs muessen das
v2-Schema mit getrenntem Provenienz- und Refinement-Vergleichsdigest nutzen.
Nur die Vergleichsdigests muessen ueber r2, r4 und r8 bitidentisch sein.

## Endliches Budget

- genau drei Zielrepliken, je einmal;
- genau vier Intervallaufrufe je Replik;
- hoechstens zwoelf neue Intervallaufrufe insgesamt;
- kein Retry und keine Wiederholung.

S1-KJ implementiert keinen Runner und fuehrt weder Replik noch Intervall aus.
Ein C05-Falloutput darf erst in einer spaeteren Stufe zusammengesetzt werden,
wenn alle drei atomaren v2-Ausgaben angenommen sind.

Entscheidung:

`B2_PIE_C05_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_TWELVE_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`5f02c7ed2de53b713d19dbed514fd35d328a79c09663e119afc939da8949791d`

## Grenzen

Keine 24-Fall-Matrix wird publiziert. Baselineabschluss, Ranking,
Kandidatenvergleich, Runtimeintegration und Forschungsprobe bleiben
geschlossen. Aus diesem Vertrag folgt keine Speicher-, Lern- oder andere
weitergehende Funktionsbehauptung.

## Naechster zulaessiger Schritt

S1-KK darf ausschliesslich die drei gebundenen B2/P_IE-Runner-IDs
implementieren und r2, r4 sowie r8 je einmal innerhalb des
Zwoelf-Intervall-Budgets ausfuehren. Keine andere Rolle, kein anderer
Profilblock, keine Fallkomposition und kein Urteil.
