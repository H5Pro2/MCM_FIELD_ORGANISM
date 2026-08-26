# S1-TO: Einmaliger synthetischer Kandidatenhuellen-Testlauf nicht abgenommen

## Ausfuehrungsumfang

S1-TO fuehrte genau einmal und unveraendert ausschliesslich die in S1-TN
definierte Testdatei aus:

```text
python -m unittest tests.test_four_node_candidate_observation_envelope -v
```

Es wurden keine weiteren Tests, keine realen Reports, kein Feldlauf und kein
Modellproducer aufgerufen. Ein Retry fand nicht statt.

## Ergebnis

```text
Ran 24 tests in 3.383s
FAILED (failures=1)
```

23 Testmethoden waren erfolgreich. Fehlgeschlagen ist ausschliesslich:

```text
test_24_api_types_and_forbidden_surfaces
```

S1-TO ist deshalb technisch nicht abgenommen.

## Statische Ursachenabgrenzung

Test 24 sucht verbotene Oberflaechenbegriffe in allen Namen aus `__all__`.
Damit erfasst er neben Funktionen und Typen auch gebundene Konstanten. Die
vertraglich erforderliche Identitaetskonstante

```text
ATLAS_FILE_SHA256
```

enthaelt den Wortteil `file` und loest dadurch die Assertion aus. Die
Konstante ist keine Datei-API und das Produktionsmodul besitzt weiterhin
keinen Dateiimport und keine Dateioperation.

Der Fehlschlag liegt damit in der Abgrenzung der Testassertion. Diese
Einordnung repariert den Test nicht, ersetzt keinen erfolgreichen Lauf und
nimmt die Implementierung nicht vorzeitig ab.

## Eingefrorener Stand

```text
mcm_field_organism/four_node_candidate_observation_envelope.py
  e7ef64fbbb8dc22ad123484ac53ab6cdbe1d5d4f17440a47ffd311f3c70ad74d
tests/test_four_node_candidate_observation_envelope.py
  ad415e940b223b694ecad26436288f80fbc496fc999379559fb5d4b59a279995
```

Der S1-TO-Lauf aenderte keine Quelldatei. Die 23 erfolgreichen Methoden
belegen innerhalb dieses synthetischen Laufs insbesondere, dass Positivhuelle,
Kardinalitaeten, Digests und alle 32 isolierten Fail-Closed-Mutationen die
definierten Erwartungen erfuellten. Wegen des Gesamtfehlers bleibt die
technische Abnahme dennoch offen.

## Verbindliche Entscheidung

```text
S1_TO_SINGLE_SYNTHETIC_RUN_NOT_ACCEPTED
23_OF_24_TEST_METHODS_PASSED_ONE_SURFACE_SCOPE_ASSERTION_FAILED
NO_RETRY_NO_SOURCE_CHANGE_NO_TECHNICAL_ACCEPTANCE
NO_CANDIDATE_NO_FUNCTIONAL_DECISION
```

## Aussagegrenze und naechster Schritt

Das Ergebnis ist ausschliesslich ein technischer Testbefund. Es ist kein
Kandidatenbefund und kein Befund zur Entwicklungsrichtung einer hypothetischen
MCM-Memory.

Der einzige naechste Schritt ist S1-TP als statischer Reparatur- und
Neulaufvertrag. Er muss vor jeder Aenderung pruefen und exakt binden, wie die
Oberflaechenassertion auf tatsaechliche oeffentliche API-Funktionen begrenzt
werden kann, ohne Konstanten, Produktionscode, Testzahl oder andere
Testmethoden zu veraendern. S1-TP darf noch nichts reparieren und keinen Test
ausfuehren.
