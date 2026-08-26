# S1-EC2: Typisierte vorbereitete E1-Eingaben

## Status

```text
TYPED_PREPARED_INPUTS_SYNTHETICALLY_ACCEPTED
CANONICAL_EXECUTION_NOT_AUTHORIZED
NO_RESEARCH_RESULT
```

S1-EC2 bindet die fachlichen Eingaberollen der verfeinerten E1-Kette an den
in S1-EC1 abgenommenen Bundle-Lebenszyklus. Die alten S1-EB-Module, der
terminale S1-EB31-Attempt und S1-EA6 bleiben unveraendert.

## Implementierung

```text
mcm_field_organism/e1_confirmation_typed_prepared_inputs.py
tests/test_e1_confirmation_typed_prepared_inputs.py
```

## Gebundene Rollen

```text
corridor
av_permutation
history_ab_plans
history_ba_plans
probe_sequences
probe_plans
initial_field
initial_state
```

Der Adapter prueft vor Lock und Attempt:

- den konkreten Python-Typ jeder Rolle;
- die Bindung aller drei Plansaetze an denselben Korridordigest;
- die Quellkontakt-Digests und Integrale von AB, BA und Probe;
- die identische geordnete Refinementfamilie;
- die gemeinsame Geometrie von Anfangsfeld und E1-Zustand;
- Tick null, fehlende Verteilung, fehlendes Substrat und neutrale
  Kantenbindungen;
- den aktuellen Digest jedes konkreten Objekts.

Danach traegt S1-EC1 genau diese Objektinstanzen durch den synthetischen
Attempt-Lebenszyklus. Es erfolgt keine erneute Eingabeaufloesung.

## Verifikation

```text
.venv/Scripts/python.exe -m pytest -q \
  tests/test_e1_confirmation_prepared_execution_bundle.py \
  tests/test_e1_confirmation_typed_prepared_inputs.py

11 passed
```

Die bekannte Pytest-Cachewarnung betrifft nur den nicht beschreibbaren
`.pytest_cache`-Pfad.

Der Test konstruiert die unveraenderte alte S1-EB-Vertragsstruktur statisch,
waehrend er die Existenz der terminalen S1-EB-Zielnamen nur fuer diesen
Konstruktionsaufruf ausblendet. Die echten Dateien werden weder entfernt noch
veraendert. Der ausgefuehrte Bundle-Lebenszyklus verwendet ausschliesslich
temporaere Zielpfade.

## Ergebnis

Der in S1-EB31 gefundene Lebenszykluswiderspruch ist fuer die acht konkreten
Eingaberollen technisch aufgeloest: Nach dem Attempt ist kein Korridor-,
Quellen-, Plan-, Feld- oder Zustandskonstruktor erforderlich.

Das ist noch keine vollstaendige neue Laufkette. Der alte
`E1RefinedConfirmationContract` ist weiterhin inhaltlich und ueber feste
Digests an S1-EB sowie dessen Zielpfade gebunden. Er kann deshalb nicht als
normaler Konstruktor einer neuen Ausfuehrungsidentitaet dienen.

## Evidenzgrenze

Es wurde kein Feld fortgeschrieben, kein E1-Zustand gebildet, keine Probe
ausgefuehrt und kein kanonischer Bericht publiziert. S1-EC2 liefert keinen
Memory-, Feldzeit-, Bedeutungs-, Organisations-, Topologie- oder KI-Befund.

## Bester naechster Schritt

Als naechstes sollte S1-EC3 einen pfadunabhaengigen strukturellen
Korridordeskriptor fuer die unveraenderten Forschungsbedingungen definieren.
Exactly-once-Zielpfade und Ausfuehrungsidentitaet muessen in einem separaten
Laufvertrag liegen. Erst diese Trennung erlaubt eine neue Identitaet, ohne
den terminalen S1-EB31-Attempt auszublenden oder wiederzuverwenden.
