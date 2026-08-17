# S1-MT: B5/P_IH-C18-Auswahl und Ausfuehrungsvertrag

## Zweck

S1-MT bindet ausschliesslich die statische Auswahl des naechsten
Matrixfalls C18:

```text
C18 / B5 / B5_F3_FULL / P_IH_ATTENUATION
```

Es wird kein Runner erweitert, keine Replik ausgefuehrt und kein Intervall
materialisiert.

## Gebundene Auswahl

- Replikate: `B5:P_IH_ATTENUATION:r2`, `r4`, `r8`.
- Sequenz: `P_IH_A_A_A`.
- Frischzustand: korrigierter B5-Zweiknoten-Frischzustand
  `TWO_NODE_OPEN_LINE`.
- Modellrolle: `B5_F3_FULL`.
- Komponenten pro Replikat: `8`.
- Terminale Checkpoints pro Replikat: `3`.
- Adapterdiagnostiken pro Replikat: `3`.
- Maximales neues Ausfuehrungsbudget fuer den naechsten Schritt:
  `9` Intervallaufrufe.
- Retry-/Repeat-Aufrufe: `0`.

Die P_IH-Sequenz startet pro Refinement aus einem eigenen B5-Frischzustand.
M-Zustand und volle B5-Konfiguration duerfen nur innerhalb der drei geordneten
Intervalle getragen werden. Zwischen Refinements gibt es keinen Feld-,
M-Zustands-, Output- oder Provenienzcarry.

## Entscheidung

`B5_PIH_C18_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_NINE_CALL_CONTRACT_BOUND_NO_EXECUTION`

Kanonischer Vertragsdigest:

`3bce6b64a720467e5dfbcb9695bc3c8f0e79fded4214e62ef7f737b6bba5ca67`

## Grenzen

S1-MT ist nur Auswahl und Ausfuehrungsvertrag. Gesperrt bleiben:

- Runner-, Initializer-, Adapter- oder Output-Implementierung;
- Replik-, Sequenz- oder Intervallausfuehrung;
- C18-Falloutput;
- 24-Fall-Matrixkomposition und Matrixpublikation;
- Baselineurteil, Kandidatenvergleich und Runtime-Integration;
- Memory-Nachweis, vorhandene Memory-Faehigkeit oder KI-System-Claim.

MCM-Memory bleibt ausschliesslich Entwicklungsrichtung fuer spaetere
MCM-faehige Memory.

## Tests

```text
python -m unittest tests.test_dynamic_substrate_s1mt_b5_pih_case_selection_contract \
  tests.test_dynamic_substrate_s1ms_matrix_completeness_gate \
  tests.test_dynamic_substrate_s1mr_b5_pie_case_output_contract
```

Ergebnis:

```text
Ran 22 tests in 71.980s
OK
```

## Naechster zulaessiger Schritt

S1-MU darf ausschliesslich die drei gebundenen C18-Replikate `r2/r4/r8`
implementieren und isoliert ausfuehren. Kein C18-Falloutput, keine
Matrixpublikation und kein Urteil.
