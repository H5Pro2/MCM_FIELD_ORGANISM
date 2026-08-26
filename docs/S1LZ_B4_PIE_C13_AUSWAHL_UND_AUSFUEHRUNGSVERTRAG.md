# S1-LZ: B4/P_IE-C13-Auswahl und Ausfuehrungsvertrag

## Zweck

S1-LZ waehlt ausschliesslich den naechsten registrierten Fall `C13` fuer
`B4/P_IE_CAUSAL_TWO_SUBSTEP` aus und bindet dessen spaeteren
Ausfuehrungsrahmen.

Es wird keine Replik, keine Sequenz und kein Intervall ausgefuehrt.

## Gebundene Auswahl

Der ausgewaehlte Fall ist:

```text
C13 / B4 / B4_F3_LINEAR_COUPLED / P_IE_CAUSAL_TWO_SUBSTEP
```

Gebunden sind:

- drei Refinements `r2/r4/r8`;
- zwei getrennte Sequenzen `P_IE_F_HIGH` und `P_IE_R_HIGH`;
- je ein unabhaengiger korrigierter B4-Frischzustand pro Sequenz;
- uniformer M-Zustand mit gebundenem `mcm.s1jt.b4.linear-coupled`-Arm;
- B4-Konfigurationsdigest;
- duale Digestrollen fuer Provenienz und Refinementvergleich;
- spaetere vollstaendige `r2_minus_r4`- und `r4_minus_r8`-Residualausgabe;
- hoechstens zwoelf neue Intervallaufrufe ohne Retry.

Entscheidung:

`B4_PIE_C13_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_RESIDUAL_TWELVE_CALL_CONTRACT_BOUND_NO_EXECUTION`

Vertragsdigest:

`2e4f4e81b9bb701c0aa74e34eb56e73032e85689a91fb858ea0a37aaa5bdc8d1`

## Grenzen

S1-LZ ist nur Auswahl und Ausfuehrungsvertrag. Gesperrt bleiben:

- Runner-, Initializer-, Adapter- oder Outputimplementierung;
- Replik-, Sequenz-, Intervall-, Retry- oder Wiederholungsausfuehrung;
- C13-Falloutput;
- 24-Fall-Matrixkomposition und Matrixpublikation;
- Baseline- oder Kandidatenentscheidung;
- Runtime-Integration;
- Memory-, KI- oder weitergehende Projektclaims.

## Tests

```text
python -m unittest tests.test_dynamic_substrate_s1lz_b4_pie_case_selection_contract \
  tests.test_dynamic_substrate_s1ly_matrix_completeness_gate
```

Ergebnis:

```text
Ran 13 tests in 0.345s
OK
```

## Naechster zulaessiger Schritt

S1-MA darf ausschliesslich die drei gebundenen B4/P_IE-Replikate `r2/r4/r8`
implementieren und isoliert ausfuehren. Keine andere Rolle, keine
Fallkomposition, keine Matrixpublikation und kein Urteil.
