# S1-MB: B4/P_IE-C13-Falloutput

## Ergebnis

S1-MB setzt den technischen Fallrecord C13 fuer den linear gekoppelten B4-Arm
unter `P_IE_CAUSAL_TWO_SUBSTEP` ausschliesslich aus den drei gebundenen
S1-MA-Ausgaben zusammen. Es wird keine Replik und kein Intervall erneut
ausgefuehrt.

Der Record bindet drei voneinander verschiedene Provenienz-Digests, drei
voneinander verschiedene Refinement-Vergleichsdigests, r4 als
Primaerausgabe und die vollstaendigen gerichteten Komponentenreste r2-r4
sowie r4-r8. Alle acht Primaerkomponenten und alle 16 Restkomponenten sind
null. Die Feld-, Privat- und Adapteroutput-Checkpointdigests bleiben ueber
r2, r4 und r8 verschieden; innerhalb eines Refinements sind die beiden
unabhaengig frisch gestarteten Sequenzen bitidentisch.

Dies ist nur ein reproduzierbarer technischer Ausgabebefund. Es ist kein
Baselineabschluss und kein Kandidatenvergleich.

Falloutputdigest:

`d52d86c152466117dbd4f9daae221d0b1c5b2c357394e06c594d98ed80bd711d`

Entscheidung:

`C13_B4_PIE_THREE_REFINEMENT_CASE_OUTPUT_AND_RESIDUALS_BOUND_FROM_S1MA_RECEIPT_NO_NEW_EXECUTION`

Kanonischer Vertragsdigest:

`8e45f668286fdaeda5cd80a95a424dccde3bdc260c576f2b0b9f2d061f48f54e`

## Grenzen

S1-MB fuehrt nichts aus. Die 24-Fall-Matrix, Baseline- und
Kandidatenurteile, Runtimeintegration und weitergehende Claims bleiben
geschlossen.

## Tests

```text
python -m unittest tests.test_dynamic_substrate_s1mb_b4_pie_case_output_contract \
  tests.test_dynamic_substrate_s1ma_b4_pie_three_refinement \
  tests.test_dynamic_substrate_s1ly_matrix_completeness_gate
```

Ergebnis:

```text
Ran 23 tests in 12.684s
OK
```

## Naechster zulaessiger Schritt

S1-MC darf ausschliesslich als Matrixvollstaendigkeitsgate C01 bis C13 als
abgeschlossen binden und den naechsten fehlenden Fall bezeichnen. Keine neue
Replik, keine Matrixpublikation und kein Urteil.
