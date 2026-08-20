# S1-PI G2/D3 endliche Bindungsangebots-Fixture, Payload, Digests und Baselineprovenienz

## Status und Umfang

S1-PI bindet ausschliesslich die endliche statische Ereignis- und
Messfixture aus S1-PH. Festgelegt werden ein dyadischer Angebotswert,
kanonische Exposure- und Payloadrecords, zwei identisch stammende externe
Baselinereplikate sowie alle zugehoerigen Digests.

S1-PI bindet keine Wirkungsgleichung, keine Kandidatennachzustaende und keine
Baselineantwort. Es gibt keine Implementierung, keinen Test und keinen Lauf.

Entscheidung:

```text
G2_D3_FINITE_FRESH_BINDING_OFFER_AND_BASELINE_PROVENANCE_BOUND
```

## Exakter Angebotswert

Verbindlich gilt:

```text
offer_amount = 0.375
```

Der Wert ist dyadisch (`3/8`) und damit binaer exakt. Gegen die in S1-PE
gebundenen freien Ressourcen gilt:

```text
free_BLOCKED_HELD = 0.25
free_FREE_AVAILABLE = 0.5

0.25 < 0.375 <= 0.5
```

Damit liegt ein unterscheidender Kapazitaetsfall vor. Daraus folgt noch nicht,
welche Menge ein spaeterer Operator tatsaechlich bindet.

## Gebundene externe Identitaeten

```text
neutral_intervention_boundary_id
= S1_PI_MODEL_NEUTRAL_INTERVENTION_BOUNDARY_V1

free_comparison_replica_id
= BASELINE_REPLICA_FREE_COMPARISON

blocked_comparison_replica_id
= BASELINE_REPLICA_BLOCKED_COMPARISON
```

Die Replikatkennungen existieren nur im externen Provenienzmanifest. Sie
duerfen nicht an einen Baselineoperator, Kandidatenrecord oder Ereignispayload
weitergegeben werden.

## Kanonischer gemeinsamer Expositionskern

```json
{"common_exposure_digest":"aa325bd855bf30a3691b2ba9b25f84fff0132bdf8a842255985dc009dab248e5","edge_id":"edge:carrier-a:carrier-b","event_id":"S1_PE_IDENTICAL_FRESH_BINDING_EVENT_V1","event_identity_digest":"b1253793c16b639cabae4fd15b5911885c79ccf93ff232945813fe21ec2428e4","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","neutral_intervention_boundary_id":"S1_PI_MODEL_NEUTRAL_INTERVENTION_BOUNDARY_V1","offer_amount":0.375,"schema_id":"g2_d3_common_binding_exposure_core","schema_version":"s1pi.v1"}
```

Der `common_exposure_digest` wird ueber den kanonischen Record ohne sein
eigenes Digestfeld berechnet. Der Kern enthaelt keine Armkennung,
Kandidatenressource oder Antwort.

## Kanonischer Ereignispayload

```json
{"common_exposure_digest":"aa325bd855bf30a3691b2ba9b25f84fff0132bdf8a842255985dc009dab248e5","edge_id":"edge:carrier-a:carrier-b","event_id":"S1_PE_IDENTICAL_FRESH_BINDING_EVENT_V1","event_identity_digest":"b1253793c16b639cabae4fd15b5911885c79ccf93ff232945813fe21ec2428e4","event_role":"FRESH_LOCAL_BINDING_OFFER","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","offer_amount":0.375,"payload_digest":"04135ee988060079554b117adf87099d3eeab6d9643ef3b415c05de86a9349da","schema_id":"g2_d3_fresh_binding_event_payload","schema_version":"s1pi.v1","source_role":"free","target_role":"bound_unconfigured"}
```

Diese Payloadbytes muessen spaeter byteidentisch an beide Kandidatenarme
gehen. Eine Baseline darf nur ueber einen noch zu bindenden modellneutralen
Adapter exponiert werden; der Adapter darf weder Arm- noch
Kandidatenzustandsinformation hinzufuegen.

## Kanonischer gemeinsamer Baselineursprung

Die primaere Gegenbaseline bleibt die bereits implementierte Klasse
`G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE`. S1-PI registriert nur ihren
vorhandenen Start- und Konfigurationsursprung:

```json
{"baseline_class_id":"G2_D3_MATCHED_SINGLE_STATE_RETENTION_BASELINE","baseline_configuration_input_bytes_digest":"12e6d381c0dcc0f170c39453bde291152bc55499e0292edacb2d0a09c27e1d93","baseline_contract_digest":"18ea29690ef7e62ae086c93b43dc3678f8ad5fed81aa1a0fde24983649d6f036","baseline_initial_state_input_bytes_digest":"f67406ef5f4da6ecd3775ab8c12139dbee607dd33b0c89e14842774c48d0ffd2","common_exposure_digest":"aa325bd855bf30a3691b2ba9b25f84fff0132bdf8a842255985dc009dab248e5","neutral_intervention_boundary_id":"S1_PI_MODEL_NEUTRAL_INTERVENTION_BOUNDARY_V1","replica_origin_digest":"2b2e8ec75aad474fcddf756665a29c71b20095d78ab67569f3ef0c8186330921","schema_id":"g2_d3_binding_baseline_replica_origin","schema_version":"s1pi.v1"}
```

Beide spaeteren Replikate muessen von genau diesen byteidentischen
Start-/Konfigurationsbytes und demselben Ursprungsrecord abgeleitet werden.

## Externes Baseline-Provenienzmanifest

```json
{"blocked_comparison_origin_digest":"2b2e8ec75aad474fcddf756665a29c71b20095d78ab67569f3ef0c8186330921","blocked_comparison_replica_id":"BASELINE_REPLICA_BLOCKED_COMPARISON","candidate_state_exposure":false,"common_exposure_digest":"aa325bd855bf30a3691b2ba9b25f84fff0132bdf8a842255985dc009dab248e5","event_adapter_status":"UNBOUND","event_payload_digest":"04135ee988060079554b117adf87099d3eeab6d9643ef3b415c05de86a9349da","free_comparison_origin_digest":"2b2e8ec75aad474fcddf756665a29c71b20095d78ab67569f3ef0c8186330921","free_comparison_replica_id":"BASELINE_REPLICA_FREE_COMPARISON","o3_exposure":false,"provenance_digest":"969ce834d238f49a66c02d5d5ea654dfdb60457ecd74061f14d59938bdb1cad0","schema_id":"g2_d3_binding_baseline_replica_provenance","schema_version":"s1pi.v1"}
```

`event_adapter_status = UNBOUND` ist eine harte Ausfuehrungssperre. Der
vorhandene Retentionsbaselineoperator akzeptiert den neuen S1-PI-Payload
nicht direkt. S1-PI repariert oder umgeht diese Schnittstellengrenze nicht.

## Digestregeln und erwartete Werte

Alle Records sind kompaktes kanonisches UTF-8-JSON mit sortierten
Schluesseln. Der jeweilige Eigendigest ist SHA-256 ueber den Record ohne sein
eigenes Digestfeld. Der Inputbytes-Digest umfasst danach den vollstaendigen
kanonischen Record.

| Record | Eigendigest | Inputbytes-Digest |
|---|---|---|
| gemeinsamer Expositionskern | `aa325bd855bf30a3691b2ba9b25f84fff0132bdf8a842255985dc009dab248e5` | `34c4198379098e40e507a4ec771e1c134859e10f8ea1636dbae227dd2a649fbc` |
| Ereignispayload | `04135ee988060079554b117adf87099d3eeab6d9643ef3b415c05de86a9349da` | `320fd5409142c79b494523401e898f082592b2925b56c6910a478c35f8e546a2` |
| Baselineursprung | `2b2e8ec75aad474fcddf756665a29c71b20095d78ab67569f3ef0c8186330921` | `e4e55d770ffd05c840297257047499d662247d8483396bb94a3353dffb1437d8` |
| Provenienzmanifest | `969ce834d238f49a66c02d5d5ea654dfdb60457ecd74061f14d59938bdb1cad0` | `d42a9593275a8c83d5162b2d99182df7e45dda6f270575b38d248a56cd10e495` |

## Rein statische Messgrenzen

Ohne eine Wirkungsgleichung sind nur folgende Grenzen zulaessig:

```text
0.0 <= committed_FREE_AVAILABLE <= 0.375
0.0 <= committed_BLOCKED_HELD <= 0.25
```

Die Grenzen folgen ausschliesslich aus Angebot und verfuegbarer freier
Ressource. Sie binden keine tatsaechlichen Commitwerte und keine
Kandidatennachzustaende.

Der Baselinekontrast bleibt als Prognose null, darf aber vor einem gebundenen
Ereignisadapter und zwei vollstaendigen Baselineergebnissen nicht berechnet
oder behauptet werden.

## Statische Gueltigkeitsbedingungen

Die Fixture ist nur gueltig, wenn:

- alle vier Records kanonisch und digestkorrekt sind;
- `offer_amount` in Expositionskern und Payload exakt `0.375` ist;
- Ereignis-, Kanten- und Feldreferenzen uebereinstimmen;
- beide Baselineursprungsdigests exakt gleich sind;
- beide Replikatkennungen verschieden und rein extern bleiben;
- `candidate_state_exposure` und `o3_exposure` exakt `false` sind;
- `event_adapter_status` exakt `UNBOUND` bleibt.

Ein gebundener oder stillschweigend angenommener Adapter waere in S1-PI
ungueltig, nicht fortgeschritten.

## Aussagegrenze

S1-PI bindet nur endliche Expositions- und Provenienzbytes. Es gibt noch
keine Kandidaten- oder Baselineantwort. Die hypothetische MCM-Memory bleibt
eine Entwicklungsrichtung.

## Naechster erlaubter Schritt

S1-PJ darf ausschliesslich die lokale konservative Bindungsgleichung, den
modellneutralen Baseline-Ereignisadapter und die exakten Vorabprognosen fuer
Kandidatennachzustaende, Commitkontrast und Baselinekontrast binden.
Implementierung, Test, Feldintegration und Lauf bleiben gesperrt.
