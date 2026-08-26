# S1-NQ G2/D3 Validator-Implementierungs-, Fixture- und Testbudgetvertrag

## Status

S1-NQ bindet ausschliesslich die Implementierungsgrenze fuer den in S1-NP
definierten additiven D3-Einzelrecord- und Paarvalidator. Dateipfade, reine
APIs, positive kanonische Fixturebytes, negative Mutationen, erwartete
Digests und ein endliches Testbudget werden vorab geschlossen.

S1-NQ implementiert und fuehrt noch nichts aus. Admissibilitaetsfunktion,
Transfer- oder Bildungsgleichung, Runtime und Feldrueckwirkung bleiben
gesperrt.

Entscheidung:

```text
G2_D3_VALIDATOR_IMPLEMENTATION_FIXTURES_AND_TEST_BUDGET_BOUND
```

## Gebundene Dateigrenze

S1-NR darf genau drei neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/g2_d3_schema_validator.py` | reine D3-Record- und Paarvalidierung |
| `tests/g2_d3_s1nr_fixtures.py` | bytefeste positive Records und exakt gebundene Mutationen |
| `tests/test_g2_d3_s1nr_schema_validator.py` | fokussierte technische Abnahme |

Bestehende KFS-1-, T1-, DTS-1-, Feld-, Runner-, Audio-/Video- und
Runtimemodule duerfen nicht veraendert werden. Insbesondere bleibt
`mcm_field_organism/kfs1_schema_validator.py` unveraendert.

## Erlaubte Abhaengigkeit

Das neue Produktionsmodul darf aus dem bestehenden KFS-1-Validator nur
folgende zwei reinen Hilfsfunktionen importieren:

```text
canonical_json_bytes
sha256_hex
```

Alle D3-Schemafelder, Registryrollen, Fehlercodes und Belegtypen werden im
neuen additiven Modul definiert. Andere KFS-1- oder DTS-1-Typen duerfen nicht
importiert werden.

## Reine oeffentliche API

Das neue Modul darf genau diese oeffentlichen Funktionsrollen bereitstellen:

```text
build_g2_d3_validation_registry() -> G2D3ValidationRegistry

validate_g2_d3_anatomy_record(
    raw_bytes,
    registry,
) -> G2D3ValidationReceipt

validate_g2_d3_f1_pair(
    c0_raw_bytes,
    c1_raw_bytes,
    registry,
) -> G2D3PairValidationReceipt
```

Zusaetzlich sind nur unveraenderliche Datentypen fuer Registry und Belege
sowie Konstanten fuer Schema, Phasen und Fehlercodes oeffentlich zulaessig.
Interne Parsing-, Digest-, Projektions- und Ablationshilfen bleiben privat.

## Registryidentitaet

Die Registry bindet exakt:

```text
schema_id = g2_d3_anatomy_record
schema_version = s1np.v1
candidate_class_id = G2_CONSERVATIVE_BOUND_SUBPARTITION
primary_edge_id = edge:carrier-a:carrier-b
primary_carrier_a_id = carrier-a
primary_carrier_b_id = carrier-b
primary_geometry_digest = 26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651
identity_control_edge_id = edge:carrier-c:carrier-d
identity_control_carrier_a_id = carrier-c
identity_control_carrier_b_id = carrier-d
identity_control_geometry_digest = 75e06f6602eeb02fe90bd5aa72b1c67103a6bc4f0c7b2136611f4ef4945fa2f1
field_reference_digest = 8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835
validator_contract_digest = b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c
```

Der Vertragsdigest ist SHA-256 der ASCII-Kennung
`g2.d3.validator.contract.s1nq.v1`.

## Positive kanonische Fixturebytes

Die folgenden Zeilen sind die vollstaendigen UTF-8-Bytes ohne BOM und ohne
abschliessenden Zeilenumbruch.

### `D3_V_C0`

```json
{"aggregate_projection_digest":"bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e","anatomy_record_digest":"1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f","blocked":0.0,"bound_configured":0.0,"bound_unconfigured":0.5,"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,"carrier_a_id":"carrier-a","carrier_b_id":"carrier-b","edge_id":"edge:carrier-a:carrier-b","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","free":0.5,"geometry_digest":"26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651","resource_account_digest":"3421bacb4167e15f864c53b5fa9e2c15969a485906ebc5e1a47f24d3fd93994c","schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}
```

### `D3_V_C1`

```json
{"aggregate_projection_digest":"bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e","anatomy_record_digest":"3cf515292d1a8591ce1fdecf6f510dfc79cdf72d0fa64dcd965dca41859c3e8c","blocked":0.0,"bound_configured":0.5,"bound_unconfigured":0.0,"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,"carrier_a_id":"carrier-a","carrier_b_id":"carrier-b","edge_id":"edge:carrier-a:carrier-b","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","free":0.5,"geometry_digest":"26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651","resource_account_digest":"4abb521d1b2e0dbf93938493033e75f3c0da73643ec90bf3808f28d0241b017b","schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}
```

### `D3_V_MIXED`

```json
{"aggregate_projection_digest":"bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e","anatomy_record_digest":"d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c","blocked":0.0,"bound_configured":0.25,"bound_unconfigured":0.25,"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,"carrier_a_id":"carrier-a","carrier_b_id":"carrier-b","edge_id":"edge:carrier-a:carrier-b","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","free":0.5,"geometry_digest":"26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651","resource_account_digest":"75bee4f5732ed8c57c942c0e495b910c54097ef72ed1fb457740a4dd7045cd1c","schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}
```

## Positive Erwartungsdigests

| Fixture | Eingabebytes | D3-Ressource | Aggregatprojektion | Record |
|---|---|---|---|---|
| `D3_V_C0` | `d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7` | `3421bacb4167e15f864c53b5fa9e2c15969a485906ebc5e1a47f24d3fd93994c` | `bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e` | `1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f` |
| `D3_V_C1` | `058ae964682a9750a316d1db1b2e155714c18bc5adab9eb71fbc6e85e3be54b5` | `4abb521d1b2e0dbf93938493033e75f3c0da73643ec90bf3808f28d0241b017b` | `bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e` | `3cf515292d1a8591ce1fdecf6f510dfc79cdf72d0fa64dcd965dca41859c3e8c` |
| `D3_V_MIXED` | `2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8` | `75bee4f5732ed8c57c942c0e495b910c54097ef72ed1fb457740a4dd7045cd1c` | `bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e` | `d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c` |

Der gemeinsame Projektionsdigest ist die zentrale positive Paarerwartung.
Digestunterschiede der D3-Records sind nur Identitaetsunterschiede und kein
Funktionsbefund.

## Bytefeste Paar-Kontrollrecords

Zwei weitere einzeln gueltige Records sind ausschliesslich fuer negative
Paarpruefungen gebunden.

### `D3_V_C1_IDENTITY_CONTROL`

```json
{"aggregate_projection_digest":"9ae4547347667b0a8b8ae97708778d4211dd6548b1c58074aab8070c835cdcab","anatomy_record_digest":"1df1ef9eb25362084aa13e1d5f65a5270e6ea8d72175feea64b9d9b7ec0dccdb","blocked":0.0,"bound_configured":0.5,"bound_unconfigured":0.0,"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,"carrier_a_id":"carrier-c","carrier_b_id":"carrier-d","edge_id":"edge:carrier-c:carrier-d","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","free":0.5,"geometry_digest":"75e06f6602eeb02fe90bd5aa72b1c67103a6bc4f0c7b2136611f4ef4945fa2f1","resource_account_digest":"441d304e5c5f166b9abe036be04e4e82c2a95f8d0d504a1807cd00dedbdbaa08","schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}
```

Erwartungsdigests:

```text
input    d1ed106bb1224919e6a106f73bab80e2ead22e02d648d928bbc66ffe635a55b6
resource 441d304e5c5f166b9abe036be04e4e82c2a95f8d0d504a1807cd00dedbdbaa08
project  9ae4547347667b0a8b8ae97708778d4211dd6548b1c58074aab8070c835cdcab
record   1df1ef9eb25362084aa13e1d5f65a5270e6ea8d72175feea64b9d9b7ec0dccdb
```

### `D3_V_C1_AGGREGATE_CONTROL`

```json
{"aggregate_projection_digest":"82b2360b2b19e75263df1d796fbc65df5fd705b55eb7963615911aa3f5071016","anatomy_record_digest":"1e0eda146f07f281bccf408f73f1d6b7cbef52d7f2779700025591c6c73597c7","blocked":0.0,"bound_configured":0.75,"bound_unconfigured":0.0,"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,"carrier_a_id":"carrier-a","carrier_b_id":"carrier-b","edge_id":"edge:carrier-a:carrier-b","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","free":0.25,"geometry_digest":"26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651","resource_account_digest":"ff7c51e0909ac99d88940246117b10b87df0a097bba27dd326b1b41d3aa2dcb4","schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}
```

Erwartungsdigests:

```text
input    fb0267ce2697ee8e1c5dae3dff6b43c35817966e401f5edefb6935c7df8578f7
resource ff7c51e0909ac99d88940246117b10b87df0a097bba27dd326b1b41d3aa2dcb4
project  82b2360b2b19e75263df1d796fbc65df5fd705b55eb7963615911aa3f5071016
record   1e0eda146f07f281bccf408f73f1d6b7cbef52d7f2779700025591c6c73597c7
```

## Gebundene Einzelmutationen

Jedes negative Einzelrecordfixture wird aus `D3_V_C0` durch genau die
angegebene Mutation gebildet. Abhaengige Digests werden absichtlich nicht
repariert, sofern die Mutation nicht ausdruecklich einen Digest betrifft.

| ID | Mutation | Primaerer sicherer Code |
|---|---|---|
| `D3_I_VERSION` | `schema_version="s1np.v2"` | `D3_UNKNOWN_SCHEMA_OR_VERSION` |
| `D3_I_MISSING` | `candidate_class_id` entfernen | `D3_MISSING_OR_UNKNOWN_FIELD` |
| `D3_I_EXTRA` | `unknown_field=true` ergaenzen | `D3_MISSING_OR_UNKNOWN_FIELD` |
| `D3_I_FORBIDDEN` | `raw_data=[]` ergaenzen | `D3_FORBIDDEN_PAYLOAD_PRESENT` |
| `D3_I_SERIALIZATION` | positives Objekt eingerueckt serialisieren | `D3_NONCANONICAL_SERIALIZATION` |
| `D3_I_CLASS` | `candidate_class_id="OTHER"` | `D3_CLASS_ID_MISMATCH` |
| `D3_I_GEOMETRY` | `geometry_digest` durch SHA-256 von `wrong-geometry` ersetzen | `D3_EDGE_ID_GEOMETRY_MISMATCH` |
| `D3_I_EDGE` | `edge_id="edge:wrong"` | `D3_EDGE_ID_GEOMETRY_MISMATCH` |
| `D3_I_FIELD` | `field_reference_digest` durch SHA-256 von `wrong-field` ersetzen | `D3_FIELD_REFERENCE_MISMATCH` |
| `D3_I_NEGATIVE` | `free=-0.5` | `D3_NEGATIVE_OR_NONFINITE_RESOURCE_ROLE` |
| `D3_I_NONFINITE` | erstes `"free":0.5` bytegenau durch `"free":1e999` ersetzen | `D3_NEGATIVE_OR_NONFINITE_RESOURCE_ROLE` |
| `D3_I_BOOLEAN` | `free=true` | `D3_NEGATIVE_OR_NONFINITE_RESOURCE_ROLE` |
| `D3_I_NEGATIVE_ZERO` | `blocked=-0.0` | `D3_NONCANONICAL_SERIALIZATION` |
| `D3_I_CAPACITY` | `capacity=2.0` | `D3_CAPACITY_MISMATCH` |
| `D3_I_RESOURCE_DIGEST` | `resource_account_digest="000...000"` | `D3_RESOURCE_ACCOUNT_DIGEST_MISMATCH` |
| `D3_I_PROJECTION_DIGEST` | `aggregate_projection_digest="000...000"` | `D3_AGGREGATE_PROJECTION_DIGEST_MISMATCH` |
| `D3_I_RECORD_DIGEST` | `anatomy_record_digest="000...000"` | `D3_ANATOMY_RECORD_DIGEST_MISMATCH` |
| `D3_I_STORED_BOUND` | zusaetzliches Feld `bound=0.5` | `D3_MISSING_OR_UNKNOWN_FIELD` |

`"000...000"` bezeichnet exakt 64 ASCII-Nullzeichen. Die Tabelle bindet fuer
jede Einzelmutation genau den genannten Fehlercode. Digestpruefungen werden
nur ausgefuehrt, wenn alle fuer den jeweiligen Digest notwendigen vorherigen
Struktur-, Identitaets- und Ledgerpruefungen bestanden sind. Ein fehlerhafter
Ressourcen- oder Projektionsdigest sperrt den davon abhaengigen
Recorddigestvergleich. Dadurch entstehen keine bloss abgeleiteten
Folgefehler. Kein Fixture darf zur Bestaetigung des Validators nachtraeglich
angepasst werden.

## Gebundene Paarmutationen

Ausgangspunkt ist immer `(D3_V_C0,D3_V_C1)`.

| ID | Mutation | Exakte sortierte Fehlercodes |
|---|---|---|
| `D3_P_ARM_INVALID` | C1 durch `D3_I_RECORD_DIGEST` ersetzen | `D3_PAIR_RECORD_INVALID` |
| `D3_P_IDENTITY` | `D3_V_C1_IDENTITY_CONTROL` als C1 koppeln | `D3_PAIR_IDENTITY_MISMATCH` plus `D3_PAIR_AGGREGATE_MISMATCH` |
| `D3_P_C0_ROLE` | `D3_V_MIXED` als C0 einsetzen | `D3_ABLATION_MISMATCH`, `D3_C0_FIXTURE_MISMATCH` |
| `D3_P_C1_ROLE` | `D3_V_MIXED` als C1 einsetzen | `D3_C1_FIXTURE_MISMATCH` |
| `D3_P_AGGREGATE` | `D3_V_C1_AGGREGATE_CONTROL` als C1 koppeln | `D3_ABLATION_MISMATCH`, `D3_C1_FIXTURE_MISMATCH`, `D3_PAIR_AGGREGATE_MISMATCH` |
| `D3_P_ABLATION` | `(D3_V_MIXED,D3_V_C1)` koppeln | `D3_ABLATION_MISMATCH`, `D3_C0_FIXTURE_MISMATCH` |

Alle fuer die Paarmutationen erforderlichen Einzelrecords und Digests sind
damit vor der Implementierung bytegenau gebunden.

## Belegverhalten

Ungueltige Recordbytes liefern einen unveraenderlichen `invalid`-Beleg und
werfen keine fachliche Ausnahme. Nur ein falscher API-Typ oder eine
ungueltige Registryinstanz darf `TypeError` beziehungsweise `ValueError` vor
der Recordpruefung ausloesen; dabei entsteht kein Teilbeleg.

Der Paarvalidator darf nur mit zwei `bytes`-Objekten arbeiten. Ein ungueltiger
Arm fuehrt zu `D3_PAIR_RECORD_INVALID`; Einzelrecordfehler bleiben in den
getrennten Einzelbelegen reproduzierbar.

## Fokussierte Testmatrix

| Test-ID | Abnahme |
|---|---|
| `T01` | C0, C1 und MIXED sind einzeln gueltig und digeststabil |
| `T02` | C0/C1 ist als Paar gueltig, gleich projiziert und exakt ablatierbar |
| `T03` | alle 18 Einzelmutationen liefern ihre gebundenen sicheren Codes |
| `T04` | alle 6 Paarmutationen liefern ihre gebundenen sicheren Codes |
| `T05` | Fehlercodes sind sortiert, eindeutig und ohne erfundene Folgedefekte |
| `T06` | gleiche Bytes und Registry erzeugen bitgleiche Belege |
| `T07` | Eingabebytes und Registry bleiben unveraendert |
| `T08` | nichtkanonische Bytes und negative Null werden nicht normalisiert |
| `T09` | D3-Ressourcen-, Projektions-, Record- und Belegdigests bleiben getrennt |
| `T10` | Paarvalidator berechnet keine Admissibilitaet und fuehrt keinen Transfer aus |
| `T11` | Modul importiert nur Standardbibliothek und zwei erlaubte KFS-1-Helfer |
| `T12` | kein Feld-, Runner-, I/O-, Audio-/Video-, Browser- oder Netzwerkpfad ist erreichbar |

Die Tests verwenden ausschliesslich `unittest` aus der Standardbibliothek.

## Endliches S1-NR-Ausfuehrungsbudget

Die spaetere Implementierung darf genau einmal fokussiert ausgefuehrt werden:

```text
python -m unittest tests.test_g2_d3_s1nr_schema_validator
```

Innerhalb dieser Abnahme gelten maximal:

```text
validate_g2_d3_anatomy_record: 64 Aufrufe
validate_g2_d3_f1_pair:         16 Aufrufe
MCM-Feldschritte:                0
Runner-/Medien-/Netzwerkaufrufe: 0
Report- oder Dateischreibzugriffe: 0
```

Bei einem Testfehler werden Vertrag und Implementierung getrennt geprueft.
Werte, Fixtures oder erwartete Codes duerfen nicht anhand des Ergebnisses
passend gemacht werden.

## Aussagegrenze

S1-NQ bindet nur eine implementierbare Validatorgrenze. Es gibt noch keinen
Validatorbefund, keine G2-Admissibilitaetsfunktion, keine Dynamik, keine
Feldwirkung, keine Lernfunktion und keinen Befund zur hypothetischen
MCM-Memory.

## Naechster erlaubter Schritt

S1-NR darf ausschliesslich die drei gebundenen Dateien implementieren und den
fokussierten Test genau einmal innerhalb des Budgets ausfuehren. Danach werden
Quell-, Fixture- und Testdigests sowie der reine Validatorbefund dokumentiert.

Admissibilitaets-, Transfer-, Bildungs- und Feldmechanik bleiben gesperrt.
