# S1-EC9: Kleine reale Fuenf-Arm-Formation

## Status

```text
SMALL_REAL_FIVE_ARM_CONTROLS_ACCEPTED
DETERMINISTIC_ON_FRESH_COPIES
NO_CANONICAL_EXECUTION
```

S1-EC9 komponiert auf derselben kleinen Zwei-Dock-In-Memory-Fixture alle
fuenf realen Formationsarme einer Refinementstufe. Jeder Arm laeuft ueber den
kopienisolierten S1-EC8-Kern.

## Implementierung

```text
mcm_field_organism/e1_confirmation_small_five_arm_formation.py
tests/test_e1_confirmation_small_five_arm_formation.py
```

## Armfolge

```text
ab
ba
ab_identity
ab_formation_ablated
ba_formation_ablated
```

## Bestaetigte Kontrollen

- `ab` und `ab_identity` liefern denselben E1-Ausgangszustand;
- beide Ablationsarme bleiben neutral;
- alle fuenf Ausgangszustaende sind objektgetrennt;
- bei ausgeschalteter History-Rueckwirkung besitzen `ab`, `ab_identity` und
  `ab_formation_ablated` denselben Felddigest;
- `ba` und `ba_formation_ablated` besitzen denselben Felddigest;
- der maximale Ressourcenbudgetfehler bleibt kleiner oder gleich `1e-12`;
- Anfangsfeld und Anfangszustand bleiben digestidentisch;
- Wiederholung auf frischen Kopien liefert denselben Kompositdigest.

## Verifikation

```text
.venv/Scripts/python.exe -m pytest -q \
  tests/test_e1_confirmation_prepared_execution_bundle.py \
  tests/test_e1_confirmation_typed_prepared_inputs.py \
  tests/test_e1_confirmation_research_corridor.py \
  tests/test_e1_confirmation_descriptor_refinement_planner.py \
  tests/test_e1_confirmation_descriptor_input_resolver.py \
  tests/test_e1_confirmation_run_contract_bundle.py \
  tests/test_e1_confirmation_prepared_formation_consumer.py \
  tests/test_e1_confirmation_prepared_real_formation_kernel.py \
  tests/test_e1_confirmation_small_five_arm_formation.py

43 passed
```

Die bekannte Warnung betrifft nur `.pytest_cache`.

## Evidenzgrenze

Die Abnahme verwendet eine kleine Fixture und nur die Kennzeichnung `r2`;
sie ist keine r2/r4/r8-Verfeinerungsuntersuchung. Sie bestaetigt die reale
Fuenf-Arm-Komposition und ihre technischen Kontrollen, aber weder den
kanonischen Effekt noch MCM-Memory.

## Bester naechster Schritt

S1-EC10 sollte auf derselben kleinen Fixture echte `r2`, `r4` und
`r8`-Schrittfolgen aus identischen Completion-Grenzen bilden und fuer jede
Stufe die fuenf Arme ausfuehren. Zu pruefen sind die bestehende Kontrollmatrix,
Eingabeisolierung und die numerischen r2-r4-/r4-r8-Reste. Noch keine volle
kanonische Formation.
