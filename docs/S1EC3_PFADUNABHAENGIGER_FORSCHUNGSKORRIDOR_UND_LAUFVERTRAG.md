# S1-EC3: Pfadunabhaengiger Forschungskorridor und Laufvertrag

## Status

```text
RESEARCH_AND_RUN_LIFECYCLES_SEPARATED
SYNTHETIC_CONTRACTS_ONLY
CANONICAL_EXECUTION_NOT_AUTHORIZED
```

S1-EC3 trennt die unveraenderten Forschungsbedingungen von jeder
Ausfuehrungsidentitaet und jedem Exactly-once-Zielpfad. Der terminale
S1-EB31-Attempt bleibt real vorhanden und wird vom neuen
Forschungsdeskriptor weder gelesen noch ausgeblendet.

## Implementierung

```text
mcm_field_organism/e1_confirmation_research_corridor.py
mcm_field_organism/e1_confirmation_typed_prepared_inputs.py
tests/test_e1_confirmation_research_corridor.py
```

## Forschungskorridor

`E1ConfirmationResearchCorridorDescriptor` bindet ausschliesslich:

- die Digests und Entscheidung des unveraenderten S1-EA6-Ausgangs;
- Forschungsfrage, Quellen-, Mechanik- und Schwellenpolitik;
- r2/r4/r8 und deren History-/Probe-Schrittinventar;
- erforderliche Kontrollen, technische Entscheidungen und Regeln;
- den numerischen Signalabstand;
- geschlossene Memory- und KI-Claims;
- als Uebergangsbindung den unveraenderten alten Planerdigest.

Der Deskriptor enthaelt keinen Upstream-Pfad, keinen Report-, Attempt- oder
Lockpfad, keine Ausfuehrungs-ID und kein Startgate.

## Separater Laufvertrag

`E1ConfirmationSyntheticRunContract` bindet separat:

- eine neue synthetische Ausfuehrungsidentitaet;
- den Digest des Forschungsdeskriptors;
- neue Report-, Attempt- und Lockpfade in einem temporaeren Verzeichnis;
- No-Retry;
- geschlossene kanonische Ausfuehrung und Claims.

Seine Konstruktion startet keinen Lauf und erzeugt keine Datei.

## S1-EC2-Anschluss

Der typisierte S1-EC2-Adapter akzeptiert nun entweder den alten
S1-EB-Korridor oder den neuen S1-EC3-Deskriptor. Beim neuen Deskriptor werden
vorhandene alte Plansaetze noch gegen dessen explizite
`legacy_planner_contract_digest`-Bindung geprueft. Damit ist die
Pfadabhaengigkeit aus dem Korridor entfernt, aber noch nicht aus der
Planerimplementierung.

## Verifikation

```text
.venv/Scripts/python.exe -m pytest -q \
  tests/test_e1_confirmation_prepared_execution_bundle.py \
  tests/test_e1_confirmation_typed_prepared_inputs.py \
  tests/test_e1_confirmation_research_corridor.py

17 passed
```

Die bekannte Pytest-Cachewarnung betrifft nur `.pytest_cache`.

## Evidenzgrenze

Es wurden nur Deskriptoren, Laufvertraege und vorbereitete Bundles erzeugt.
Keine Formation, Probe, Feldauswertung oder kanonische Persistenz wurde
ausgefuehrt. Daraus folgt kein E1-, Memory-, Feldzeit-, Bedeutungs-,
Organisations-, Topologie- oder KI-Befund.

## Bester naechster Schritt

S1-EC4 sollte einen neuen pfadunabhaengigen Refinementplaner bereitstellen,
der den S1-EC3-Deskriptor direkt akzeptiert. Seine Ausgaben muessen fuer
dieselben AB-, BA- und Probesequenzen in allen zeitlichen, integralen und
Handoff-Feldern mit den unveraenderten alten Plaenen uebereinstimmen; nur die
Vertragsbindung darf auf den neuen Deskriptordigest wechseln. Weiterhin kein
Feld- oder kanonischer Lauf.
