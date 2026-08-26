# S1-LS: B3/P_IK-C11 Drei-Refinement-Implementierung und Ausfuehrung

## Zweck

S1-LS erweitert den privaten Orchestrator exakt um den in S1-LR gebundenen
Fall `C11 / B3 / B3_F3_LOCAL_LEAKY / P_IK_INTERFERENCE`.

Ausgefuehrt wurden nur die drei registrierten Replikate:

- `B3:P_IK_INTERFERENCE:r2`
- `B3:P_IK_INTERFERENCE:r4`
- `B3:P_IK_INTERFERENCE:r8`

Jedes Refinement fuehrt zwei getrennte Sequenzen aus:

- `P_IK_A_B_A`
- `P_IK_A_GAP_A`

Beide Sequenzen starten pro Refinement aus einem eigenen vollstaendigen
B3-Frischzustand. Carry ist nur innerhalb der je vier geordneten Intervalle
einer Sequenz zulaessig. Zwischen Sequenzen und Refinements gibt es keinen
Feld-, M-State-, Output- oder Provenienzcarry.

## Technische Ausfuehrung

Gebunden sind:

- 3 Replikate;
- 2 Sequenzen pro Replikat;
- 4 Intervallaufrufe pro Sequenz;
- 8 Intervallaufrufe pro Replikat;
- 24 neue Intervallaufrufe insgesamt;
- 2 terminale Checkpoints pro Replikat;
- 6 signed Komponenten pro Replikat;
- 8 Adapterdiagnostiken pro Replikat.

Entscheidung:

`B3_PIK_R2_R4_R8_IMPLEMENTED_TWENTY_FOUR_INTERVALS_DISTINCT_REFINEMENT_OUTPUTS_ACCEPTED_FROM_S1LR_SELECTION`

Receipt-Digest:

`9793383c0ef474336f4b9ce79e2513fea1d32c1a89260de018a3b29240e0ebcb`

## Grenzen

S1-LS ist nur eine technische C11-Ausfuehrung des registrierten B3-Baselinearms.

Nicht enthalten sind:

- kein C11-Caseoutput;
- keine 24-Fall-Matrix;
- keine Matrixpublikation;
- kein Kandidatenvergleich;
- kein Baselineurteil;
- keine Runtime-Integration;
- keine Memory-, KI- oder weitergehende Projektclaims.

Die sechs nichtnulligen P_IK-Komponenten sind ein gebundener technischer
Output des B3/P_IK-Arms. Sie duerfen erst in einem separaten Falloutput und
spaeter in einer vollstaendigen Matrix gegen andere Faelle eingeordnet werden.

## Tests

Fokussierte Abnahme:

```text
python -m unittest tests.test_dynamic_substrate_s1ls_b3_pik_three_refinement \
  tests.test_dynamic_substrate_s1lr_b3_pik_case_selection_contract \
  tests.test_dynamic_substrate_s1lq_matrix_completeness_gate \
  tests.test_dynamic_substrate_s1lo_b3_pih_three_refinement \
  tests.test_dynamic_substrate_s1lp_b3_pih_case_output_contract
```

Ergebnis:

```text
Ran 35 tests in 16.661s
OK
```

## Naechster zulaessiger Schritt

S1-LT darf ausschliesslich den technischen C11-Falloutput aus den bereits
gebundenen S1-LS-Ausgaben zusammensetzen. Keine neue Replik, kein neuer
Intervallaufruf, keine Matrixkomposition und kein Urteil.
