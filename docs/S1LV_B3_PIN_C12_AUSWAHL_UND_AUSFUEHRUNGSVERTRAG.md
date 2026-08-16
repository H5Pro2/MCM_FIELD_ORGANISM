# S1-LV: B3/P_IN-C12-Auswahl und Ausfuehrungsvertrag

## Zweck

S1-LV waehlt als naechsten einzelnen technischen Fall exakt:

`C12 / B3 / B3_F3_LOCAL_LEAKY / P_IN_RELEASE_REUSE / r2-r4-r8`

Die Auswahl folgt direkt aus dem S1-LU-Gate. C01 bis C11 sind abgeschlossen,
die 24-Fall-Matrix bleibt unvollstaendig, und C12 ist der einzige naechste
registrierte Fall.

## Gebundener Ausfuehrungsrahmen

Gebunden sind:

- drei Replikate `r2/r4/r8`;
- zwei Sequenzen pro Replikat:
  - `P_IN_RECOVERY_ON`;
  - `P_IN_RECOVERY_OFF`;
- vier Intervallaufrufe pro Sequenz;
- acht Intervallaufrufe pro Replikat;
- maximal 24 neue Intervallaufrufe;
- zwei terminale Checkpoints pro Replikat;
- sechs signed Komponenten pro Replikat;
- acht Adapterdiagnostiken pro Replikat;
- vollstaendiger korrigierter B3-Frischzustand mit Drei-Knoten-Geometrie und
  eingebettetem M-State.

Die beiden Sequenzen starten pro Refinement getrennt aus bitidentischem
Frischfeld und vollstaendigem B3-M-State. Carry ist nur innerhalb der vier
geordneten Intervalle einer Sequenz zulaessig. Zwischen Sequenzen und
Refinements gibt es keinen Feld-, M-State-, Output- oder Provenienzcarry.

Entscheidung:

`B3_PIN_C12_SELECTED_THREE_REFINEMENT_TWO_SEQUENCE_DUAL_DIGEST_TWENTY_FOUR_CALL_CONTRACT_BOUND_NO_EXECUTION`

Vertragsdigest:

`bc11f71be2ab76f19f14b9846061895059db5dd926cb020d8aae3be84773da44`

## Grenzen

S1-LV implementiert keinen Runner und fuehrt nichts aus.

Gesperrt bleiben:

- Replik-, Sequenz- oder Intervallausfuehrung;
- C12-Falloutput;
- Matrixkomposition und Matrixpublikation;
- Release-/Reuse-, Baseline- oder Kandidatenurteil;
- Runtime-Integration;
- Memory-, KI- oder weitergehende Projektclaims.

## Tests

```text
python -m unittest tests.test_dynamic_substrate_s1lv_b3_pin_case_selection_contract \
  tests.test_dynamic_substrate_s1lu_matrix_completeness_gate
```

Ergebnis:

```text
Ran 11 tests in 0.111s
OK
```

## Naechster zulaessiger Schritt

S1-LW darf ausschliesslich die drei gebundenen B3/P_IN-C12-Replikate
`r2/r4/r8` im privaten Orchestrator implementieren und ausfuehren. Kein
C12-Falloutput, keine Matrixkomposition und kein Urteil.
