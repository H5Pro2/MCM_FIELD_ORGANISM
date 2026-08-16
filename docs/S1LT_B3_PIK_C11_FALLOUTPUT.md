# S1-LT: B3/P_IK-C11-Falloutput

## Zweck

S1-LT setzt den technischen Fallrecord `C11` fuer `B3/P_IK_INTERFERENCE`
ausschliesslich aus den bereits gebundenen S1-LS-Ausgaben zusammen.

Es wird keine Replik, keine Sequenz und kein Intervall neu ausgefuehrt.

## Gebundener Output

Der Fallrecord enthaelt:

- drei Replikate `r2/r4/r8`;
- drei Provenienz-Digests;
- drei Refinement-Vergleichsdigests;
- sechs technische signed Komponenten pro Refinement;
- `r4` als Primaerrefinement;
- zwei gerichtete Residualbloecke `r2_minus_r4` und `r4_minus_r8`;
- vollstaendige terminale Feld-, Privat- und Adapteroutput-Digestmatrizen.

Entscheidung:

`C11_B3_PIK_THREE_REFINEMENT_CASE_OUTPUT_AND_RESIDUALS_BOUND_FROM_S1LS_RECEIPT_NO_NEW_EXECUTION`

Case-Output-Digest:

`a759720fd1fda3d159493a83dd20fdc802a92c9290af732d06323656749f52c3`

Vertragsdigest:

`575c0a90935383b6ebda1825400d3fe744a76818162a3b444a733ee0dd4c68df`

## Grenzen

S1-LT ist kein Baselineurteil und kein Kandidatenvergleich. Die nichtnulligen
Komponenten und die schrumpfenden Residuals sind nur technische
Falloutputdaten des B3/P_IK-Arms.

Weiterhin gesperrt bleiben:

- 24-Fall-Matrixkomposition;
- Matrixpublikation;
- Baseline- oder Kandidatenentscheidung;
- Runtime-Integration;
- Memory-, KI- oder weitergehende Projektclaims.

## Tests

```text
python -m unittest tests.test_dynamic_substrate_s1lt_b3_pik_case_output_contract \
  tests.test_dynamic_substrate_s1ls_b3_pik_three_refinement \
  tests.test_dynamic_substrate_s1lr_b3_pik_case_selection_contract
```

Ergebnis:

```text
Ran 23 tests in 11.313s
OK
```

## Naechster zulaessiger Schritt

S1-LU darf ausschliesslich als Matrixvollstaendigkeitsgate C01 bis C11 als
abgeschlossen binden und den naechsten fehlenden Fall bezeichnen. Keine neue
Replik, keine Matrixpublikation und kein Urteil.
