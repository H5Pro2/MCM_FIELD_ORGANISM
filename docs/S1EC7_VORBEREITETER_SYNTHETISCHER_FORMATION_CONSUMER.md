# S1-EC7: Vorbereiteter synthetischer Formation-Consumer

## Status

```text
PREPARED_FORMATION_HANDOFF_SYNTHETICALLY_ACCEPTED
NO_INPUT_RECONSTRUCTION_AFTER_ATTEMPT
NO_FIELD_EXECUTION
```

S1-EC7 bindet den ersten nach dem Attempt liegenden Verarbeitungsschritt an
das vorbereitete S1-EC6-Bundle. Der Consumer liest ausschliesslich bereits
gebundene Objekte und besitzt keinen Eingabe-, Plan-, Feld- oder
Zustandsbuilder.

## Implementierung

```text
mcm_field_organism/e1_confirmation_prepared_formation_consumer.py
tests/test_e1_confirmation_prepared_formation_consumer.py
```

## Gebundene Formationsordnung

Fuer jede Refinementstufe `r2`, `r4` und `r8` werden in fester Reihenfolge
fuenf synthetische Kerne aufgerufen:

```text
ab
ba
ab_identity
ab_formation_ablated
ba_formation_ablated
```

Das ergibt 15 Aufrufe. Jeder Kern erhaelt direkt:

- die bereits gebundene AB- oder BA-Sequenz;
- die bereits gebundenen Vorschlagsschritte des passenden Plans;
- dasselbe vorbereitete Anfangsfeld;
- denselben vorbereiteten neutralen E1-Anfangszustand;
- das feste Formation-enabled/Ablation-Flag.

Die Kerne liefern nur SHA-256-Digests. S1-EC7 fuehrt selbst keine
Feldoperation aus.

## Abnahme

- alle 15 Aufrufe erfolgen in der festgelegten Ordnung;
- der Consumer wird innerhalb des S1-EC1-Executors nach vorhandenem Attempt
  ausgefuehrt;
- Quellen, Schritte, Anfangsfeld und Zustand sind dieselben Objektinstanzen
  wie im Bundle;
- der Consumer rekonstruiert keine Eingabe;
- ein ungueltiges Kernelresultat behaelt den Attempt, entfernt den Lock und
  blockiert einen zweiten Start;
- terminale S1-EB31-Artefakte bleiben unveraendert.

## Verifikation

```text
.venv/Scripts/python.exe -m pytest -q \
  tests/test_e1_confirmation_prepared_execution_bundle.py \
  tests/test_e1_confirmation_typed_prepared_inputs.py \
  tests/test_e1_confirmation_research_corridor.py \
  tests/test_e1_confirmation_descriptor_refinement_planner.py \
  tests/test_e1_confirmation_descriptor_input_resolver.py \
  tests/test_e1_confirmation_run_contract_bundle.py \
  tests/test_e1_confirmation_prepared_formation_consumer.py

35 passed
```

Die bekannte Warnung betrifft nur `.pytest_cache`.

## Evidenzgrenze

Die 15 Kerne sind Digest-Substitute. Es wurden keine MCM-Feldwerte und keine
E1-Bindungen fortgeschrieben. Der Befund betrifft nur die kontrollierte
Objekt- und Lebenszyklusweitergabe, nicht E1 oder MCM-Memory.

## Bester naechster Schritt

S1-EC8 sollte den vorhandenen realen Formationskern hinter dieselbe
S1-EC7-Schnittstelle setzen, zunaechst jedoch nur in einer kleinen
substituierten In-Memory-Abnahme. Dabei muessen Eingangsdigests vor und nach
der Verarbeitung unveraendert bleiben und die fuenf Ergebnisarme pro
Refinement objektgetrennt sein. Noch kein kanonischer Einmallauf.
