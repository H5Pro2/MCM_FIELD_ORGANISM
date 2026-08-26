# S1-RM: Implementierung von Manifestconsumer und Vier-Knoten-Nullfeldfabrik

## Status und Umfang

S1-RM implementiert den in S1-RL gebundenen unveraenderlichen Consumer fuer
das S1-RK-Manifest und die gemeinsame oeffentliche Vier-Knoten-
Nullfeldfabrik. Zusaetzlich sind die fokussierten Consumer- und
Nullfeldtests definiert.

S1-RM implementiert keine rollenprivate Frischfabrik, keinen Adapter, keine
Gleichung und keinen Runner. Es wurde kein Test ausgefuehrt und kein
Feldschritt erzeugt.

Implementierungsstatus:

```text
S1RK_MANIFEST_CONSUMER_IMPLEMENTED
RECURSIVELY_IMMUTABLE_MANIFEST_VIEW_IMPLEMENTED
COMMON_FOUR_NODE_TICK_ZERO_FIELD_FACTORY_IMPLEMENTED
TEN_CONSUMER_AND_SIX_PUBLIC_FACTORY_TESTS_DEFINED
PRIVATE_ROLE_FACTORIES_NOT_IMPLEMENTED
NO_TEST_EXECUTION_NO_FIELD_ADVANCE_NO_MATRIX_CELL
```

## Geaenderte Produktionsdateien

### `mcm_field_organism/four_node_fresh_manifest.py`

Der Consumer:

- liest nur einen explizit uebergebenen `Path` und besitzt keine
  Importzeit-Dateioperation;
- lehnt ungueltiges UTF-8, ungueltiges JSON, doppelte Schluessel und
  unbekannte Rootfelder fail-closed ab;
- prueft Manifest-, Quellen- und Kanonisierungsidentitaet;
- reproduziert vier gemeinsame und zwoelf private Payloaddigests;
- prueft die zwei Zustandslosmarkierungen und die lueckenlose Rollenachse;
- prueft Kanten-, Geometrie- und Queridentitaetsabhaengigkeiten;
- reproduziert den registrierten Manifestdigest;
- gibt Dictionaries als `MappingProxyType` und Listen als Tupel aus.

Es existieren weder Cache noch Defaults, Reparaturpfad oder globale geladene
Manifestinstanz.

### `mcm_field_organism/four_node_fresh_factory.py`

Die Fabrik `build_four_node_public_fresh_field` baut aus der validierten
Manifestansicht:

- vier native `MCMNeuron`-Objekte in der Reihenfolge node-a bis node-d;
- einen nativen `MCMNeuronLayer` mit den Offsets `(-1,)` und `(1,)`;
- keine periodische Achse;
- einen verlustlosen Dock mit vier Carrier-Knoten-Paaren;
- `S=0.0`, `H=0.0`, Wahrnehmungstakt null und Rezeptorkontakt `0.0`;
- keine lokalen Samples, keine letzte Distribution, kein Substrat und keine
  Entwicklungsrolle.

Anschliessend wird die erzeugte oeffentliche Projektion erneut kanonisch
gebildet und gegen den registrierten Digest
`ce6912af2bc94458c2ba4243fa6df7b8b05494d956ef96730f4faf7ec5a8a879`
geprueft. `SharedMCMField.advance` wird nicht aufgerufen.

## Definierte Tests

`tests/test_four_node_fresh_manifest.py` enthaelt zehn Tests fuer:

- Annahme des registrierten Manifests;
- rekursive Unveraenderlichkeit;
- Nicht-Bytes, ungueltiges JSON und doppelte Schluessel;
- unbekannte Rootfelder und abweichende Schemaidentitaet;
- gemeinsame und private Digestabweichungen;
- Rollenachsen-, Abhaengigkeits- und Manifestdigestabweichungen.

`tests/test_four_node_fresh_factory.py` enthaelt sechs Tests fuer:

- Feld-, Geometrie-, Layer- und Knotenidentitaeten;
- exakte Nullprojektion bei Takt null;
- offene Drei-Kanten-Linie ohne Periodizitaet;
- verlustlosen registrierten Dock;
- getrennte Objektgraphen bei wiederholter Erzeugung;
- Ablehnung einer nicht validierten Manifesteingabe.

Diese Tests sind nur definiert. S1-RM fuehrt sie nicht aus.

## Statischer Grenzaudit

Der Quellenaudit bestaetigt:

- genau zwei neue Produktions- und zwei neue Testdateien;
- keine Aenderung an `current_api.py`, Paketexporten oder Altmodulen;
- keine Verwendung des historischen S1-JZ-Frischzustandsbauers;
- keine Funktion `build_four_node_role_fresh_bundle`;
- keinen Aufruf von `advance`;
- keine Materialisierung privater Modellzustaende;
- 16 definierte Tests innerhalb des S1-RL-Budgets von maximal 28.

Die S1-RL-Digestbruecke wird in S1-RM noch nicht benoetigt, weil kein
M-Substratzustand erzeugt wird. Beide Digestrollen bleiben unveraendert und
getrennt.

## Technische Aussagegrenze

S1-RM zeigt auf Implementierungsebene nur, wie das registrierte Manifest
gelesen und ein gemeinsames technisches Nullfeld konstruiert werden soll.
Ohne den noch gesperrten Testlauf liegt noch keine technische Abnahme dieser
Implementierung vor.

Insbesondere folgen daraus keine Aussage ueber Baselinefunktion,
Felddynamik, hypothetische MCM-Memory oder eine andere groessere Faehigkeit.

## Paketstatus

```text
S1RM_SOURCE_IMPLEMENTATION_COMPLETE
FOCUSED_TESTS_DEFINED_NOT_EXECUTED
COMMON_PUBLIC_FRESH_FIELD_NOT_YET_TEST_ACCEPTED
PRIVATE_ROLE_FACTORIES_NOT_IMPLEMENTED
BASELINE_ADAPTERS_NOT_CONNECTED
MANDATORY_224_CELL_PACKAGE_NOT_EXECUTABLE
```

## Genau ein naechster Schritt

Als einziger Anschluss ist zulaessig:

```text
S1-RN - fokussierte Ausfuehrung und technische Abnahme der zehn
        Manifestconsumer- und sechs Nullfeldfabriktests
```

S1-RN darf genau diese beiden Testmodule ausfuehren und die Ergebnisse
statisch protokollieren. Keine rollenprivate Fabrik, kein allgemeiner
Testbestand, kein Adapteranschluss, keine Matrixzelle und kein Feldlauf.
