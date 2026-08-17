# S1-MP: B5/P_IE-C17-Auswahl und Ausfuehrungsvertrag

## Zweck

S1-MP bindet ausschliesslich die statische Auswahl des naechsten
Matrixfalls C17:

```text
C17 / B5 / B5_F3_FULL / P_IE_CAUSAL_TWO_SUBSTEP
```

Es wird kein Runner erweitert, keine Replik ausgefuehrt und kein Intervall
materialisiert.

## Gebundene Auswahl

- Replikate: `B5:P_IE_CAUSAL_TWO_SUBSTEP:r2`, `r4`, `r8`.
- Sequenzen: `P_IE_F_HIGH` und `P_IE_R_HIGH`.
- Frischzustand: korrigierter B5-Zweiknoten-Frischzustand
  `TWO_NODE_OPEN_LINE`.
- Modellrolle: `B5_F3_FULL`.
- Komponenten pro Replikat: `8`.
- Terminale Checkpoints pro Replikat: `4`.
- Adapterdiagnostiken pro Replikat: `4`.
- Maximales neues Ausfuehrungsbudget fuer den naechsten Schritt:
  `12` Intervallaufrufe.
- Retry-/Repeat-Aufrufe: `0`.

Die zwei P_IE-Sequenzen starten pro Refinement aus getrennten B5-
Frischzustaenden. M-Zustand und volle B5-Konfiguration duerfen nur innerhalb
einer Sequenz ueber die zwei geordneten Intervalle getragen werden. Zwischen
Sequenzen und Refinements gibt es keinen Feld-, M-Zustands-, Output- oder
Provenienzcarry.

## Entscheidung

`B5_PIE_C17_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_RESIDUAL_TWELVE_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`8dad9e91bd0d5c334978b13a71422990da5d6348f5c151d5098d8c66c6658f81`

## Grenzen

S1-MP ist nur Auswahl und Ausfuehrungsvertrag. Gesperrt bleiben:

- Runner-, Initializer-, Adapter- oder Output-Implementierung;
- Replik-, Sequenz- oder Intervallausfuehrung;
- C17-Falloutput;
- 24-Fall-Matrixkomposition und Matrixpublikation;
- Baselineurteil, Kandidatenvergleich und Runtime-Integration;
- Memory-Nachweis, vorhandene Memory-Faehigkeit oder KI-System-Claim.

MCM-Memory bleibt ausschliesslich Entwicklungsrichtung fuer spaetere
MCM-faehige Memory.

## Tests

```text
python -m unittest tests.test_dynamic_substrate_s1mp_b5_pie_case_selection_contract \
  tests.test_dynamic_substrate_s1mo_matrix_completeness_gate \
  tests.test_dynamic_substrate_s1mn_b4_pin_case_output_contract
```

Ergebnis:

```text
Ran 22 tests in 24.147s
OK
```

## Naechster zulaessiger Schritt

S1-MQ darf ausschliesslich die drei gebundenen C17-Replikate `r2/r4/r8`
implementieren und isoliert ausfuehren. Kein C17-Falloutput, keine
Matrixpublikation und kein Urteil.
