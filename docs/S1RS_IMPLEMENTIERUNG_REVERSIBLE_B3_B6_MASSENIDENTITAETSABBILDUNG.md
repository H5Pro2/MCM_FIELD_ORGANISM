# S1-RS: Implementierung der reversiblen B3-B6-Massenidentitaetsabbildung

## Status und Umfang

S1-RS implementiert die in S1-RR gebundene lokale Uebersetzung zwischen dem
registrierten Massenfeld `node_id` und dem nativen Feld `neuron_id`.

Es wurde kein Test, Adapter, Feldschritt oder Matrixfall ausgefuehrt.

Implementierungsstatus:

```text
FORWARD_NODE_ID_TO_NEURON_ID_IMPLEMENTED
REVERSE_NEURON_ID_TO_NODE_ID_IMPLEMENTED
FOUR_MASS_SHAPE_IDENTITY_ORDER_AND_VALUE_GATES_IMPLEMENTED
MANIFEST_NATIVE_CLASSES_TESTS_AND_OTHER_ROLES_UNCHANGED
NO_TEST_EXECUTION_NO_FIELD_ADVANCE
```

## Geaenderte Produktionsstelle

Geaendert wurde ausschliesslich:

```text
mcm_field_organism/four_node_fresh_factory.py
```

Der Produktionsdiff ist auf `_build_substrate` und den
`FourNodeSubstrateFreshState`-Zweig von `_state_projection` begrenzt.

## Vorwaertsabbildung

`_build_substrate` prueft jetzt vor dem nativen Bau:

- genau vier Masseneintraege;
- je Eintrag exakt die Schluessel `node_id` und `mass`;
- die Reihenfolge node-a, node-b, node-c, node-d;
- je Eintrag exakt den Massenwert `0.25`.

Erst danach wird pro Eintrag ein neues natives Mapping erzeugt:

```text
node_id -> neuron_id
mass    -> mass
```

Nur diese neu aufgebauten Eintraege werden an
`MCMSubstrateState.from_payload` uebergeben. Unbekannte oder fehlende Felder
werden nicht entfernt, ergaenzt oder toleriert.

## Rueckabbildung

Der Substratzweig von `_state_projection` erzeugt den registrierten Payload
jetzt explizit aus den nativen Wertobjekten:

```text
native MCMSubstrateMass.neuron_id -> registered node_id
native MCMSubstrateMass.mass      -> registered mass
```

Arm, registrierter Kanteninventardigest und B6-Zusatzdigest werden getrennt
wie zuvor eingesetzt. Der native `neuron_id`-Schluessel gelangt nicht in den
registrierten Payload.

## Unveraenderte Bereiche

Nicht geaendert wurden:

- S1-RK-Manifest und Manifestconsumer;
- `MCMSubstrateMass` und `MCMSubstrateState`;
- Testdateien und Testanzahl;
- Armparameter, Massenwerte oder Kanten-Digestbruecke;
- A0-A3, B1, B2, M1, M2, M4 und M5;
- Adapter, Runner, Gleichungen oder Paketexporte.

## Statischer Audit

Der statische Audit bestaetigt:

- genau eine geaenderte Produktionsdatei;
- nur die zwei in S1-RR zugelassenen Funktionsbereiche;
- syntaktisch gueltige Pythonquelle;
- keine Testaenderung;
- keinen Test- oder Advanceaufruf.

Dieser Audit bestaetigt noch nicht, dass der S1-RQ-Fehler behoben ist. Das
erfordert den unveraenderten Wiederholungslauf.

## Technische Aussagegrenze

S1-RS implementiert nur eine reversible Schemaabbildung. Daraus folgt keine
Aussage ueber Adapterfunktion, Felddynamik oder hypothetische MCM-Memory.

## Paketstatus

```text
S1RS_MASS_KEY_TRANSLATION_SOURCE_COMPLETE
S1RQ_CORRECTION_NOT_YET_TEST_ACCEPTED
FACTORY_TESTS_UNCHANGED_NOT_RERUN
BASELINE_ADAPTERS_NOT_CONNECTED
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RT - unveraenderte Wiederholung der exakt 16 Vier-Knoten-Fabriktests
```

S1-RT darf nur `tests/test_four_node_fresh_factory.py` ausfuehren und das
Ergebnis protokollieren. Keine Code- oder Testaenderung, kein Consumer-
Gesamtlauf, kein Adapteranschluss, keine Matrixzelle und kein Feldlauf.
