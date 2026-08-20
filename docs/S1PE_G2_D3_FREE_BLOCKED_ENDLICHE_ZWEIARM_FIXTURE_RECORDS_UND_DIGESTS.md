# S1-PE G2/D3 Free/Blocked endliche Zweiarm-Fixture, Records und Digests

## Status und Umfang

S1-PE bindet ausschliesslich die endliche statische Fixture der in S1-PD
festgelegten Zweiarm-Intervention. Gebunden werden dyadische Ressourcenwerte,
IDs, drei D3-Anatomierecords, eine noch inhaltsfreie Ereignisidentitaet, ein
externer Fixturemanifest und deren Digests.

S1-PE fuehrt keine Wirkungsgleichung, Bindungsdynamik, Implementierung, Tests
oder Ausfuehrung ein. Das frische Bindungsereignis besitzt in diesem Schritt
ausdruecklich noch keinen Payload.

Entscheidung:

```text
G2_D3_FREE_BLOCKED_FINITE_PAIRED_FIXTURE_BOUND
```

## Gebundene Identitaeten

```text
fixture_id = S1_PE_G2_D3_FREE_BLOCKED_PAIR_V1
causal_source_id = REGISTERED_EXTERNAL_TEST_INTERVENTION
free_available_arm_id = FREE_AVAILABLE
blocked_held_arm_id = BLOCKED_HELD
fresh_event_id = S1_PE_IDENTICAL_FRESH_BINDING_EVENT_V1
```

Arm- und Fixture-IDs gehoeren nur zum externen Beobachter- und
Validierungsrahmen. Sie werden nicht in einem D3-Anatomierecord gespeichert
und duerfen spaeter nicht zum Kandidateneingang werden.

## Exakte dyadische Ressourcenauswahl

Alle Werte sind ganzzahlige Vielfache von `1/8` und damit in binaerer
Gleitkommadarstellung exakt:

| Rolle | Vorzustand | `FREE_AVAILABLE` | `BLOCKED_HELD` |
|---|---:|---:|---:|
| `capacity` | `1.0` | `1.0` | `1.0` |
| `free` | `0.375` | `0.5` | `0.25` |
| `bound_unconfigured` | `0.25` | `0.25` | `0.25` |
| `bound_configured` | `0.25` | `0.25` | `0.25` |
| `blocked` | `0.125` | `0.0` | `0.25` |

Der fuer beide Richtungen identische Umbuchungsbetrag ist:

```text
transfer_amount = 0.125
```

Damit gilt exakt:

```text
FREE_AVAILABLE: blocked -> free
0.125 -> 0.0
0.375 -> 0.5

BLOCKED_HELD: free -> blocked
0.375 -> 0.25
0.125 -> 0.25
```

Die leitende Bindung bleibt in beiden Armen `0.5`. Es gibt keine Rundung,
kein Clipping und keine Normalisierung.

## Kanonische D3-Records

Alle drei Records verwenden unveraendert das vorhandene Schema
`g2_d3_anatomy_record / s1np.v1`, dieselbe Kante, Geometrie und
Feldreferenz.

### Gemeinsamer Vorzustand

```json
{"aggregate_projection_digest":"3db12bc8f737c9a5fa9339697a5a5373ca923d2794063793a072964a97a5e5ab","anatomy_record_digest":"585a00a9b8cd1af79ef59989271c5ab5c1fed3e30f1d965de86043a9ea715f6a","blocked":0.125,"bound_configured":0.25,"bound_unconfigured":0.25,"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,"carrier_a_id":"carrier-a","carrier_b_id":"carrier-b","edge_id":"edge:carrier-a:carrier-b","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","free":0.375,"geometry_digest":"26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651","resource_account_digest":"d91dc46e35fec94622e52bda5d482bdbeb34fc37c97a7745e55c5f6396e4713e","schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}
```

### Nachzustand `FREE_AVAILABLE`

```json
{"aggregate_projection_digest":"bcce82a9527d3c3e4ef85a826b73e3dd3ec01f1ba885453a63ccf8ac9bae4b5e","anatomy_record_digest":"d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c","blocked":0.0,"bound_configured":0.25,"bound_unconfigured":0.25,"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,"carrier_a_id":"carrier-a","carrier_b_id":"carrier-b","edge_id":"edge:carrier-a:carrier-b","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","free":0.5,"geometry_digest":"26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651","resource_account_digest":"75bee4f5732ed8c57c942c0e495b910c54097ef72ed1fb457740a4dd7045cd1c","schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}
```

Dieser Record ist byteidentisch zum bereits gebundenen gueltigen
`D3_V_MIXED`-Fixture. Er wird nicht dupliziert oder uminterpretiert.

### Nachzustand `BLOCKED_HELD`

```json
{"aggregate_projection_digest":"707f0997b24d49c604872f01630479e0b6c5d85264e304ad637b98d141fc4607","anatomy_record_digest":"4bd692e489c6c9a217e5790abb0970d279fa367c7024b2119db6342e3f5d66e9","blocked":0.25,"bound_configured":0.25,"bound_unconfigured":0.25,"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,"carrier_a_id":"carrier-a","carrier_b_id":"carrier-b","edge_id":"edge:carrier-a:carrier-b","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","free":0.25,"geometry_digest":"26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651","resource_account_digest":"f473d9db55a71beb3eb5cb629d0e1e52e2610a473b73ea8eb4fb0d75f5721a59","schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}
```

## Frische Ereignisidentitaet

Der Ereignisrecord bindet nur die spaetere gemeinsame Exposition. Der Wert
`UNBOUND` sperrt jede Ausfuehrung, bis ein eigener Vertrag den
modellneutralen Payload festlegt.

```json
{"event_id":"S1_PE_IDENTICAL_FRESH_BINDING_EVENT_V1","event_identity_digest":"b1253793c16b639cabae4fd15b5911885c79ccf93ff232945813fe21ec2428e4","event_payload_status":"UNBOUND","event_role":"IDENTICAL_FRESH_LOCAL_BINDING","exposure_scope":"CANDIDATE_ARMS_AND_REGISTERED_BASELINES","schema_id":"g2_d3_fresh_binding_event_identity","schema_version":"s1pe.v1"}
```

Diese Identitaet enthaelt keine Bindungsmenge, Rate, Schwelle, Armkennung
oder Kandidatenressource.

## Externer Fixturemanifest

Der Manifest bleibt ausserhalb des Kandidatenpfads:

```json
{"blocked_held_arm_id":"BLOCKED_HELD","blocked_held_post_record_digest":"4bd692e489c6c9a217e5790abb0970d279fa367c7024b2119db6342e3f5d66e9","candidate_metadata_exposure":false,"causal_source_id":"REGISTERED_EXTERNAL_TEST_INTERVENTION","common_prestate_record_digest":"585a00a9b8cd1af79ef59989271c5ab5c1fed3e30f1d965de86043a9ea715f6a","fixture_digest":"76a619cce91fb923080a3746b4cd9b29b46ee8cbbb3fc73a273496bab93553e0","fixture_id":"S1_PE_G2_D3_FREE_BLOCKED_PAIR_V1","free_available_arm_id":"FREE_AVAILABLE","free_available_post_record_digest":"d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c","fresh_event_identity_digest":"b1253793c16b639cabae4fd15b5911885c79ccf93ff232945813fe21ec2428e4","schema_id":"g2_d3_free_blocked_intervention_fixture","schema_version":"s1pe.v1","transfer_amount":0.125}
```

## Digestregeln und erwartete Digests

Alle Records werden als kompaktes UTF-8-JSON mit sortierten Schluesseln,
ohne Leerraum und ohne nicht endliche Zahlen kanonisiert. Hashfunktion ist
SHA-256 in kleingeschriebener Hexdarstellung.

Fuer D3-Anatomierecords gelten unveraendert die bestehenden Regeln:

- `resource_account_digest`: kanonisch ueber `edge_id`, `capacity`, `free`,
  `bound_unconfigured`, `bound_configured`, `blocked`;
- `aggregate_projection_digest`: kanonisch ueber `edge_id`, `capacity`,
  `free`, den abgeleiteten Gesamtwert `bound` und `blocked`;
- `anatomy_record_digest`: kanonischer Gesamtpayload ohne
  `anatomy_record_digest`;
- Inputbytes-Digest: SHA-256 ueber den vollstaendigen kanonischen Record.

Fuer Ereignis und Manifest wird der jeweilige Eigendigest ueber den
kanonischen Payload ohne sein eigenes Digestfeld berechnet. Der
Inputbytes-Digest umfasst anschliessend den vollstaendigen Record.

| Record | Eigendigest | Inputbytes-Digest |
|---|---|---|
| Vorzustand | `585a00a9b8cd1af79ef59989271c5ab5c1fed3e30f1d965de86043a9ea715f6a` | `47e65ce1b4f0a7a42dce13222cfb6e29a91b226c8b9ed479ccd3d9eb3539eff6` |
| `FREE_AVAILABLE` | `d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c` | `2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8` |
| `BLOCKED_HELD` | `4bd692e489c6c9a217e5790abb0970d279fa367c7024b2119db6342e3f5d66e9` | `f9a43177383df5f900faf9020f6aa76e10b0898cdf527d21d1f0e2a93bbd4025` |
| Ereignisidentitaet | `b1253793c16b639cabae4fd15b5911885c79ccf93ff232945813fe21ec2428e4` | `82996574d1de2b09953188332b6a81a6ea549a7406e3a39c0ba31c164b49acf7` |
| Fixturemanifest | `76a619cce91fb923080a3746b4cd9b29b46ee8cbbb3fc73a273496bab93553e0` | `a1af0a6336cd3911f4b3e2cae03e8af0de1a0a3d4cd3a8967dbb9fe33d1650c6` |

## Erwartete statische Abnahme

Eine spaetere reine Fixturevalidierung muss vor jeder Dynamik exakt ergeben:

```text
PRESTATE_VALID
FREE_AVAILABLE_POSTSTATE_VALID
BLOCKED_HELD_POSTSTATE_VALID
PAIR_TRANSFER_EXACT
PAIR_CONTROLS_IDENTICAL
CANDIDATE_METADATA_EXPOSURE_FALSE
FRESH_EVENT_PAYLOAD_UNBOUND
```

Der vorhandene Einzeldatensatzvalidator kann die drei D3-Records spaeter
gegen `s1np.v1` pruefen. Der vorhandene F1-Paarvalidator darf nicht verwendet
werden: Er ist absichtlich auf C0/C1, identische Aggregatprojektionen und die
G2-Ablation begrenzt. Die S1-PE-Arme besitzen dagegen verschiedene
`free`/`blocked`-Aggregatprojektionen.

## Aussagegrenze

S1-PE bindet nur reproduzierbare Fixturebytes. Die Werte sind technische
Pruefwerte und keine Materialparameter. Es gibt noch keine gemessene
Kandidatenwirkung. Die hypothetische MCM-Memory bleibt eine
Entwicklungsrichtung.

## Naechster erlaubter Schritt

S1-PF darf ausschliesslich den statischen Implementierungs-, Validator-,
Fehlermutations- und Testbudgetvertrag fuer diese Fixture binden. Er muss den
bestehenden D3-Einzeldatensatzvalidator wiederverwenden und einen getrennten
Interventionspaarvalidator vorsehen. Implementierung, Wirkungsgleichung,
Bindungsdynamik und Ausfuehrung bleiben gesperrt.
