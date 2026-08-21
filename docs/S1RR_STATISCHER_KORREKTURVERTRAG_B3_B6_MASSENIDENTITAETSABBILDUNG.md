# S1-RR: Statischer Korrekturvertrag fuer die B3-B6-Massenidentitaetsabbildung

## Status und Zweck

S1-RR bindet ausschliesslich die Korrektur des in S1-RQ gefundenen
Feldnamenunterschieds zwischen registriertem B3-B6-Massenpayload und nativem
`MCMSubstrateMass`.

S1-RR implementiert nichts und fuehrt keinen Test, Adapter, Feldschritt oder
Matrixfall aus.

Vertragsentscheidung:

```text
ONE_REVERSIBLE_KEY_TRANSLATION_BOUND
FORWARD_NODE_ID_TO_NEURON_ID
REVERSE_NEURON_ID_TO_NODE_ID
VALUES_ORDER_ARMS_AND_DIGESTS_UNCHANGED
NO_MANIFEST_OR_NATIVE_CLASS_CHANGE
NO_IMPLEMENTATION_NO_TEST_EXECUTION
```

## Exakte Fehlergrenze

Der registrierte Massenpayload besitzt pro B3-B6-Knoten exakt:

```json
{"mass": 0.25, "node_id": "node-a"}
```

Der native Konstruktor `MCMSubstrateMass.from_payload` akzeptiert exakt:

```json
{"mass": 0.25, "neuron_id": "node-a"}
```

`node_id` und `neuron_id` bezeichnen an dieser Grenze dieselbe technische
Knotenidentitaet. Sie sind dennoch verschiedene Schemafelder und duerfen
nicht stillschweigend als austauschbar behandelt werden.

## Zulaessiger Einfuegepunkt

Die spaetere Korrektur darf ausschliesslich diese beiden lokalen Funktionen
in `mcm_field_organism/four_node_fresh_factory.py` aendern:

```text
_build_substrate
_state_projection
```

Keine andere Produktions- oder Testdatei darf fachlich geaendert werden.
Forschungsstandsdokumentation bleibt zulaessig.

## Vorwaertsabbildung

`_build_substrate` muss jeden registrierten Masseneintrag vor Aufruf von
`MCMSubstrateState.from_payload` explizit neu aufbauen:

```python
{
    "neuron_id": registered_mass["node_id"],
    "mass": registered_mass["mass"],
}
```

Vor der Abbildung gelten fail-closed:

- der registrierte Eintrag besitzt exakt die Schluessel `node_id` und
  `mass`;
- es liegen exakt vier Eintraege vor;
- ihre Reihenfolge ist node-a, node-b, node-c, node-d;
- jede Identitaet ist eindeutig;
- jeder Massenwert ist exakt `0.25`;
- keine unbekannten Felder werden verworfen oder weitergereicht.

Die Abbildung veraendert nur den Schluesselnamen. Identitaetswert und
Massenwert werden unveraendert uebernommen.

## Rueckabbildung

`_state_projection` darf fuer `FourNodeSubstrateFreshState` den nativen
Massenpayload nicht direkt publizieren. Jeder native Eintrag wird explizit
zurueckgebildet:

```python
{
    "node_id": native_mass.neuron_id,
    "mass": native_mass.mass,
}
```

Arm, registrierter Kanteninventardigest und
`frozen_spec_digest_or_null` werden wie in S1-RP getrennt eingesetzt. Das
Ergebnis muss wieder exakt das registrierte S1-RK-`state_payload` ergeben.

## Reversible Identitaet

Fuer jeden der vier Eintraege muss gelten:

```text
registered.node_id
    == native.neuron_id
    == roundtrip.node_id

registered.mass
    == native.mass
    == roundtrip.mass
    == 0.25
```

Die geordnete Viererfolge muss in beiden Richtungen erhalten bleiben. Eine
Sortierung nach der Uebersetzung ist nur zulaessig, weil der native
`MCMSubstrateState` dieselbe kanonische Reihenfolge node-a bis node-d
erzwingt; sie darf keine fehlende oder doppelte Identitaet verdecken.

## Unveraendertheitsvertrag

Die Korrektur darf nicht veraendern:

- `reports/s1rk_four_node_fresh_manifest.json`;
- Manifestconsumer und Manifestdigest;
- `MCMSubstrateMass`, `MCMSubstrateState` oder deren native API;
- B3-B6-Modellrollen und Privatdigests;
- Arm-IDs, `lambda_sm_per_second`, `kappa`, `eta` oder Gesamtmasse;
- die vier Einzelmassen;
- registrierten oder nativen Kanten-Digestpfad;
- B6-CONST-V-Spezifikationsdigest;
- A0-A3, B1, B2, M1, M2, M4 oder M5;
- die 16 bestehenden Fabriktests oder ihr Budget.

Es wird kein Aliasfeld im Manifest und kein zusaetzliches Feld im nativen
Zustand eingefuehrt.

## Roundtrip- und Digestpflicht

Nach der Rueckabbildung muessen weiterhin beide bereits implementierten
Pruefungen bestehen:

```text
projected_state_payload == registered_state_payload
SHA256(reconstructed_private_payload) == registered_private_digest
```

Dies gilt getrennt fuer B3, B4, B5 und B6. Eine gemeinsame erfolgreiche
Rolle darf keinen Fehler einer anderen Rolle verdecken.

## Fail-Closed-Regeln

Folgende Abweichungen enden ohne Teilobjekt mit
`FRESH_FACTORY_PRIVATE_STATE_INVALID`:

- fehlendes oder zusaetzliches Massenfeld;
- andere Anzahl oder Reihenfolge;
- doppelte oder unbekannte Knotenidentitaet;
- anderer Massenwert;
- nicht reversible Identitaet;
- abweichender projizierter State-Payload.

Ein abweichender rekonstruierter Privatdigest endet weiterhin mit
`FRESH_FACTORY_PRIVATE_DIGEST_MISMATCH`.

## Erneutes Testbudget

Es werden keine neuen Tests definiert. Nach einer getrennten
Implementierungsstufe darf ausschliesslich derselbe S1-RQ-Befehl erneut
ausgefuehrt werden:

```text
python -m unittest discover -s tests -p "test_four_node_fresh_factory.py" -v
```

Technische Abnahme erfordert:

- 16 von 16 bestandene Testmethoden;
- erfolgreiche B3-, B4-, B5- und B6-Subtests;
- erfolgreichen Aufbau aller 14 Rollen;
- erfolgreiche Objekttrennung fuer B3;
- Exitcode `0`;
- keine Test- oder Codeaenderung zwischen Korrekturcommit und Wiederholung.

## Technische Aussagegrenze

S1-RR korrigiert nur eine Schemauebersetzung. Daraus folgt keine Aussage
ueber Adapterfunktion, Felddynamik oder hypothetische MCM-Memory.

## Paketstatus

```text
S1RR_REVERSIBLE_MASS_KEY_TRANSLATION_BOUND
CORRECTION_NOT_IMPLEMENTED
S1RQ_ACCEPTANCE_STILL_WITHHELD
BASELINE_ADAPTERS_NOT_CONNECTED
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RS - Implementierung der gebundenen B3-B6-Abbildung
        node_id -> neuron_id -> node_id
```

S1-RS darf nur `_build_substrate` und den Substratzweig von
`_state_projection` aendern. Keine Testaenderung, keine Testausfuehrung,
kein Adapteranschluss, keine Matrixzelle und kein Feldlauf.
