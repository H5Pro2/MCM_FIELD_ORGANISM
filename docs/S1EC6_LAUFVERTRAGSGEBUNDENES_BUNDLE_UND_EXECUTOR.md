# S1-EC6: Laufvertragsgebundenes Bundle und Executor

## Status

```text
RUN_CONTRACT_IS_SINGLE_PATH_AUTHORITY
SYNTHETIC_LIFECYCLE_ACCEPTED
NO_FIELD_EXECUTION
```

S1-EC6 bindet S1-EC1, S1-EC2 und S1-EC5 an den separaten
S1-EC3-Laufvertrag. Im neuen Pfad ist dieser Vertrag die einzige Quelle fuer
Ausfuehrungsidentitaet sowie Report-, Attempt- und Lockpfad.

## Implementierung

```text
mcm_field_organism/e1_confirmation_prepared_execution_bundle.py
mcm_field_organism/e1_confirmation_typed_prepared_inputs.py
mcm_field_organism/e1_confirmation_descriptor_input_resolver.py
tests/test_e1_confirmation_run_contract_bundle.py
```

## Neuer Pfad

```text
S1-EC3-Forschungsdeskriptor
-> S1-EC3-Synthetic-Laufvertrag
   - execution_id
   - report_path
   - attempt_path
   - lock_path
   - No-Retry
-> S1-EC5-Eingaberesolver
-> S1-EC2-Typbindung
-> S1-EC1-Bundle mit Laufvertragsdigest
-> synthetischer Exactly-once-Executor
-> Receipt mit demselben Laufvertragsdigest
```

Der neue Bundlekonstruktor liest die drei Pfade direkt aus dem Laufvertrag.
Er importiert oder verwendet keine Dateinamenskonstante zur Zielableitung.
Der Executor arbeitet anschliessend nur mit den im Bundle gebundenen Pfaden.

## Kompatibilitaetsgrenze

Der bisherige S1-EC1-Synthetic-Konstruktor bleibt fuer seine vorhandenen
Tests bestehen und traegt einen expliziten Legacy-Unbound-Laufdigest. Er ist
nicht Teil des neuen S1-EC6-Pfads. Beide Profile sind im Bundle und Receipt
geschlossen registriert; unbekannte Identitaeten oder Zielnamen werden
abgelehnt.

## Abnahme

- Identitaet und alle drei Pfade stimmen wortgleich zwischen Laufvertrag und
  Bundle ueberein;
- Bundle und Receipt tragen denselben Laufvertragsdigest;
- der vollstaendige S1-EC5-Eingabesatz wird an den Vertrag gebunden;
- Report entsteht nur am vertraglichen temporaeren Pfad;
- Attempt wird erst nach verifizierter Publikation entfernt;
- Lock wird freigegeben;
- der neue Konstruktor leitet keine Zielnamen ab;
- terminale S1-EB31-Artefakte bleiben unveraendert.

## Verifikation

```text
.venv/Scripts/python.exe -m pytest -q \
  tests/test_e1_confirmation_prepared_execution_bundle.py \
  tests/test_e1_confirmation_typed_prepared_inputs.py \
  tests/test_e1_confirmation_research_corridor.py \
  tests/test_e1_confirmation_descriptor_refinement_planner.py \
  tests/test_e1_confirmation_descriptor_input_resolver.py \
  tests/test_e1_confirmation_run_contract_bundle.py

30 passed
```

Die bekannte Warnung betrifft ausschliesslich `.pytest_cache`.

## Evidenzgrenze

Der Consumer liefert weiterhin nur einen synthetischen Digest. Formation,
Probe, Ergebniskern und kanonische Persistenz wurden nicht ausgefuehrt.
S1-EC6 ist ein technischer Lebenszyklusbefund und kein E1- oder
MCM-Memory-Befund.

## Bester naechster Schritt

S1-EC7 sollte einen privaten Formation-Consumer definieren, der nach dem
Attempt ausschliesslich die bereits gebundenen S1-EC5-Objekte liest. Zunaechst
muss er mit substituierten kleinen Rechenkernen nachweisen, dass kein
Korridor-, Quellen-, Plan-, Feld- oder Zustandsbuilder aufgerufen wird. Noch
keine kanonische Ausfuehrung und kein Forschungsclaim.
