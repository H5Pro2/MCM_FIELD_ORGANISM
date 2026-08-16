# S1-LM: B3/P_IH-C10-Auswahl und Ausfuehrungsvertrag

S1-LM waehlt als naechsten einzelnen technischen Fall exakt `C10`:
zustandsbehaftete B3-Interferenz/Leaky-gegenlaeufige Baseline unter dem
registrierten Profil `P_IH_ATTENUATION` auf der offenen Zweiknotengeometrie.
Die Auswahl bindet kein erwartetes Vorzeichen und bleibt kein Baseline- oder
Kandidatenurteil.

Gebunden sind die drei registrierten Repliken `r2`, `r4` und `r8`. Jede
Replik startet aus einem eigenen korrigierten B3-Frischzustand. Die einzige
Sequenz `P_IH_A_A_A` trägt das vollstaendige Feld und den vollstaendigen
gebundenen lokalen Leaky-Arm ueber drei geordnete A-Intervalle.
Feld, eingebetteter M-Zustand und Bound-Arm duerfen nur innerhalb der
jeweiligen Sequenz getragen werden.

Jede Ausgabe muss das v2-Schema mit getrenntem Provenienz- und
Vergleichsdigest verwenden. Fuer B3 wird keine Bitidentitaet der
r2/r4/r8-Inhalte vorausgesetzt.

## Endliches Budget

- drei Zielrepliken, je einmal;
- eine Sequenz je Replik;
- drei Intervallaufrufe je Sequenz;
- hoechstens neun neue Intervallaufrufe;
- kein Retry und keine Wiederholung.

Entscheidung:

`B3_PIH_C10_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_NINE_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`6a5217af1426462bcf910bfdb94ae19813b8fdd2de3b1c9db6c77f577506678b`

## Grenzen

S1-LM implementiert keinen Runner und fuehrt weder Replik noch Intervall aus.
Kein C10-Falloutput, keine 24-Fall-Matrix und kein Baseline- oder
Kandidatenurteil.
