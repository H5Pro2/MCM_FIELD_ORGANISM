# S1-MH: B4/P_IK-C15-Auswahl und Ausfuehrungsvertrag

## Zweck

S1-MH bindet ausschliesslich die statische Auswahl des naechsten
Matrixfalls C15:

```text
C15 / B4 / B4_F3_LINEAR_COUPLED / P_IK_INTERFERENCE
```

Es wird kein Runner erweitert, keine Replik ausgefuehrt und kein Intervall
materialisiert.

## Gebundene Auswahl

- Replikate: `B4:P_IK_INTERFERENCE:r2`, `r4`, `r8`.
- Sequenzen: `P_IK_A_B_A` und `P_IK_A_GAP_A`.
- Frischzustand: korrigierter B4-Dreiknoten-Frischzustand
  `THREE_NODE_OPEN_LINE`.
- Modellrolle: `B4_F3_LINEAR_COUPLED`.
- Komponenten pro Replikat: `6`.
- Terminale Checkpoints pro Replikat: `2`.
- Adapterdiagnostiken pro Replikat: `8`.
- Maximales neues Ausfuehrungsbudget fuer den naechsten Schritt:
  `24` Intervallaufrufe.
- Retry-/Repeat-Aufrufe: `0`.

Die zwei P_IK-Sequenzen starten pro Refinement aus getrennten, bitidentischen
B4-Frischzustaenden. M-Zustand und linear gekoppelte B4-Konfiguration duerfen
nur innerhalb einer Sequenz ueber die vier geordneten Intervalle getragen
werden. Zwischen Sequenzen und Refinements gibt es keinen Feld-, M-Zustands-,
Output- oder Provenienzcarry.

## Entscheidung

`B4_PIK_C15_SELECTED_THREE_REFINEMENT_TWO_SEQUENCE_DUAL_DIGEST_TWENTY_FOUR_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`8cbd097973cf50276f27e72c00674eab70b9171b86834604b8151b7a705e38d0`

## Grenzen

S1-MH ist nur Auswahl und Ausfuehrungsvertrag. Gesperrt bleiben:

- Runner-, Initializer-, Adapter- oder Output-Implementierung;
- Replik-, Sequenz- oder Intervallausfuehrung;
- C15-Falloutput;
- 24-Fall-Matrixkomposition und Matrixpublikation;
- Baselineurteil, Kandidatenvergleich und Runtime-Integration;
- Memory-Nachweis, vorhandene Memory-Faehigkeit oder KI-System-Claim.

MCM-Memory bleibt ausschliesslich Entwicklungsrichtung fuer spaetere
MCM-faehige Memory.

## Tests

```text
python -m unittest tests.test_dynamic_substrate_s1mh_b4_pik_case_selection_contract \
  tests.test_dynamic_substrate_s1mg_matrix_completeness_gate \
  tests.test_dynamic_substrate_s1mf_b4_pih_case_output_contract
```

Ergebnis:

```text
Ran 21 tests in 2.218s
OK
```

## Naechster zulaessiger Schritt

S1-MI darf ausschliesslich die drei gebundenen C15-Replikate `r2/r4/r8`
implementieren und isoliert ausfuehren. Kein C15-Falloutput, keine
Matrixpublikation und kein Urteil.
