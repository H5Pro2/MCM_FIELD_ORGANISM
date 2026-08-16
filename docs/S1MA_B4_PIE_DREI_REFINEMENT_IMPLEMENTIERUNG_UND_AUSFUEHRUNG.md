# S1-MA: B4/P_IE-Drei-Refinement-Implementierung und Ausfuehrung

## Ergebnis

S1-MA erweitert den privaten Ein-Replik-Runner exakt um die drei in S1-LZ
gebundenen B4/P_IE-IDs r2, r4 und r8. Die Frischzustandsrekonstruktion bildet
den vollstaendigen M-Zustand, den gebundenen Linear-Coupled-Arm und den
B4-Konfigurationsdigest ab.

Jede Replik wurde genau einmal ausgefuehrt. Pro Replik starteten
`P_IE_F_HIGH` und `P_IE_R_HIGH` unabhaengig aus dem registrierten
B4-Zweiknoten-Frischzustand. Insgesamt wurden zwoelf Intervalle
materialisiert und durch den vorhandenen B4-Adapter verarbeitet.

## Technische Ausgaben

Vollstaendige Provenienz-Digests:

- r2: `acd835e0f0aa36a06eff777d2af545545c8b3f0787d4c20a63f90f597271f15c`
- r4: `49d91cc38bb266eae80c28810d1255ebeab05e717d313a050966af9bc331c918`
- r8: `74ac9549d3796e720064c372bb96341081236cacee2729d9a6ce0cf5362f9fbc`

Refinement-Vergleichsdigests:

- r2: `e765f9ee9ca2046672e71e97fd0c1c433048f1cb4e7e6db5695e9ce8b4b65587`
- r4: `2a1581ba2f1b0910d311498f530c1a7a40477c20b02144ad7ce62b7b3611dbbf`
- r8: `83fb33939461378ae06fb08ccffcb7c5f02963a148f5cc830081513be998f477`

Alle acht signed F-High-minus-R-High-Komponenten sind in r2, r4 und r8 null.
Innerhalb eines Refinements besitzen die beiden unabhaengigen Sequenzen
bitidentische Checkpointdigestpaare. Die vollstaendigen Inhalte und Digests
unterscheiden sich zwischen r2, r4 und r8. Das wird nicht als Baseline- oder
Kandidatenurteil gewertet.

Entscheidung:

`B4_PIE_R2_R4_R8_IMPLEMENTED_TWELVE_INTERVALS_DISTINCT_REFINEMENT_OUTPUTS_ACCEPTED_FROM_S1LZ_SELECTION`

Receipt-Digest:

`24e4fe8c8641b0df2e4d0c3e167883eaa51643a69ea2563d108e0a024220f6a3`

## Grenzen

C13 wurde noch nicht als Falloutput zusammengesetzt. Weitere Rollen und
Profile, die 24-Fall-Matrix, Baseline- und Kandidatenurteile,
Runtimeintegration sowie Forschungslaeufe bleiben geschlossen.

## Tests

```text
python -m unittest tests.test_dynamic_substrate_s1ma_b4_pie_three_refinement \
  tests.test_dynamic_substrate_s1lz_b4_pie_case_selection_contract \
  tests.test_dynamic_substrate_s1lk_b3_pie_three_refinement
```

Ergebnis:

```text
Ran 26 tests in 24.814s
OK
```

## Naechster zulaessiger Schritt

S1-MB darf ausschliesslich den technischen C13-Fallrecord aus den drei
bereits gebundenen S1-MA-Ausgaben zusammensetzen und die vorregistrierten
r2-r4- sowie r4-r8-Komponentenreste berechnen. Keine neue Replik und kein
neues Intervall.
