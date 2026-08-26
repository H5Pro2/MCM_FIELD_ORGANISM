# S1-ML: B4/P_IN-C16-Auswahl und Ausfuehrungsvertrag

## Zweck

S1-ML bindet ausschliesslich die statische Auswahl des naechsten
Matrixfalls C16:

```text
C16 / B4 / B4_F3_LINEAR_COUPLED / P_IN_RELEASE_REUSE
```

Es wird kein Runner erweitert, keine Replik ausgefuehrt und kein Intervall
materialisiert.

## Gebundene Auswahl

- Replikate: `B4:P_IN_RELEASE_REUSE:r2`, `r4`, `r8`.
- Sequenzen: `P_IN_RECOVERY_ON` und `P_IN_RECOVERY_OFF`.
- Frischzustand: korrigierter B4-Dreiknoten-Frischzustand
  `THREE_NODE_OPEN_LINE`.
- Modellrolle: `B4_F3_LINEAR_COUPLED`.
- Komponenten pro Replikat: `6`.
- Terminale Checkpoints pro Replikat: `2`.
- Adapterdiagnostiken pro Replikat: `8`.
- Maximales neues Ausfuehrungsbudget fuer den naechsten Schritt:
  `24` Intervallaufrufe.
- Retry-/Repeat-Aufrufe: `0`.

Die zwei P_IN-Sequenzen starten pro Refinement aus getrennten, bitidentischen
B4-Frischzustaenden. M-Zustand und linear gekoppelte B4-Konfiguration duerfen
nur innerhalb einer Sequenz ueber die vier geordneten Intervalle getragen
werden. Zwischen Sequenzen und Refinements gibt es keinen Feld-, M-Zustands-,
Output- oder Provenienzcarry.

## Entscheidung

`B4_PIN_C16_SELECTED_THREE_REFINEMENT_TWO_SEQUENCE_DUAL_DIGEST_TWENTY_FOUR_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`a1a021f4da45995a15649e962668cad3c195723ce79b1857116c511c272a9b32`

## Grenzen

S1-ML ist nur Auswahl und Ausfuehrungsvertrag. Gesperrt bleiben:

- Runner-, Initializer-, Adapter- oder Output-Implementierung;
- Replik-, Sequenz- oder Intervallausfuehrung;
- C16-Falloutput;
- 24-Fall-Matrixkomposition und Matrixpublikation;
- Release-/Reuse-Urteil, Baselineurteil, Kandidatenvergleich und Runtime-Integration;
- Memory-Nachweis, vorhandene Memory-Faehigkeit oder KI-System-Claim.

MCM-Memory bleibt ausschliesslich Entwicklungsrichtung fuer spaetere
MCM-faehige Memory.

## Tests

```text
python -m unittest tests.test_dynamic_substrate_s1ml_b4_pin_case_selection_contract \
  tests.test_dynamic_substrate_s1mk_matrix_completeness_gate \
  tests.test_dynamic_substrate_s1mj_b4_pik_case_output_contract
```

Ergebnis:

```text
Ran 20 tests in 8.859s
OK
```

## Naechster zulaessiger Schritt

S1-MM darf ausschliesslich die drei gebundenen C16-Replikate `r2/r4/r8`
implementieren und isoliert ausfuehren. Kein C16-Falloutput, keine
Matrixpublikation und kein Urteil.
