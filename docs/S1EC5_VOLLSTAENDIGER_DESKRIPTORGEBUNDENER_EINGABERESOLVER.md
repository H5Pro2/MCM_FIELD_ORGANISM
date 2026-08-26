# S1-EC5: Vollstaendiger deskriptorgebundener Eingaberesolver

## Status

```text
LEGACY_CORRIDOR_CONSTRUCTION_REMOVED_FROM_INPUT_PATH
COMPLETE_TYPED_INPUT_SET_READY
NO_FIELD_EXECUTION
```

S1-EC5 erzeugt den vollstaendigen typisierten Eingangssatz der neuen
Entwicklungslinie direkt aus S1-EC3 und S1-EC4. Der alte
S1-EB-Korridorkonstruktor wird in diesem Pfad weder importiert noch
aufgerufen.

## Implementierung

```text
mcm_field_organism/e1_confirmation_descriptor_input_resolver.py
tests/test_e1_confirmation_descriptor_input_resolver.py
```

## Direkter Eingabefluss

```text
unveraenderter S1-EA6-Bericht
-> pfadunabhaengiger S1-EC3-Forschungsdeskriptor
-> kanonische AV-Permutation
-> S1-EC4-AB-/BA-/Probeplaene
-> frisches kanonisches Anfangsfeld
-> neutraler E1-Anfangszustand
-> typisierte S1-EC2-Eingaben
-> vorbereitetes S1-EC1-Bundle
```

Der Resolver ruft den Deskriptor- und AV-Builder jeweils einmal sowie den
Planer genau dreimal fuer AB, BA und Probe auf. Er erzeugt keinen Report-,
Attempt- oder Lockpfad und fuehrt keinen Feldschritt aus.

## Abnahme

- alle acht S1-EC2-Rollen sind vorhanden;
- alle drei Plangruppen tragen denselben S1-EC3-Deskriptordigest;
- Anfangsfeld steht auf Tick null ohne Verteilung oder Substrat;
- der E1-Anfangszustand besitzt ausschliesslich neutrale Kantenbindungen;
- der Resolverquelltext enthaelt keinen alten Korridorkonstruktor oder
  S1-EB-Zielnamen;
- das direkte Bundle passiert den synthetischen Attempt-Lebenszyklus;
- S1-EB31-Artefakte bleiben unveraendert.

## Verifikation

```text
.venv/Scripts/python.exe -m pytest -q \
  tests/test_e1_confirmation_prepared_execution_bundle.py \
  tests/test_e1_confirmation_typed_prepared_inputs.py \
  tests/test_e1_confirmation_research_corridor.py \
  tests/test_e1_confirmation_descriptor_refinement_planner.py \
  tests/test_e1_confirmation_descriptor_input_resolver.py

26 passed
```

Die bekannte Warnung betrifft nur `.pytest_cache`.

## Evidenzgrenze

S1-EC5 belegt die vollstaendige technische Eingabevorbereitung ohne den
terminalen Legacy-Korridor. Die gebundenen Feld- und E1-Objekte werden nicht
fortgeschrieben. Es gibt daher keinen neuen E1- oder MCM-Memory-Befund.

## Bester naechster Schritt

S1-EC6 sollte den separaten S1-EC3-Laufvertrag als einzige Quelle fuer
Ausfuehrungsidentitaet und temporaere Report-/Attempt-/Lockpfade in S1-EC1
einspeisen. Bundle und Worker duerfen diese Pfade dann nicht mehr selbst
ableiten. Damit wird die verbleibende doppelte Pfaddefinition entfernt,
weiterhin nur synthetisch und ohne Feldlauf.
