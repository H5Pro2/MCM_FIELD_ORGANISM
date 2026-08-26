# S1-PJ G2/D3 konservative Bindungsgleichung, Baselineadapter und exakte Vorabprognose

## Status und Umfang

S1-PJ bindet ausschliesslich die kleinste lokale Bindungsgleichung fuer das
S1-PI-Angebot, einen statischen modellneutralen Adapter zur vorhandenen
Retentionsbaseline und die exakten Vorabprognosen. Der Schritt legt
Kandidatennachrecords und beide gerichteten Kontraste fest.

S1-PJ implementiert nichts und fuehrt keinen Test oder Lauf aus. O3-, Feld-,
Runtime- und Medienpfad bleiben gesperrt.

Entscheidung:

```text
G2_D3_CONSERVATIVE_MAXIMAL_BINDING_AND_BASELINE_CONTRAST_PREDICTED
```

## Lokale konservative Bindungsgleichung

Fuer einen vollstaendig gueltigen D3-Vorzustand und den gueltigen
S1-PI-Ereignispayload gilt exakt:

```text
commit_amount = min(offer_amount, pre.free)

post.free = pre.free - commit_amount
post.bound_unconfigured = pre.bound_unconfigured + commit_amount
post.bound_configured = pre.bound_configured
post.blocked = pre.blocked
post.capacity = pre.capacity
```

`commit_amount` muss endlich und nichtnegativ sein. `offer_amount` muss
positiv und endlich sein. Vorzustand, Ereignispayload, Kante und
Feldreferenz muessen vor der Berechnung vollstaendig gueltig sein.

`min` ist die vorregistrierte Sattigungsgrenze zwischen endlichem Angebot und
endlicher freier Ressource. Sie ist kein nachtraegliches Clipping und keine
Reparatur eines ungueltigen Zustands. Ungueltige Eingaben erzeugen keinen
Nachzustand.

Der Nachzustand wird nur nach vollstaendiger Berechnung und Validierung
atomar angenommen. Ein partieller Rollencommit ist verboten.

## Kanonischer Gleichungsvertrag

```json
{"amount_rule_id":"MIN_OFFER_AND_PRE_FREE","atomic_commit_required":true,"equation_contract_digest":"ae19f42cf9b35e4bfc3429976388c75d01b2128b91b686875edfbd76e46f5ecb","event_payload_digest":"04135ee988060079554b117adf87099d3eeab6d9643ef3b415c05de86a9349da","offer_amount":0.375,"operator_id":"G2_D3_CONSERVATIVE_MAXIMAL_LOCAL_BINDING","schema_id":"g2_d3_local_binding_equation_contract","schema_version":"s1pj.v1","source_role":"free","target_role":"bound_unconfigured","unchanged_roles":["capacity","bound_configured","blocked"]}
```

## Exakte Kandidatenprognose

### `FREE_AVAILABLE`

Vorzustand:

```text
(free, bound_unconfigured, bound_configured, blocked)
= (0.5, 0.25, 0.25, 0.0)
```

Vorabprognose:

```text
commit_amount = min(0.375, 0.5) = 0.375
post = (0.125, 0.625, 0.25, 0.0)
```

Kanonischer Nachrecord:

```json
{"aggregate_projection_digest":"30fb1640be5e0bcf50f7048ddd345e5b85dd51f3d957e4141c159cc2ab2bac85","anatomy_record_digest":"e4f0c95e59ea37aa9db8ae25688ec5f28a700dcbaa76ba5bd2056b4eaac42804","blocked":0.0,"bound_configured":0.25,"bound_unconfigured":0.625,"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,"carrier_a_id":"carrier-a","carrier_b_id":"carrier-b","edge_id":"edge:carrier-a:carrier-b","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","free":0.125,"geometry_digest":"26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651","resource_account_digest":"0fc6e14290c7f3e4df23edbd02d61952a2f939def54fea4dd56cbf3186675578","schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}
```

### `BLOCKED_HELD`

Vorzustand:

```text
(free, bound_unconfigured, bound_configured, blocked)
= (0.25, 0.25, 0.25, 0.25)
```

Vorabprognose:

```text
commit_amount = min(0.375, 0.25) = 0.25
post = (0.0, 0.5, 0.25, 0.25)
```

Kanonischer Nachrecord:

```json
{"aggregate_projection_digest":"b4d35fdb8d8ee864092b37c8ca36157dcbc84d0939128b89a3b490e466e269f9","anatomy_record_digest":"c3874e3b342a62c5f9366938eded9c60cb3c38356aa8be9155cd6855a126645c","blocked":0.25,"bound_configured":0.25,"bound_unconfigured":0.5,"candidate_class_id":"G2_CONSERVATIVE_BOUND_SUBPARTITION","capacity":1.0,"carrier_a_id":"carrier-a","carrier_b_id":"carrier-b","edge_id":"edge:carrier-a:carrier-b","field_reference_digest":"8f189f31bd6fc92753311d3c4e4bcb29921429107728971226c48718ef410835","free":0.0,"geometry_digest":"26469bd04ca523a797d18b2fb31b6b2a1ba99e4d27d4936e56a5c2fe6737e651","resource_account_digest":"88fb527d8ec392fc9cdfaf5d28ebc7b5d0a0a20b8df1cb95a72034ce67ca252d","schema_id":"g2_d3_anatomy_record","schema_version":"s1np.v1"}
```

Damit lautet die exakte Kandidatenprognose:

```text
candidate_binding_contrast = 0.375 - 0.25 = 0.125
```

## Modellneutraler Baseline-Ereignisadapter

Der Adapter darf aus dem S1-PI-Payload nur das Vorliegen genau eines
gueltigen frischen Ereignisses ableiten. Er verwirft Angebotswert, Kante und
Feldreferenz fuer die Retentionsbaseline, weil deren vorhandene Schnittstelle
nur einen modellneutralen Fortsetzungstoken akzeptiert. Armkennung,
Kandidatenzustand und O3 stehen dem Adapter nicht zur Verfuegung.

Sein einzig zulaessiger Output sind die bereits gebundenen kanonischen Bytes:

```json
{"event_class_id":"G2_D3_FRESH_CONTINUATION","event_schema_id":"g2_d3_model_neutral_continuation_event","event_schema_version":"s1oy.v1"}
```

Inputbytes-Digest:

```text
dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f
```

Kanonischer Adaptervertrag:

```json
{"adapter_digest":"7a42352262636bf6dc851095814a1bc6be35c692eb21300e72a13678f4ae3c75","adapter_id":"S1_PJ_BINDING_OFFER_TO_RETENTION_CONTINUATION_V1","adapter_status":"BOUND_STATIC_NOT_IMPLEMENTED","projection_rule_id":"EVENT_OCCURRENCE_ONLY_NO_ARM_OR_CANDIDATE_STATE","schema_id":"g2_d3_binding_offer_retention_event_adapter","schema_version":"s1pj.v1","source_event_payload_digest":"04135ee988060079554b117adf87099d3eeab6d9643ef3b415c05de86a9349da","source_event_role":"FRESH_LOCAL_BINDING_OFFER","target_event_class_id":"G2_D3_FRESH_CONTINUATION","target_event_input_bytes_digest":"dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f","target_event_schema_id":"g2_d3_model_neutral_continuation_event","target_event_schema_version":"s1oy.v1"}
```

Der Adapter ist statisch gebunden, aber nicht implementiert. Die Abbildung
des Ereignisses erlaubt nur einen Replikatkontrast. Weil die
Retentionsbaseline den Angebotswert nicht modelliert, darf ihr absoluter
Antwortwert nicht gegen die absolute Kandidatenbindung als
Modellgleichwertigkeit interpretiert werden.

## Exakte Baseline-Gegenprognose

Beide Baselinereplikate verwenden exakt:

```text
chain_role = OP_CHAIN_XXX
first_boundary_input_digest
= c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c
second_boundary_input_digest
= 6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a
initial_state = 0.5
retention_fraction = 0.5
adapter_output_digest
= dbffc12bef77155c2271d3990ebe1b8ae4d481ce6155bf8716b1f6e19128b30f
```

Der Vergleichswert ist ausschliesslich der erste vorhandene Baselineschritt:

```text
cp0 = 0.5
cp1 = 0.25
baseline_first_step_response = cp0 - cp1 = 0.25
```

Beide Replikate muessen exakt dieselbe Antwort `0.25` liefern. Damit gilt:

```text
baseline_replica_contrast = 0.25 - 0.25 = 0.0
```

Der vorhandene Baselineoperator berechnet technisch auch `cp2 = 0.125`.
Dieser zweite Checkpoint ist fuer S1-PJ ausgeschlossen: Er darf weder in den
Replikatkontrast noch in den Kandidatenvergleich oder eine Entscheidung
eingehen.

## Kanonische Gesamtprognose

```json
{"adapter_digest":"7a42352262636bf6dc851095814a1bc6be35c692eb21300e72a13678f4ae3c75","baseline_chain_role":"OP_CHAIN_XXX","baseline_cp0_value":0.5,"baseline_cp1_value":0.25,"baseline_first_boundary_input_digest":"c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c","baseline_first_step_response":0.25,"baseline_replica_contrast":0.0,"baseline_second_boundary_input_digest":"6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a","blocked_held_commit":0.25,"blocked_held_post_record_digest":"c3874e3b342a62c5f9366938eded9c60cb3c38356aa8be9155cd6855a126645c","blocked_held_pre_record_digest":"4bd692e489c6c9a217e5790abb0970d279fa367c7024b2119db6342e3f5d66e9","candidate_binding_contrast":0.125,"equation_contract_digest":"ae19f42cf9b35e4bfc3429976388c75d01b2128b91b686875edfbd76e46f5ecb","excluded_baseline_checkpoint":"cp2","expected_decision":"CANDIDATE_DIFFERENT_BASELINE_EQUAL","free_available_commit":0.375,"free_available_post_record_digest":"e4f0c95e59ea37aa9db8ae25688ec5f28a700dcbaa76ba5bd2056b4eaac42804","free_available_pre_record_digest":"d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c","prediction_digest":"0fabfc2935e47e5c5b6be99d4a31ae28e2c1d26f25cfe12892060c42ed2dbb61","schema_id":"g2_d3_binding_offer_static_prediction","schema_version":"s1pj.v1"}
```

Die erwartete spaetere Entscheidung lautet:

```text
CANDIDATE_DIFFERENT_BASELINE_EQUAL
```

Das ist eine Vorabprognose und noch kein Ergebnis.

## Digesttabelle

| Record | Eigendigest | Inputbytes-Digest |
|---|---|---|
| Gleichungsvertrag | `ae19f42cf9b35e4bfc3429976388c75d01b2128b91b686875edfbd76e46f5ecb` | `5c8a3dc5081755c34854ef4ab119b00731f4d60924e5becda9565d28b59135e5` |
| `FREE_AVAILABLE`-Nachrecord | `e4f0c95e59ea37aa9db8ae25688ec5f28a700dcbaa76ba5bd2056b4eaac42804` | `9195946005008bf034a8625d04ddaf58826254f8a8fbd11f3b3e3433a9483d9f` |
| `BLOCKED_HELD`-Nachrecord | `c3874e3b342a62c5f9366938eded9c60cb3c38356aa8be9155cd6855a126645c` | `1f7d2b8fb9a5d7afebe1fbd60adaa915b3f46c5efe85d98c37d02389cfb64227` |
| Adaptervertrag | `7a42352262636bf6dc851095814a1bc6be35c692eb21300e72a13678f4ae3c75` | `15d5134123f30dd45b0435cb7c7b6f151d03dd115d559253d0aec762f5e7d99d` |
| Gesamtprognose | `0fabfc2935e47e5c5b6be99d4a31ae28e2c1d26f25cfe12892060c42ed2dbb61` | `4c85ec5a607fc93c91c255f5e8b483533601d761194513296821c6f2b2089973` |

## Falsifikation und Abbruch

Die Vorabprognose ist falsifiziert, wenn eine spaetere gueltige Umsetzung
einen anderen Kandidatencommit, Nachrecord oder Kandidatenkontrast liefert.

Die Abnahme ist ungueltig oder abzubrechen, wenn:

- der Adapter unterschiedliche Bytes fuer die Replikate erzeugt;
- Armkennung, Kandidatenzustand, O3 oder Angebotswert in den
  Retentionsbaselineoperator gelangt;
- die Baselinereplikate verschiedene Urspruenge oder Ketten erhalten;
- `cp2` in den S1-PJ-Vergleich eingeht;
- ein Kandidatennachzustand repariert oder nur teilweise committed wird;
- ein anderer als der gebundene Gleichungs-, Payload- oder Adapterdigest
  verwendet wird;
- der Baselinekontrast ungleich `0.0` ist;
- ein positiver Ausgang als mehr als kontrollierte Ressourcensensitivitaet
  ausgelegt wird.

## Aussagegrenze

S1-PJ beschreibt einen konstruktiv festgelegten ressourcenbegrenzten
Bindungsoperator. Eine spaetere Bestaetigung zeigt deshalb zunaechst nur, dass
Implementierung und Ledger der vorregistrierten Regel entsprechen. Die
extern gesetzte `free`/`blocked`-Differenz ist keine selbst gebildete
Substratgeschichte. Die hypothetische MCM-Memory bleibt eine
Entwicklungsrichtung.

## Naechster erlaubter Schritt

S1-PK darf ausschliesslich den Implementierungs-, Fixture-, Adapter-,
Comparator-, Fehlermutations- und Einmaltestbudgetvertrag fuer S1-PJ binden.
Implementierung, Feldintegration und Lauf bleiben gesperrt.
