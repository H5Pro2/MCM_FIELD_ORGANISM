# S1-LW: B3/P_IN-C12 Drei-Refinement-Implementierung und Ausfuehrung

## Zweck

S1-LW erweitert den privaten Orchestrator exakt um den in S1-LV gebundenen
Fall `C12 / B3 / B3_F3_LOCAL_LEAKY / P_IN_RELEASE_REUSE`.

Ausgefuehrt wurden nur die drei registrierten Replikate:

- `B3:P_IN_RELEASE_REUSE:r2`
- `B3:P_IN_RELEASE_REUSE:r4`
- `B3:P_IN_RELEASE_REUSE:r8`

Jedes Refinement fuehrt zwei getrennte Sequenzen aus:

- `P_IN_RECOVERY_ON`
- `P_IN_RECOVERY_OFF`

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

Die terminalen Recovery-on/off-Digests sind innerhalb jedes Refinements
bitidentisch. Alle sechs signed Komponenten sind null. Das ist nur ein
technischer B3/P_IN-Output und kein Release-/Reuse- oder Baselineurteil.

Entscheidung:

`B3_PIN_R2_R4_R8_IMPLEMENTED_TWENTY_FOUR_INTERVALS_DISTINCT_REFINEMENT_OUTPUTS_ACCEPTED_FROM_S1LV_SELECTION`

Receipt-Digest:

`9e608a0e25e3ba3b9de18f5de8009544d372aa5517ed46e8d194da73fc87c4b4`

## Grenzen

S1-LW ist nur eine technische C12-Ausfuehrung des registrierten B3-Baselinearms.

Nicht enthalten sind:

- kein C12-Caseoutput;
- keine 24-Fall-Matrix;
- keine Matrixpublikation;
- kein Kandidatenvergleich;
- kein Baseline- oder Release-/Reuse-Urteil;
- keine Runtime-Integration;
- keine Memory-, KI- oder weitergehende Projektclaims.

## Tests

```text
python -m unittest tests.test_dynamic_substrate_s1lw_b3_pin_three_refinement \
  tests.test_dynamic_substrate_s1lv_b3_pin_case_selection_contract \
  tests.test_dynamic_substrate_s1ls_b3_pik_three_refinement \
  tests.test_dynamic_substrate_s1lt_b3_pik_case_output_contract
```

Ergebnis:

```text
Ran 32 tests in 24.362s
OK
```

## Naechster zulaessiger Schritt

S1-LX darf ausschliesslich den technischen C12-Falloutput aus den bereits
gebundenen S1-LW-Ausgaben zusammensetzen. Keine neue Replik, kein neuer
Intervallaufruf, keine Matrixkomposition und kein Urteil.
