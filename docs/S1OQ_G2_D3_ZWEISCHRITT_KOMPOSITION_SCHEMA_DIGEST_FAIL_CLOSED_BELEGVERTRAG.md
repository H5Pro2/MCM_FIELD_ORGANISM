# S1-OQ G2/D3 Zweischrittkomposition: Schema-, Digest- und Fail-Closed-Belegvertrag

## Status

S1-OQ bindet ausschliesslich API-Schema, Sequenzregistry, Vertragsdigest,
Phasen, Fehlercodes und passive Belegrollen fuer die in S1-OP festgelegte
reine Zweischrittkomposition. Der Schritt implementiert keine Funktion,
erzeugt keine Fixtures und fuehrt keinen Test aus.

Entscheidung:

```text
G2_D3_TWO_STEP_COMPOSITION_SCHEMA_DIGEST_REGISTRY_AND_FAIL_CLOSED_RECEIPT_BOUND
```

## Gebundene API

Eine spaetere Implementierung darf genau bereitstellen:

```text
build_g2_d3_two_step_composition_registry()
-> G2D3TwoStepCompositionRegistry

compose_g2_d3_two_step_continuation(
    first_boundary_raw_bytes,
    second_boundary_raw_bytes,
    initial_d3_raw_bytes,
    formation_enabled,
    sequence_registry,
    target_commit_registry,
    amount_registry,
    boundary_registry,
    d3_registry,
) -> G2D3TwoStepCompositionResult
```

Die drei Byteeingaben muessen exakt `bytes`, der Schalter exakt `bool` und
alle Registries Instanzen ihrer vorregistrierten Klassen sein. Falsche Typen
oder Registries scheitern vor einem Resultat.

Die API akzeptiert keine Zielbytes, Betraege, Projektionsbelege,
Commitbelege, Validierungsbelege, Schrittzaehler oder Ergebnisrollen als
Eingabe.

## Vertragsidentitaet

Gebundene ASCII-Vertragsidentitaet und SHA-256-Digest:

```text
g2.d3.two-step-composition.contract.s1oq.v1
-> e68646a2d4a605ecdd36125dcd5f97cd849091d5af1bbcf1f587b1c01e1c2e06
```

Die spaetere Registry muss zusaetzlich exakt akzeptieren:

```text
projector contract
= c761d3f5b2dc486ca6cb9389d305e9b2ec8d847812bac72e40d89995a66f6e2b

commit contract
= 4cae38e9c7986ff6099cfd8c2c742a2c11465bb61a9885441a403fab9b5859b5

amount operator contract
= 396bd7b9fde4b7ee3b268e1d53245fd2a950cf4d8d9464f084d9b498c17de83b

boundary validator contract
= 7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0

D3 validator contract
= b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c
```

Eine abweichende Vertragsdigestidentitaet scheitert vor der ersten
Projektion.

## Registryform

`G2D3TwoStepCompositionRegistry` ist unveraenderlich und bindet genau:

```text
receipt_schema_id
receipt_schema_version
composition_class_id
composition_statuses
composition_phases
failure_codes
chain_records
accepted_projector_contract_digest
accepted_commit_contract_digest
accepted_amount_operator_contract_digest
accepted_boundary_validator_contract_digest
accepted_d3_validator_contract_digest
composition_contract_digest
```

Feste Werte:

```text
receipt_schema_id = g2_d3_two_step_composition_receipt
receipt_schema_version = s1oq.v1
composition_class_id = G2_D3_TWO_FRESH_CONTINUATION_COMPOSITION
composition_statuses = (TWO_STEP_COMPOSED, not_computable)
```

## Zwei Registry-Chainrecords

`chain_records` enthaelt exakt zwei unveraenderliche Records.

### `OP_CHAIN_XXX`

```text
first_boundary_input_digest
= c3999c31317b4e79dbc42323904a82fcf0bb1ec4b6089d7dded51415d249f42c

second_boundary_input_digest
= 6d4a6a51e8c3fb81734598f23edff930f88b5f85e00b79c5d84d1da2b5b0ad9a

first_current_contact_digest
= 0df023f42e8be41504bbad49fc8c5d89b7d16e25a2904c773f0845a841ffea15

second_prior_contact_digest
= 0df023f42e8be41504bbad49fc8c5d89b7d16e25a2904c773f0845a841ffea15
```

### `OP_CHAIN_YYY`

```text
first_boundary_input_digest
= 2b128b63e23ede98397b080515768e012ec7fe87fa1734874de790f35456a34b

second_boundary_input_digest
= dc772636ed23e9cf9a904fd9943a7a1bcfacafe08aed9e60a65ac93f3d266d32

first_current_contact_digest
= d270f4a888136e4a6dc182b15468c3e7dc4c0567b4bb92eee75818638088f356

second_prior_contact_digest
= d270f4a888136e4a6dc182b15468c3e7dc4c0567b4bb92eee75818638088f356
```

Beide Chainrecords binden gemeinsam:

```text
initial_d3_input_digest
= d248ddae09d0cbd3874254082ed5675a82792d6e4fb3aa76ecf0ef59cbc546f7

initial_anatomy_record_digest
= 1eb6882cb0d566ca5c41a1bdf3b805f3ba0f2fd2bebfe4013461d1f56e74ea3f

intermediate_d3_input_digest
= 2a4eaace22145b47e44e3d0c5a98a8b3e289deeee1190db4bb079228bf11aea8

intermediate_anatomy_record_digest
= d9d4249f64c737b49c2b8e3816d0f9c876e0fdcea898208bf919185560c6ce4c

final_d3_input_digest
= a0e9a2468571ab2a3c437f8d436958b5c0eef886ad1e7f3d2b4ce54d278e7bab

final_anatomy_record_digest
= efba6284b3e56cfe2041465eb8acc76b00de34ee8303f6a2caa20b2a3fc66681
```

Der erste Boundary-Inputdigest waehlt die Chainrolle. Initial-D3 und
zweite Grenze werden danach gegen denselben Chainrecord geprueft. X- und
Y-Rollen duerfen nicht gekreuzt werden.

## Resultat und passiver Beleg

Das unveraenderliche Resultat enthaelt genau:

```text
final_d3_raw_bytes: bytes | not_computable
receipt: G2D3TwoStepCompositionReceipt
```

Der passive Beleg bindet ausschliesslich:

```text
receipt_schema_id
receipt_schema_version
composition_class_id
first_boundary_input_bytes_digest
second_boundary_input_bytes_digest
initial_d3_input_bytes_digest
formation_enabled
chain_role
first_current_contact_digest
second_prior_contact_digest
first_projection_receipt_digest
first_commit_receipt_digest
intermediate_d3_input_bytes_digest
intermediate_anatomy_record_digest
second_boundary_validation_receipt_digest
second_source_d3_anatomy_record_digest
second_projection_receipt_digest
second_commit_receipt_digest
final_d3_input_bytes_digest
final_anatomy_record_digest
composition_status
validation_status
completed_checks
failure_reasons
accepted_projector_contract_digest
accepted_commit_contract_digest
accepted_amount_operator_contract_digest
accepted_boundary_validator_contract_digest
accepted_d3_validator_contract_digest
composition_contract_digest
composition_receipt_digest
```

Der Beleg enthaelt keine Rohbytes und keine verschachtelten Belegobjekte.
Sein eigener Digest wird ueber die kanonische Payload ohne
`composition_receipt_digest` berechnet. Er ist passive Dokumentation und
kein Folgeeingang fuer Grenz-, D3-, O3-, Feld- oder Sequenzlogik.

Bei Erfolg gilt:

```text
composition_status = TWO_STEP_COMPOSED
validation_status = valid
failure_reasons = ()
final_d3_raw_bytes is second committed_d3_raw_bytes
```

## Gebundene Phasen

```text
api_intake
chain_binding
first_projection
first_commit
intermediate_identity_gate
second_boundary_validation
second_source_binding_gate
second_contact_link_gate
second_projection
second_commit
final_identity_gate
persistence_guard
composition_receipt
```

Der erste Fehler beendet alle nachgelagerten Phasen. Insbesondere werden
zweite Projektion und zweiter Commit erst nach erfolgreicher
Zwischenidentitaet, zweiter Grenzvalidierung sowie Quellen- und
Kontaktverknuepfung aufgerufen.

## Fehlercodes

Die Registry bindet exakt:

```text
OQ_UNKNOWN_CHAIN_BINDING
OQ_FORMATION_DISABLED
OQ_FIRST_PROJECTION_FAILED
OQ_FIRST_COMMIT_FAILED
OQ_INTERMEDIATE_IDENTITY_MISMATCH
OQ_SECOND_BOUNDARY_INVALID
OQ_SECOND_SOURCE_BINDING_MISMATCH
OQ_SECOND_CONTACT_LINK_MISMATCH
OQ_SECOND_PROJECTION_FAILED
OQ_SECOND_COMMIT_FAILED
OQ_FINAL_IDENTITY_MISMATCH
```

Pro ungueltigem Beleg ist exakt ein Fehlercode erlaubt. Alle nicht belastbar
erreichten Rollen und `final_d3_raw_bytes` werden `not_computable`.

### Chain- und Formationsgate

Ein unbekannter erster Boundary-Inputdigest oder ein vom Chainrecord
abweichender Initial-D3-Digest liefert `OQ_UNKNOWN_CHAIN_BINDING`.
`formation_enabled=false` liefert separat `OQ_FORMATION_DISABLED`. Kein
erster Projektionsaufruf wird dann ausgefuehrt. Eine gekreuzte X/Y-Zweitgrenze
wird erst nach dem ersten Commit am gebundenen Kontaktlink gesperrt.

### Erster Schritt

Ein ungueltiges Projektionsresultat liefert `OQ_FIRST_PROJECTION_FAILED`.
Ein ungueltiges Commitresultat oder ein anderer Status als
`PROJECTED_COMMITTED` liefert `OQ_FIRST_COMMIT_FAILED`.

Weichen erste Commitbytes, Inputdigest oder Anatomierecorddigest von Mixed
ab, gilt `OQ_INTERMEDIATE_IDENTITY_MISMATCH`. Danach wird keine zweite
Grenze validiert.

### Zweite Grenze

Die zweite Grenze wird mit den vollstaendigen ersten Commitbytes durch den
unveraenderten S1-OC-Validator geprueft. Ein sonstiger Grenzfehler liefert
`OQ_SECOND_BOUNDARY_INVALID`.

Bindet ihr Feld `source_d3_anatomy_record_digest` nicht exakt Mixed, gilt
`OQ_SECOND_SOURCE_BINDING_MISMATCH`. Entspricht ihr validierter
`prior_contact_digest` nicht der registrierten ersten
`current_contact_digest`, gilt `OQ_SECOND_CONTACT_LINK_MISMATCH`.

Diese beiden Kausalfehler werden nicht als unbekannte Chain oder allgemeiner
Grenzfehler umgedeutet. Die zweite Projektion bleibt gesperrt.

### Zweiter Schritt

Ein ungueltiges zweites Projektionsresultat liefert
`OQ_SECOND_PROJECTION_FAILED`. Ein ungueltiges zweites Commitresultat oder
ein anderer Status als `PROJECTED_COMMITTED` liefert
`OQ_SECOND_COMMIT_FAILED`.

Weichen zweite Commitbytes, finaler Inputdigest oder finaler
Anatomierecorddigest vom registrierten Second-Zustand ab, gilt
`OQ_FINAL_IDENTITY_MISMATCH`. Es werden keine finalen Bytes ausgegeben.

## Persistenz- und Aufrufgrenze

Pro gueltigem Aufruf sind hoechstens erlaubt:

```text
2 Projektionsaufrufe
2 Commitaufrufe
1 zusaetzliche Validierung der zweiten Grenze
```

Die Commitaufrufe duerfen intern wie gebunden neu projizieren. Diese
Rekonstruktion ist keine dritte Sequenzstufe.

Zwischenbytes und Belege bleiben nur lokale Werte desselben reinen Aufrufs.
Es gibt keine globale Variable, keinen Cache, keinen Singleton, keinen
Dateizugriff und keine Runtimepublikation.

## Aussagegrenze

S1-OQ bindet nur die technische Nachvollziehbarkeit einer begrenzten
Zweischrittkomposition. Es gibt noch keine Sequenzimplementierung und keinen
Lauf. Die deterministische Halbierungsfolge ist keine eigene
Funktionsabgrenzung gegen angepasste zustandsbehaftete Baselines und kein
Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OR darf ausschliesslich Dateigrenzen, zwei gueltige Chainfixtures,
gezielte Einzelmutationen und ein endliches Einmaltestbudget fuer die
S1-OQ-Komposition binden.

S1-OR darf keine Produktions- oder Testimplementierung, keinen Testlauf,
keine Runtimepublikation, keine O3-Auswertung und keinen Feld-, Transfer-
oder Runnerpfad ausfuehren.
