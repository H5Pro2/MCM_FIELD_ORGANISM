# S1-EC4: Deskriptorgebundener Refinementplaner

## Status

```text
DESCRIPTOR_BOUND_PLANNER_EQUIVALENT_TO_LEGACY
NO_FIELD_EXECUTION
CANONICAL_EXECUTION_NOT_AUTHORIZED
```

S1-EC4 ersetzt die Pfadvertragsabhaengigkeit des Refinementplaners durch die
direkte Bindung an den pfadunabhaengigen S1-EC3-Forschungsdeskriptor. Die
zeitlichen und numerischen Planregeln wurden nicht veraendert.

## Implementierung

```text
mcm_field_organism/e1_confirmation_descriptor_refinement_planner.py
mcm_field_organism/e1_confirmation_typed_prepared_inputs.py
tests/test_e1_confirmation_descriptor_refinement_planner.py
```

## Wiederverwendete Mechanik

Der neue Planer verwendet unveraendert:

- Completion-Ticks der Rezeptorframes;
- gemeinsame Zeitskala und Horizontgrenzen;
- die bestehenden `r2`, `r4` und `r8`-Refinementfaktoren;
- `_refined_steps(...)`;
- `handoff_receptor_completion_groups(...)`;
- `_source_contact_evidence(...)`;
- `_handoff_digest(...)`;
- die bestehenden einzelnen `E1ConfirmationRefinementPlan`-Objekte.

Neu ist nur `E1ConfirmationDescriptorRefinementPlanSet`. Es traegt anstelle
des alten vollstaendigen Korridorvertragsdigests den Digest des
S1-EC3-Forschungsdeskriptors.

## Aequivalenzbefund

Fuer dieselben AB-, BA- und Probesequenzen stimmen neue und alte Plaene
feldweise exakt ueberein:

- Refinement-ID und Faktor;
- Horizont und Basisintervallzahl;
- jeder einzelne Vorschlagsschritt;
- Rezeptor-Handoff;
- Completion-Ticks;
- Quellkontakt-Digest;
- vorzeichenbehaftetes, absolutes und quadratisches Integral;
- Handoff-Digest;
- Quellereigniszahl.

Nur die aeussere Plan-Set-Vertragsbindung ist neu.

S1-EC2 akzeptiert jetzt vollstaendige Legacy- oder vollstaendige
deskriptorgebundene Planfamilien. Eine Mischung wird abgelehnt.

## Verifikation

```text
.venv/Scripts/python.exe -m pytest -q \
  tests/test_e1_confirmation_prepared_execution_bundle.py \
  tests/test_e1_confirmation_typed_prepared_inputs.py \
  tests/test_e1_confirmation_research_corridor.py \
  tests/test_e1_confirmation_descriptor_refinement_planner.py

21 passed
```

Die bekannte Warnung betrifft nur den nicht beschreibbaren
`.pytest_cache`-Pfad.

## Evidenzgrenze

Planerzeugung ist keine Feld- oder E1-Ausfuehrung. Es wurden keine Zustaende
gebildet, keine Probe ausgefuehrt und keine Forschungsentscheidung erzeugt.
Der Aequivalenzbefund betrifft ausschliesslich die technische Planstruktur.

## Bester naechster Schritt

S1-EC5 sollte den vollstaendigen typisierten Eingangssatz direkt aus
S1-EC3-Deskriptor, kanonischer AV-Permutation, S1-EC4-Plaenen, frischem
Anfangsfeld und neutralem E1-Anfangszustand erzeugen. Damit muss auch in den
Tests kein alter S1-EB-Korridor mehr konstruiert oder dessen Attempt fuer
einen Konstruktionsaufruf ausgeblendet werden. Weiterhin kein Feldlauf.
