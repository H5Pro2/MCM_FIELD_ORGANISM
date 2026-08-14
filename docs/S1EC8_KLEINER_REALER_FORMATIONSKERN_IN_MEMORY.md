# S1-EC8: Kleiner realer Formationskern in-memory

## Status

```text
REAL_FORMATION_ARM_CORE_ACCEPTED_ON_MINIMAL_FIXTURE
PREPARED_INPUTS_PRESERVED
NO_CANONICAL_EXECUTION
```

S1-EC8 setzt den vorhandenen realen `_run_arm`-Kern hinter eine
S1-EC7-kompatible Kerneloberflaeche. Die Abnahme verwendet ausschliesslich
eine minimale In-Memory-Geometrie mit zwei Docks und zwei completion-aligned
Zeitschritten.

## Implementierung

```text
mcm_field_organism/e1_confirmation_prepared_real_formation_kernel.py
tests/test_e1_confirmation_prepared_real_formation_kernel.py
```

## Schutzmechanik

Vor jedem Arm werden die Digests des vorbereiteten Anfangsfelds und des
neutralen E1-Anfangszustands bestimmt. Der Adapter erstellt tiefe Kopien und
uebergibt ausschliesslich diese Kopien an `_run_arm(...)`. Nach dem Lauf
werden die Digests der Originale erneut geprueft.

Das Ergebnis bindet:

- Arm- und Refinementidentitaet;
- Formation-enabled/Ablation;
- beide Eingangsdigests;
- den resultierenden E1-Zustand und seinen Digest;
- das bestehende Formationsaudit;
- bestaetigte Eingangserhaltung und Kopienverwendung;
- geschlossene kanonische Ausfuehrung und Claims.

`prepared_real_formation_kernel_digest(...)` stellt denselben realen Kern als
Digest-Kernel fuer die S1-EC7-Schnittstelle bereit.

## Abnahmebefund

- Der aktive kleine `ab/r2`-Arm veraendert den kopierten E1-Zustand.
- Der ablatierte kleine Arm bleibt neutral.
- Ausgabenzustaende sind von den vorbereiteten Zustaenden objektgetrennt.
- Anfangsfeld und Anfangszustand bleiben digestidentisch.
- Wiederholung auf frischen Kopien liefert denselben Ergebnisdigest.
- Der Adapter besitzt keinen Builder- oder Persistenzpfad.

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
  tests/test_e1_confirmation_prepared_real_formation_kernel.py

39 passed
```

Die bekannte Warnung betrifft nur `.pytest_cache`.

## Evidenzgrenze

Dies ist erstmals eine reale Feldkern-Ausfuehrung in der korrigierten Linie,
aber nur auf einer minimalen technischen Testfixture. Sie prueft
Kernanschluss, Kopienisolierung und Determinismus. Sie bestaetigt weder die
kanonische r2/r4/r8-Formation noch einen Memory- oder KI-Befund.

## Bester naechster Schritt

S1-EC9 sollte auf derselben kleinen Fixture alle fuenf Formationsarme einer
Refinementstufe gemeinsam ausfuehren und die bestehenden Kontrollen pruefen:
AB-Identitaetswiederholung, neutrale Ablationsarme, objektgetrennte
Ausgabenzustaende, gleiche Feldresultate bei ausgeschalteter Rueckwirkung und
erhaltenes Ressourcenbudget. Noch keine volle kanonische Formation.
