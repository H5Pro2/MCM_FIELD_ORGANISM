# S1-TP: Statische Testoberflaechen-Reparatur und neues Einmallaufbudget

## Status und Zweck

S1-TP bindet ausschliesslich die Reparatur der in S1-TO fehlgeschlagenen
Oberflaechenassertion. S1-TP aendert noch keine Datei und fuehrt keinen Test
aus.

```text
S1_TP_SINGLE_TEST_SURFACE_SCOPE_REPAIR_AND_ONE_NEW_RUN_BUDGET_BOUND
```

## Gebundener Ausgangsbefund

Der einzige S1-TO-Lauf meldete:

```text
Ran 24 tests in 3.383s
FAILED (failures=1)
```

23 Methoden waren erfolgreich. Nur
`test_24_api_types_and_forbidden_surfaces` schlug fehl, weil die Assertion
alle Namen aus `__all__` einschliesslich Konstanten durchsucht und dadurch
`ATLAS_FILE_SHA256` wegen des Wortteils `file` trifft.

Die Konstante ist eine gebundene Identitaet und keine Dateioberflaeche. Das
Produktionsmodul besitzt keinen Dateiimport und keine Dateioperation.

## Eingefrorene Dateien

```text
mcm_field_organism/four_node_candidate_observation_envelope.py
  e7ef64fbbb8dc22ad123484ac53ab6cdbe1d5d4f17440a47ffd311f3c70ad74d
tests/test_four_node_candidate_observation_envelope.py
  ad415e940b223b694ecad26436288f80fbc496fc999379559fb5d4b59a279995
```

Das Produktionsmodul bleibt waehrend der Reparatur byteidentisch. Weitere
Produktions-, Test-, Fixture-, Report- oder Artefaktdateien bleiben
unveraendert.

## Exakte Reparaturgrenze

S1-TQ darf genau eine bestehende Datei aendern:

```text
tests/test_four_node_candidate_observation_envelope.py
```

In Test 24 darf exakt dieser einmal vorhandene Block ersetzt werden:

```python
        public = set(envelope_module.__all__)
        self.assertFalse(any(any(token in name.lower() for token in (
            "file", "producer", "builder", "parse", "repair", "runner", "comparator", "serialize"
        )) for name in public))
```

durch:

```python
        public_functions = {
            name for name in envelope_module.__all__ if callable(getattr(envelope_module, name))
            and not isinstance(getattr(envelope_module, name), type)
        }
        self.assertFalse(any(any(token in name.lower() for token in (
            "file", "producer", "builder", "parse", "repair", "runner", "comparator", "serialize"
        )) for name in public_functions))
```

Damit prueft die Assertion weiterhin dieselben verbotenen Begriffe, aber nur
gegen die tatsaechlichen oeffentlichen aufrufbaren Nicht-Typen. Konstanten
und Recordklassen werden nicht mehr faelschlich als Funktionsoberflaechen
klassifiziert.

Der vorab im Arbeitsspeicher berechnete Nachher-Digest der Testdatei ist:

```text
b457cab3e798859cdc1550d98800ca130bcce055341d6b15ebdcc4ef53595d8c
```

Die simulierte Nachher-Datei besitzt gueltige Python-Syntax, weiterhin exakt
24 Testmethoden und genau eine Methode mit dem Namen
`test_24_api_types_and_forbidden_surfaces`.

## Statische Vorpruefung fuer S1-TQ

Vor einer Testausfuehrung muessen gemeinsam gelten:

1. der Produktionsmoduldigest stimmt unveraendert;
2. der Ausgangsdigest der Testdatei stimmt vor der Reparatur;
3. der gebundene Block kommt exakt einmal vor;
4. nach dem Austausch stimmt der gebundene Nachher-Digest;
5. beide Dateien besitzen gueltige Syntax;
6. die Testdatei enthaelt weiterhin exakt 24 Testmethoden;
7. Produktionsimporte, `__all__`, Fehlercodes und Testdaten sind unveraendert;
8. `git diff --check` meldet keinen Fehler;
9. vor der Ergebnisdokumentation ist nur die eine Testdatei geaendert.

Bei jeder Abweichung endet S1-TQ vor einer Ausfuehrung fail-closed.

## Neues einmaliges Testbudget

Nach erfolgreicher statischer Vorpruefung darf S1-TQ genau einmal ausfuehren:

```text
python -m unittest tests.test_four_node_candidate_observation_envelope -v
```

Erwartet werden exakt 24 erfolgreiche Testmethoden und `OK`. Ein zweiter Lauf
ist nicht freigegeben. Es duerfen keine weiteren Tests, realen Reports,
Feldlaeufe oder Modellproducer aufgerufen werden.

## Ergebnis- und Aussagegrenze

Nur `Ran 24 tests` zusammen mit `OK` darf die rein technische Abnahme der
synthetischen Kandidatenhuelle schliessen. Jeder Fehler, Fehlschlag, eine
andere Methodenzahl oder eine Digestabweichung stoppt S1-TQ ohne Retry.

Auch ein positives Ergebnis waere nur eine technische Strukturabnahme. Es
waere kein Kandidatenbefund und kein Befund zur Entwicklungsrichtung einer
hypothetischen MCM-Memory.

## Naechster Schritt

Der einzige naechste Schritt ist S1-TQ fuer den exakt gebundenen Austausch,
die statische Vorpruefung und anschliessend genau einen neuen Lauf der einen
Testdatei.
