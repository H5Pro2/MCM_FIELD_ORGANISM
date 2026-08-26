# S1-RJ: Statischer kanonischer Payload- und Digestpraeimagevertrag der Vier-Knoten-Frischformen

## Status und Umfang

S1-RJ bindet die kanonischen Felder, Wertquellen, Listenordnungen und
Digestabhaengigkeiten fuer den in S1-RF bis S1-RI geschlossenen
Vier-Knoten-Frischbestand.

Der Vertrag umfasst:

- das untergeordnete Drei-Kanten-Inventar;
- die modellneutrale physische Geometrie;
- das davon getrennte aeussere Expositionsrollenmapping;
- die fuer alle 224 Pflichtzellen gleiche oeffentliche Frischprojektion;
- vierzehn rollenprivate Frischformen oder Zustandslosmarkierungen.

S1-RJ berechnet keinen Digest, erzeugt keine JSON-Datei, registriert keine
Geometrie, implementiert keine Fabrik und fuehrt keinen Test oder Feldlauf
aus.

Vertragsentscheidung:

```text
CANONICAL_JSON_AND_SHA256_PREIMAGE_RULE_BOUND
THREE_EDGE_INVENTORY_PREIMAGE_BOUND
PHYSICAL_GEOMETRY_PREIMAGE_BOUND
OUTER_ROLE_MAPPING_PREIMAGE_BOUND_AND_MODEL_PRIVATE
ONE_COMMON_PUBLIC_FRESH_PROJECTION_PREIMAGE_BOUND
FOURTEEN_PRIVATE_FRESH_FORMS_OR_STATELESS_MARKERS_BOUND
DIGEST_DEPENDENCY_ORDER_BOUND_WITHOUT_DIGEST_CALCULATION
NO_IMPLEMENTATION_NO_REGISTRATION_NO_TEST_NO_EXECUTION
```

## Kanonische Wert- und Byteregel

Jeder spaetere S1-RJ-Digest muss ausschliesslich nach folgender Regel
entstehen:

1. Zulaessig sind nur `null`, Boolesche Werte, Strings, ganze Zahlen,
   endliche Binaer64-Zahlen, Listen und Objekte mit Stringschluesseln.
2. Negative numerische Null wird vor der Serialisierung auf positive
   `0.0` normalisiert.
3. Tupel und andere gebundene Sequenzen werden zu JSON-Listen.
4. Listen behalten die in diesem Vertrag festgelegte Reihenfolge.
5. Objektschluessel werden lexikografisch aufsteigend serialisiert.
6. JSON wird als UTF-8 mit ASCII-Escaping, ohne NaN oder Infinity, ohne
   Einrueckung und mit `,` beziehungsweise `:` als kompakten Trennern
   serialisiert.
7. Der Digest ist SHA-256 der exakten UTF-8-Bytes und wird als 64
   kleingeschriebene Hexzeichen dargestellt.

Das entspricht der bereits akzeptierten S1-JN-/S1-JT-Kanonisierung. Eine
andere Floatdarstellung, ein Zeilenumbruch am Dateiende oder eine dekorative
JSON-Formatierung gehoert nicht zum Digestpraeimage.

In den nachfolgenden Schemata bezeichnet `<...>` eine gebundene
Abhaengigkeit. Diese Schreibweise ist kein zu serialisierender String.
Vor einer spaeteren Digestberechnung muss jede Abhaengigkeit durch den exakt
zuvor berechneten Wert ersetzt sein.

## Digestabhaengigkeitsordnung

Die spaetere Materialisierung muss streng in dieser Reihenfolge erfolgen:

```text
01 edge_inventory_digest
02 physical_geometry_digest
03 outer_exposure_role_mapping_digest
04 public_fresh_projection_digest
05 private_fresh_state_digest je zustandsbehafteter Modellrolle
   oder exakte Zustandslosmarkierung je zustandsloser Modellrolle
```

Es gibt keine Rueckkante. Insbesondere darf ein Geometrie- oder
Kanteninventardigest keinen privaten Zustand, kein Rollenmapping und keinen
bereits davon abgeleiteten Frischdigest enthalten.

## Untergeordnetes Kanteninventar

Der Praeimagepayload fuer `edge_inventory_digest` besitzt exakt diese
Felder und Werte:

```json
{
  "schema_id": "mcm.s1rj.edge-inventory.4n.v1",
  "geometry_class": "FOUR_NODE_OPEN_LINE_S1PZ",
  "node_order": ["node-a", "node-b", "node-c", "node-d"],
  "edges": [
    {"first_node_id": "node-a", "second_node_id": "node-b"},
    {"first_node_id": "node-b", "second_node_id": "node-c"},
    {"first_node_id": "node-c", "second_node_id": "node-d"}
  ]
}
```

Die Endpunkte jeder Kante sind lexikografisch geordnet. Die Kantenliste ist
nach erstem und dann zweitem Endpunkt geordnet. Keine Selbstkante, keine
`node-a--node-d`-Kante und kein Richtungsduplikat ist zulaessig.

## Physische Geometrie

Der Praeimagepayload fuer `physical_geometry_digest` lautet strukturell
exakt:

```json
{
  "schema_id": "mcm.s1rj.physical-geometry.4n.v1",
  "geometry_class": "FOUR_NODE_OPEN_LINE_S1PZ",
  "field_id": "mcm.s1rf.field.4n",
  "layer_id": "mcm.s1rf.layer.4n",
  "geometry_id": "mcm.s1rf.geometry.4n",
  "modality_id": "technical-control",
  "sample_offsets": [[-1], [1]],
  "periodic_axes": [],
  "nodes": [
    {"node_id": "node-a", "position": [0]},
    {"node_id": "node-b", "position": [1]},
    {"node_id": "node-c", "position": [2]},
    {"node_id": "node-d", "position": [3]}
  ],
  "edge_inventory_digest": "<edge_inventory_digest>",
  "dock": {
    "dock_id": "dock.s1rf.technical-control.4n",
    "receptor_geometry_id": "mcm.s1rf.receptor.4n",
    "carrier_pairs": [
      ["carrier-a", "node-a"],
      ["carrier-b", "node-b"],
      ["carrier-c", "node-c"],
      ["carrier-d", "node-d"]
    ]
  }
}
```

Der Payload enthaelt keine A/B/C/D-Rollen, keine Modellrolle, keine
Expositionsreplik und keinen Feldwert. Der Modellkern darf spaeter nur
`physical_geometry_digest`, nicht den Rollenmappingdigest erhalten.

## Aeusseres Rollenmapping

Der Praeimagepayload fuer `outer_exposure_role_mapping_digest` lautet:

```json
{
  "schema_id": "mcm.s1rj.outer-exposure-role-mapping.4n.v1",
  "physical_geometry_digest": "<physical_geometry_digest>",
  "role_to_node": [
    ["B_LOCAL", "node-a"],
    ["A_FOCAL", "node-b"],
    ["D_CONTROL", "node-c"],
    ["C_REMOTE", "node-d"]
  ],
  "node_reflection_orbits": [
    ["node-a", "node-d"],
    ["node-b", "node-c"]
  ],
  "edge_reflection_orbits": [
    [["node-a", "node-b"], ["node-c", "node-d"]],
    [["node-b", "node-c"]]
  ]
}
```

Die Listenordnung ist Vertrag und keine Prioritaet. `D_CONTROL` bleibt eine
aeussere Kontrollgegenlage und ist weder Modellrolle noch vierte
Expositionsfamilie. Dieser Payload bleibt ausschliesslich im Orchestrator.

## Gemeinsame oeffentliche Frischprojektion

Der eine Praeimagepayload fuer `public_fresh_projection_digest` gilt
bitgleich fuer alle 14 Modellrollen und alle 16 Frischrepliken:

```json
{
  "schema_id": "mcm.s1rj.public-fresh-projection.4n.v1",
  "physical_geometry_digest": "<physical_geometry_digest>",
  "initial_field_tick": 0,
  "nodes": [
    {"node_id": "node-a", "S": 0.0, "H": 0.0, "perception_tick": 0, "receptor_contact": 0.0, "local_samples": []},
    {"node_id": "node-b", "S": 0.0, "H": 0.0, "perception_tick": 0, "receptor_contact": 0.0, "local_samples": []},
    {"node_id": "node-c", "S": 0.0, "H": 0.0, "perception_tick": 0, "receptor_contact": 0.0, "local_samples": []},
    {"node_id": "node-d", "S": 0.0, "H": 0.0, "perception_tick": 0, "receptor_contact": 0.0, "local_samples": []}
  ],
  "last_distribution": null
}
```

Der oeffentliche Projektionspayload enthaelt absichtlich keinen privaten
M-, L-, NORM-, Puffer-, Spur- oder Ressourcenstatus. Er enthaelt ebenfalls
keine Modell-, Replik-, Ereignis-, Rollenmapping- oder Ergebnisidentitaet.

`S` und `H` bezeichnen hier nur die vorhandenen technischen Feldkoordinaten.
Der Payload behauptet keine neue Feldfunktion.

## Gemeinsame private Huelle

Jeder zustandsbehaftete Privatpayload wird spaeter unter genau dieser Huelle
digestiert:

```json
{
  "schema_id": "mcm.s1rj.private-fresh-state.4n.v1",
  "model_role": "<exact-S1-RA-model-role>",
  "carry_class": "<exact-S1-QZ-carry-class>",
  "native_state_schema_id": "<role-specific-schema-id>",
  "configuration_binding": "<exact-accepted-configuration-digest-or-registration-digest>",
  "state_payload": "<role-specific-complete-state-payload>"
}
```

`configuration_binding` ist kein neuer Konfigurationsdigest. Er muss den
bereits akzeptierten rollenfesten S1-JT-, S1-QI-, S1-QQ-, S1-QV-, S1-QM-
oder DTS-1-Registrierungsbezug bytegenau uebernehmen. Ist dieser Bezug nicht
eindeutig aufloesbar, darf kein Privatdigest entstehen.

Die 16 Repliken derselben Modellrolle erhalten getrennte Objekte mit
identischem kanonischem Payload. Verschiedene Rollen teilen kein Objekt und
muessen nicht denselben Privatdigest besitzen.

## Zustandslose Rollen A0 und A1

Fuer diese zwei Rollen wird kein leerer Objektpayload erfunden und kein
privater Zustandsdigest vorgetaeuscht. Die exakten Markierungen lauten:

```text
A0_CURRENT_CONTACT -> STATELESS_MARKER:A0_CURRENT_CONTACT:S1RJ
A1_FAST_SH         -> FIELD_ONLY:A1_FAST_SH:S1RJ
```

A1 traegt S/H ausschliesslich im vollstaendigen Feld. Eine private H-Kopie
oder ein privater Nullvektor waere ungueltig.

## A2-B1-Fixed-Adapter

Fuer `A2_B1_FIXED_ADAPTER` gilt:

```text
carry_class            = OPAQUE_PRIVATE_STATE
native_state_schema_id = mcm.s1jt.b1-fixed-adapter.v1
configuration_binding  = existing S1_JT B1 configuration digest
```

`state_payload` lautet:

```json
{
  "backreaction_enabled": true,
  "base_rate_per_second": 1.0,
  "edge_inventory_digest": "<edge_inventory_digest>",
  "edge_rates": [
    {"first_node_id": "node-a", "second_node_id": "node-b", "rate_per_second": 1.1},
    {"first_node_id": "node-b", "second_node_id": "node-c", "rate_per_second": 1.1},
    {"first_node_id": "node-c", "second_node_id": "node-d", "rate_per_second": 1.1}
  ]
}
```

Die drei Raten stammen gemeinsam aus dem in S1-RI ausgewaehlten leitenden
Kantenbestand. B1 speichert weder freie noch refraktaere M4-Ressource.

## A2-B2-Integrator

Fuer `A2_B2_INTEGRATOR` gilt:

```text
carry_class            = OPAQUE_PRIVATE_STATE
native_state_schema_id = mcm.s1jt.b2-private-L.v1
configuration_binding  = existing S1_JT B2 configuration digest
```

`state_payload` lautet:

```json
{
  "entries": [
    {"node_id": "node-a", "value": 0.0},
    {"node_id": "node-b", "value": 0.0},
    {"node_id": "node-c", "value": 0.0},
    {"node_id": "node-d", "value": 0.0}
  ]
}
```

## A2-B3 bis A2-B6

Die vier Rollen verwenden dieselbe kanonische Massenordnung, aber getrennte
rollenfeste Arm- und Konfigurationsbindungen:

| Modellrolle | `arm_id` | `lambda_sm_per_second` | Zusatzbindung |
|---|---|---:|---|
| `A2_B3_LOCAL_LEAKY` | `mcm.s1jt.b3.local-leaky` | `1.0` | keine |
| `A2_B4_LINEAR_COUPLED` | `mcm.s1jt.b4.linear-coupled` | `1.0` | keine |
| `A2_B5_F3_FULL` | `mcm.s1jt.b5.full` | `1.0` | keine |
| `A2_B6_CONST_V` | `mcm.s1jt.b6.const-v` | `0.5` | bestehender S1-JT-B6-Spezifikationsdigest |

Je Rolle gilt:

```text
carry_class            = OPAQUE_PRIVATE_STATE
native_state_schema_id = mcm.s1rj.embedded-m-state.4n.v1
configuration_binding  = existing role-matching S1_JT configuration digest
```

Der vollstaendige `state_payload` lautet je Rolle mit dem tabellarischen
`arm_id` und `lambda_sm_per_second`:

```json
{
  "arm": {
    "arm_id": "<role-specific-arm-id>",
    "lambda_sm_per_second": "<role-specific-value>",
    "kappa": 0.5,
    "eta": 1.0,
    "initial_total_mass": 1.0
  },
  "masses": [
    {"node_id": "node-a", "mass": 0.25},
    {"node_id": "node-b", "mass": 0.25},
    {"node_id": "node-c", "mass": 0.25},
    {"node_id": "node-d", "mass": 0.25}
  ],
  "edge_inventory_digest": "<edge_inventory_digest>",
  "frozen_spec_digest_or_null": "<B6-existing-spec-digest-otherwise-null>"
}
```

Die in spitzen Klammern stehenden Werte werden vor der Serialisierung aus
der obigen Tabelle beziehungsweise dem bestehenden S1-JT-Beleg eingesetzt.
Bei B3 bis B5 ist `frozen_spec_digest_or_null` exakt `null`.

## A3-NORM

Fuer `A3_NORM` gilt:

```text
carry_class            = OPAQUE_PRIVATE_STATE
native_state_schema_id = w7n.local-baseline-state.norm.4n.v1
configuration_binding  = existing S1-QI NORM configuration digest
```

`state_payload` lautet:

```json
{"model_id": "norm", "latent": [0.0, 0.0, 0.0, 0.0]}
```

Nenner, Skalierungswert und vorheriger Output sind nicht Teil des
Frischzustands.

## M1-Parallel-Leak

Fuer `M1_PARALLEL_LEAK` gilt:

```text
carry_class            = OPAQUE_PRIVATE_STATE
native_state_schema_id = m1-parallel-leak-bank/s1qr.v1
configuration_binding  = existing S1-QQ registration digest
```

`state_payload` lautet:

```json
{
  "trace_order": ["FAST", "SLOW"],
  "fast_state": {"model_id": "leak", "latent": [0.0, 0.0, 0.0, 0.0]},
  "slow_state": {"model_id": "leak", "latent": [0.0, 0.0, 0.0, 0.0]}
}
```

Beide Nullspuren sind getrennte Objekte. Die Konfiguration behaelt die
gebundenen Zeitrollen `1.0` und `4.0` Sekunden sowie den gleichen
Punktmittel-Readout; diese Werte werden nicht in den Zustandsvektor kopiert.

## M2-Delay und M2-Replay

Beide Rollen verwenden getrennte private Objekte und dieselbe gebundene
Pufferkapazitaet `2`. Fuer beide gilt:

```text
carry_class            = OPAQUE_PRIVATE_STATE
native_state_schema_id = m2-bounded-buffer-state/s1qw.v1
configuration_binding  = existing S1-QV registration digest
```

`M2_DELAY` besitzt:

```json
{
  "mode_id": "DELAY",
  "geometry_digest": "<physical_geometry_digest>",
  "neuron_order": ["node-a", "node-b", "node-c", "node-d"],
  "records": [],
  "replay_phase": "NOT_APPLICABLE",
  "replay_cursor": 0
}
```

`M2_REPLAY` besitzt:

```json
{
  "mode_id": "REPLAY",
  "geometry_digest": "<physical_geometry_digest>",
  "neuron_order": ["node-a", "node-b", "node-c", "node-d"],
  "records": [],
  "replay_phase": "CAPTURE",
  "replay_cursor": 0
}
```

Der Frischzustand enthaelt keinen Dummyrecord und keine vorausgenommene
Quelle. Delay und Replay teilen weder Puffer noch Privatdigest.

## M4-DTS-1/T1

Fuer `M4_DTS1_T1` gilt:

```text
carry_class            = OPAQUE_THREE_ROLE_LEDGER
native_state_schema_id = mcm.s1rj.dts1-three-role-ledger.4n.v1
configuration_binding  = existing frozen DTS-1 configuration digest
```

`state_payload` lautet:

```json
{
  "edge_inventory_digest": "<edge_inventory_digest>",
  "node_capacities": [
    {"node_id": "node-a", "capacity": 1.0},
    {"node_id": "node-b", "capacity": 1.0},
    {"node_id": "node-c", "capacity": 1.0},
    {"node_id": "node-d", "capacity": 1.0}
  ],
  "edge_resources": [
    {"first_node_id": "node-a", "second_node_id": "node-b", "conductive_bound": 0.2, "refractory": 0.1},
    {"first_node_id": "node-b", "second_node_id": "node-c", "conductive_bound": 0.2, "refractory": 0.1},
    {"first_node_id": "node-c", "second_node_id": "node-d", "conductive_bound": 0.2, "refractory": 0.1}
  ],
  "rates": {"binding_rate": 0.4, "turnover_rate": 0.3, "recovery_rate": 0.2},
  "candidate_sidecar_digest_or_null": null
}
```

Freie Ressource, lokale Halbanteile und globale Summen werden nicht
gespeichert. Sie bleiben abgeleitete Validatorerwartungen aus S1-RI. T1 ist
nur die eingefrorene Ein-Kanten-Validierungsbaseline und erhaelt in diesem
Payload keinen zweiten dynamischen Zustand.

## M5-Direct

Fuer `M5_DIRECT` gilt:

```text
carry_class            = OPAQUE_PRIVATE_STATE
native_state_schema_id = w7n.local-baseline-state.leak.4n.v1
configuration_binding  = existing S1-QM M5 leak configuration digest
```

`state_payload` lautet:

```json
{"model_id": "leak", "latent": [0.0, 0.0, 0.0, 0.0]}
```

M5 besitzt genau eine lokale Retentionskoordinate je Ort. Keine zweite Spur,
kein Massenstatus und kein Puffer gehoeren in den Frischzustand.

## Vollstaendigkeitsmatrix

| Position | Modellrolle | Frischform |
|---:|---|---|
| 01 | `A0_CURRENT_CONTACT` | exakte Zustandslosmarkierung |
| 02 | `A1_FAST_SH` | exakte Feld-only-Markierung |
| 03 | `A2_B1_FIXED_ADAPTER` | Drei-Kanten-Fixed-Adapter |
| 04 | `A2_B2_INTEGRATOR` | vier L-Nullwerte |
| 05 | `A2_B3_LOCAL_LEAKY` | B3-M-Viertelmassen |
| 06 | `A2_B4_LINEAR_COUPLED` | B4-M-Viertelmassen |
| 07 | `A2_B5_F3_FULL` | B5-M-Viertelmassen |
| 08 | `A2_B6_CONST_V` | B6-M-Viertelmassen plus CONST-V-Bezug |
| 09 | `A3_NORM` | vier NORM-Nullwerte |
| 10 | `M1_PARALLEL_LEAK` | zwei getrennte Vier-Orte-Nullspuren |
| 11 | `M2_DELAY` | leerer DELAY-Puffer |
| 12 | `M2_REPLAY` | leerer REPLAY-Puffer |
| 13 | `M4_DTS1_T1` | Vier-Knoten-/Drei-Kanten-Dreirollenledger |
| 14 | `M5_DIRECT` | vier LEAK-Nullwerte |

Die Positionen sind ausschliesslich Serialisierungspositionen der S1-RA-
Modellachse. Sie sind keine Ausfuehrungsreihenfolge oder Wertung.

## Trennungs- und Gleichheitsregeln

Spaetere Materialisierung muss belegen:

- genau einen `edge_inventory_digest` fuer B1, B3-B6 und M4;
- genau einen `physical_geometry_digest` fuer alle 14 Rollen;
- genau einen `public_fresh_projection_digest` fuer alle 224 Pflichtzellen;
- genau 16 getrennte, payloadgleiche Privatinstanzen je zustandsbehafteter
  Modellrolle;
- die exakte Markierung statt Privatobjekt fuer A0 und A1;
- keine Gleichheitsforderung zwischen Privatdigests verschiedener Rollen;
- keinen Rollenmappingdigest im Modell- oder Privatpayload;
- keine Expositionsreplik im Feld- oder Privatfrischpayload.

Die globale M4-Bilanz `3.10 + 0.60 + 0.30 = 4.00` ist eine
Validierungsidentitaet und kein zusaetzliches Digestfeld.

## Fail-Closed-Regeln

S1-RJ wird verletzt, wenn spaeter:

- ein Schemafeld fehlt, hinzukommt oder umbenannt wird;
- eine gebundene Listenordnung sortiert, permutiert oder aus einem Mapping
  rekonstruiert wird;
- negative Null, NaN oder Infinity in einen Praeimagepayload gelangt;
- Rollenmapping und physische Geometrie in denselben Digest fallen;
- der oeffentliche Frischpayload einen privaten Zustand enthaelt;
- A0 oder A1 einen privaten Nullzustand erhalten;
- B1 und M4 verschiedene Kanteninventare oder leitende Quellen erhalten;
- B3-B6 andere als vier Viertelmassen erhalten;
- M1-Spuren, M2-Puffer oder Repliken dasselbe veraenderliche Objekt teilen;
- freie M4-Ressource gespeichert oder global doppelt gezaehlt wird;
- eine bestehende Konfigurationsbindung neu berechnet, retuned oder durch
  einen Platzhalterstring serialisiert wird;
- ein Digest vor vollstaendiger Aufloesung seiner Abhaengigkeiten entsteht;
- Registrierung, Implementierung oder Ausfuehrung vor dem spaeteren
  Materialisierungs- und Digestaudit beginnt.

## Paketstatus

```text
CANONICAL_PREIMAGE_SCHEMAS_BOUND
ALL_FOURTEEN_FRESH_ROLE_FORMS_CLOSED
DIGEST_VALUES_NOT_COMPUTED
CANONICAL_MANIFEST_NOT_MATERIALIZED
GEOMETRY_NOT_REGISTERED
FRESH_FACTORIES_NOT_IMPLEMENTED
MANDATORY_BASELINE_PACKAGE_NOT_EXECUTABLE
```

S1-RJ ist ein statischer Daten- und Provenienzvertrag. Er ist kein
dynamischer Befund und keine Aussage zu einer hypothetischen MCM-Memory.

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RK - statischer Materialisierungs-, Digestberechnungs- und
        Queridentitaetsaudit fuer das S1-RJ-Frischmanifest
```

S1-RK soll die gebundenen Praeimages ohne Runtime- oder Feldkernaufruf
materialisieren, alle Digests exakt einmal berechnen und die gemeinsamen
Geometrie-, Kanteninventar- und Frischidentitaeten querpruefen. Es darf noch
keine Produktionsgeometrie registrieren, keine Frischfabrik implementieren,
keine Matrixzelle ausfuehren und keine Ergebnisentscheidung treffen.
