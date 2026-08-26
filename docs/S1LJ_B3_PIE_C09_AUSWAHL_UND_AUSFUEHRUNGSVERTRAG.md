# S1-LJ: B3/P_IE-C09-Auswahl und Ausfuehrungsvertrag

## Ergebnis

S1-LJ waehlt als naechsten einzelnen technischen Fall exakt C09: die
Gegenbaseline `B3_F3_LOCAL_LEAKY` unter dem registrierten Profil
`P_IE_CAUSAL_TWO_SUBSTEP` auf der offenen Zweiknotengeometrie. Die Auswahl
ist noch kein Baseline- oder Kandidatenurteil.

## Gebundener Umfang

Gebunden sind die drei registrierten Repliken r2, r4 und r8. Innerhalb jeder
Replik starten `P_IE_F_HIGH` und `P_IE_R_HIGH` jeweils aus einem eigenen
vollstaendigen B3-Frischzustand. Dieser besitzt:

- gleichmaessige M-Massen von 0,5 auf node-a und node-b;
- den gebundenen Arm `mcm.s1jt.b3.local-leaky`;
- den kanonischen eingebetteten M-Zustandsdigest;
- getrennte Feld- und Privatdigests.

Feld, M-Zustand und gebundener Arm duerfen nur zwischen den zwei geordneten
Intervallen derselben Sequenz getragen werden.

Jede Ausgabe muss das v2-Schema mit getrenntem Provenienz- und
Refinement-Vergleichsdigest verwenden. Fuer B3 wird keine Bitidentitaet der
r2/r4/r8-Inhalte vorausgesetzt. Ein spaeterer C09-Fallrecord muss r4 als
Primaerausgabe behalten und die vollstaendigen gerichteten Komponentenreste
r2 minus r4 sowie r4 minus r8 publizieren.

## Endliches Budget

- genau drei Zielrepliken, je einmal;
- zwei unabhaengige Sequenzen pro Replik;
- zwei Intervallaufrufe je Sequenz;
- hoechstens zwoelf neue Intervallaufrufe insgesamt;
- kein Retry und keine Wiederholung.

S1-LJ implementiert keinen Runner und fuehrt weder Replik noch Intervall aus.

Entscheidung:

`B3_PIE_C09_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_RESIDUAL_TWELVE_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`1ea37ea12b9c0bb9fa82bc24410e4a240accfcd628b2611deae93fded20241af`

## Grenzen

Kein C09-Falloutput und keine 24-Fall-Matrix werden publiziert.
Baselineabschluss, Ranking, Kandidatenvergleich, Runtimeintegration und
Forschungsprobe bleiben geschlossen.

## Naechster zulaessiger Schritt

S1-LK darf ausschliesslich die drei gebundenen B3/P_IE-Runner-IDs
implementieren und r2, r4 sowie r8 je einmal innerhalb des
Zwoelf-Intervall-Budgets ausfuehren. Keine andere Rolle, kein anderer
Profilblock, keine Fallkomposition und kein Urteil.
