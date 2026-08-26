# S1-EC15: Atomarer Fixture-Publisher fuer den vollstaendigen Zustandshandoff

## Status

```text
COMPLETE_FIXTURE_PAYLOAD_PUBLICATION_ACCEPTED
FINAL_REREAD_ACCEPTED
TYPED_RELOAD_ACCEPTED
EXACTLY_ONCE_FAILURE_POLICY_ACCEPTED
NO_FULL_FORMATION
NO_PROBE
```

S1-EC15 implementiert und prueft die atomare Publikation des vollstaendigen
S1-EC14-Payloads. Verwendet wird ausschliesslich eine 15-Zustands-Fixture auf
der vollstaendigen 84-Knoten-/145-Kanten-Geometrie. S1-EC13 wird nicht
wiederholt und kein neuer Forschungsbericht erzeugt.

## Implementierung

```text
mcm_field_organism/e1_confirmation_full_formation_handoff_publisher.py
tests/test_e1_confirmation_full_formation_handoff_publisher.py
```

## Getrennte Publikationsidentitaet

```text
publication_id:
e1.full-formation-handoff.s1ec15.fixture.v1

report:
e1_full_formation_handoff_s1ec15_fixture_once_v1.json

attempt:
e1_full_formation_handoff_s1ec15_fixture_once_v1.attempt.json

lock:
e1_full_formation_handoff_s1ec15_fixture_once_v1.lock
```

Diese Identitaet ist von S1-EC3, S1-EC13 und allen kanonischen Pfaden
getrennt. Der Publisher akzeptiert nur Fixture-Payloads.

## Bestaetigte Reihenfolge

```text
vorbereiteter vollstaendiger Payload
-> Lock exklusiv
-> Attempt exklusiv
-> vollstaendigen temporaeren Bericht schreiben und fsyncen
-> temporaeren Bericht erneut lesen
-> finalen Bericht exklusiv publizieren
-> finalen Bericht erneut lesen und SHA-256 pruefen
-> eingebetteten Payload-Digest pruefen
-> alle 15 Zustaende typisiert zurueckladen
-> Formationsergebnisdigest pruefen
-> Attempt entfernen
-> Lock freigeben
```

Ein Fehler nach dem Attempt laesst den Attempt bestehen und sperrt dieselbe
Identitaet gegen Wiederholung. Ein bereits erfolgreich verwendeter
Berichtspfad sperrt ebenfalls jede zweite Publikation.

## JSON-Normalisierung

Beim ersten Test wurde eine direkte Python-Objektgleichheit zwischen Tupeln
vor dem Schreiben und Listen nach dem JSON-Reread verworfen. Die Pruefung
verwendet nun korrekt die kanonische JSON-Digestgleichheit und danach den
typisierten Loader. Weder Payloadschema noch Zahlenwerte wurden veraendert.

## Abnahme

- vollstaendiger Bericht wurde atomar publiziert und erneut gelesen;
- Payload- und Formationsergebnisdigest blieben erhalten;
- alle 15 E1-Zustaende wurden aus dem finalen Bericht typisiert geladen;
- Mutation eines vorbereiteten Payloads wurde vor Markern abgelehnt;
- ein erzwungener Reloadfehler liess den Attempt bestehen;
- erneute Nutzung derselben Identitaet wurde abgelehnt;
- S1-EC13 und alle geschuetzten Artefakte blieben unveraendert.

```text
publisher_policy_digest = 96617801a6591a96415f0df591e7175d767e6dab0240355446fb53de85f0314f
70 tests passed
```

Die bekannte Warnung betrifft nur den nicht beschreibbaren Pytest-Cache.

## Evidenzgrenze

S1-EC15 bestaetigt den Publisher und die Exactly-once-Fehlerpolitik fuer
einen vollstaendigen Fixture-Payload. Es wurde kein realer neuer
Vollformationszustand publiziert. Daraus folgt kein Probe-, Memory-, Lern-,
Feldzeit-, Organisations-, Semantik-, Selbstregulations- oder KI-Befund.

Der **STOPP fuer Wiederholung und direkten Probe-Handoff von S1-EC13** bleibt
unveraendert bestehen.

## Bester naechster Schritt

S1-EC16 sollte statisch einen neuen temporaeren Gesamtlebenszyklusvertrag
binden, der S1-EC12-Preflight, Vollformation, S1-EC14-Payloadbildung und
S1-EC15-Publikation in genau dieser Reihenfolge kombiniert. Die neue
Identitaet, Ressourcengates und No-Retry-Grenze muessen vor jeder Ausfuehrung
feststehen. Noch keine neue Vollformation und keine Probe.
