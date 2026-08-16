# S1-MD: B4/P_IH-C14-Auswahl und Ausfuehrungsvertrag

## Zweck

S1-MD waehlt ausschliesslich den naechsten registrierten Fall `C14` fuer
`B4/P_IH_ATTENUATION` aus und bindet dessen spaeteren Ausfuehrungsrahmen.

Es wird keine Replik, keine Sequenz und kein Intervall ausgefuehrt.

## Gebundene Auswahl

Der ausgewaehlte Fall ist:

```text
C14 / B4 / B4_F3_LINEAR_COUPLED / P_IH_ATTENUATION
```

Gebunden sind:

- drei Refinements `r2/r4/r8`;
- die einzelne Sequenz `P_IH_A_A_A`;
- je ein unabhaengiger korrigierter B4-Frischzustand pro Refinement;
- uniformer M-Zustand mit gebundenem `mcm.s1jt.b4.linear-coupled`-Arm;
- B4-Konfigurationsdigest;
- duale Digestrollen fuer Provenienz und Refinementvergleich;
- hoechstens neun neue Intervallaufrufe ohne Retry.

MCM-Memory bleibt eine Entwicklungsrichtung und Forschungszielsetzung fuer
spaetere MCM-faehige Memory. S1-MD enthaelt keinen Memory-Nachweis und keinen
KI-System-Claim.

Entscheidung:

`B4_PIH_C14_SELECTED_THREE_REFINEMENT_DUAL_DIGEST_NINE_CALL_CONTRACT_BOUND_NO_EXECUTION`

Vertragsdigest:

`026e7ac0e7de28345531585a85ba2062691c649b964baa854504283c2a6b818b`

## Grenzen

S1-MD ist nur Auswahl und Ausfuehrungsvertrag. Gesperrt bleiben:

- Runner-, Initializer-, Adapter- oder Outputimplementierung;
- Replik-, Sequenz-, Intervall-, Retry- oder Wiederholungsausfuehrung;
- C14-Falloutput;
- 24-Fall-Matrixkomposition und Matrixpublikation;
- Baseline- oder Kandidatenentscheidung;
- Runtime-Integration;
- Memory-Nachweis, vorhandene Memory-Faehigkeit oder KI-System-Claim.

## Tests

```text
python -m unittest tests.test_dynamic_substrate_s1md_b4_pih_case_selection_contract \
  tests.test_dynamic_substrate_s1mc_matrix_completeness_gate
```

Ergebnis:

```text
Ran 14 tests in 0.679s
OK
```

## Naechster zulaessiger Schritt

S1-ME darf ausschliesslich die drei gebundenen B4/P_IH-Replikate `r2/r4/r8`
implementieren und isoliert ausfuehren. Keine andere Rolle, keine
Fallkomposition, keine Matrixpublikation und kein Urteil.
