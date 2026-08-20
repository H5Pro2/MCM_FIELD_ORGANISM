# S1-OK G2/D3 Zielprojektions- und Commit-Schema-, Digest- und Fail-Closed-Vertrag

## Status

S1-OK bindet ausschliesslich die statischen Schnittstellen fuer eine reine
G2/D3-Zielprojektion und eine davon getrennte atomare Zustandsauswahl. Der
Schritt implementiert keine API, fuehrt keinen Test aus und veraendert keinen
Runtime-, O3- oder Feldzustand.

Entscheidung:

```text
G2_D3_TARGET_PROJECTION_AND_ATOMIC_COMMIT_SCHEMAS_DIGESTS_FAIL_CLOSED_BOUND
```

## Trennung der Schnittstellen

Spaeter sind genau drei oeffentliche Funktionen vorgesehen:

```text
build_g2_d3_target_commit_registry()
-> G2D3TargetCommitRegistry

project_g2_d3_conservative_target(
    boundary_raw_bytes,
    source_d3_raw_bytes,
    formation_enabled,
    target_commit_registry,
    amount_registry,
    boundary_registry,
    d3_registry,
) -> G2D3TargetProjectionResult

verify_and_commit_g2_d3_projected_target(
    boundary_raw_bytes,
    source_d3_raw_bytes,
    current_d3_raw_bytes,
    proposed_target_d3_raw_bytes,
    formation_enabled,
    target_commit_registry,
    amount_registry,
    boundary_registry,
    d3_registry,
) -> G2D3AtomicCommitResult
```

Alle Byteeingaben muessen exakt `bytes`, der Schalter exakt `bool` und alle
Registries Instanzen ihrer vorregistrierten Klassen sein. Eine Projektion
nimmt keinen Betragsbeleg entgegen. Die Commitfunktion nimmt weder einen
Betrags- noch einen Projektionsbeleg entgegen. Sie berechnet die erwartete
Projektion aus den Originalbytes neu.

`commit` bezeichnet in S1-OK nur die atomare Auswahl vollstaendiger Bytes im
Rueckgabeobjekt. Es gibt weder einen Runtime-Speicherzugriff noch eine
Publikation in das MCM-Wahrnehmungsfeld.

## Gebundene Vertragsdigests

Die spaetere Registry muss folgende ASCII-Vertragsidentitaeten und deren
SHA-256-Digests exakt binden:

```text
g2.d3.conservative-target.projector.contract.s1ok.v1
-> c761d3f5b2dc486ca6cb9389d305e9b2ec8d847812bac72e40d89995a66f6e2b

g2.d3.atomic-target-commit.contract.s1ok.v1
-> 4cae38e9c7986ff6099cfd8c2c742a2c11465bb61a9885441a403fab9b5859b5
```

Zusaetzlich sind exakt zu akzeptieren:

```text
S1-OI amount operator:
396bd7b9fde4b7ee3b268e1d53245fd2a950cf4d8d9464f084d9b498c17de83b

S1-OC boundary validator:
7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0

D3 anatomy validator:
b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c
```

Eine abweichende Registry oder Vertragsdigestidentitaet scheitert vor einer
fachlichen Auswertung.

## Projektionsresultat und passiver Beleg

Das unveraenderliche `G2D3TargetProjectionResult` enthaelt genau:

```text
target_d3_raw_bytes: bytes | "not_computable"
receipt: G2D3TargetProjectionReceipt
```

Der passive Beleg verwendet:

```text
schema_id = g2_d3_target_projection_receipt
schema_version = s1ok.v1
```

Er bindet ausschliesslich:

```text
boundary_input_bytes_digest
source_d3_input_bytes_digest
formation_enabled
amount_evaluation_receipt_digest
source_anatomy_record_digest
computed_repartition_amount
projection_status
target_d3_input_bytes_digest
target_anatomy_record_digest
target_validation_receipt_digest
aggregate_projection_digest
evaluation_status
completed_checks
failure_reasons
accepted_amount_operator_contract_digest
accepted_boundary_validator_contract_digest
accepted_d3_validator_contract_digest
projector_contract_digest
projection_receipt_digest
```

Er enthaelt keine Rohbytes und ist kein Folgeeingang. Sein eigener Digest
wird ueber die kanonische Belegabbildung ohne das Feld
`projection_receipt_digest` berechnet.

Zulaessige Projektionsstatus sind:

```text
NO_CHANGE
PROJECTED
not_computable
```

Bei `NO_CHANGE` muss das Resultat dasselbe Byteobjekt wie
`source_d3_raw_bytes` tragen. Bei `PROJECTED` muessen vollstaendige,
kanonische und D3-validierte Zielbytes vorliegen. Bei `not_computable` sind
Zielbytes und alle nicht belastbar ermittelbaren Rollen ebenfalls
`not_computable`.

## Projektionsphasen

Die spaetere Projektion bindet diese Reihenfolge:

```text
api_intake
amount_evaluation
source_projection
target_construction
target_digest_binding
target_validation
persistence_guard
projection_receipt
```

Ein von S1-OI abgelehnter Originalinput wird nicht repariert. Fuer diesen
oeffentlich erreichbaren Fehler gilt exakt:

```text
OK_PROJECTION_AMOUNT_EVALUATION_FAILED
```

Eine intern konstruierte Verletzung der S1-OJ-Erhaltung, Digestidentitaet
oder D3-Validitaet ist ein Implementierungsdefekt. Sie darf keine Zielbytes
und keinen scheinbar gueltigen Beleg liefern.

## Commitresultat und passiver Beleg

Das unveraenderliche `G2D3AtomicCommitResult` enthaelt genau:

```text
committed_d3_raw_bytes: bytes | "not_computable"
receipt: G2D3AtomicCommitReceipt
```

Der passive Beleg verwendet:

```text
schema_id = g2_d3_atomic_commit_receipt
schema_version = s1ok.v1
```

Er bindet ausschliesslich:

```text
boundary_input_bytes_digest
source_d3_input_bytes_digest
current_d3_input_bytes_digest
proposed_target_d3_input_bytes_digest
formation_enabled
recomputed_projection_receipt_digest
source_anatomy_record_digest
current_anatomy_record_digest
expected_target_d3_input_bytes_digest
proposed_target_anatomy_record_digest
commit_status
committed_d3_input_bytes_digest
validation_status
completed_checks
failure_reasons
accepted_projector_contract_digest
accepted_amount_operator_contract_digest
accepted_boundary_validator_contract_digest
accepted_d3_validator_contract_digest
commit_contract_digest
commit_receipt_digest
```

Der eigene Digest schliesst `commit_receipt_digest` aus. Der Beleg enthaelt
keine Rohbytes und autorisiert weder denselben noch einen spaeteren Aufruf.

Zulaessige Commitstatus sind:

```text
NO_CHANGE_COMMITTED
PROJECTED_COMMITTED
STALE_SOURCE
not_computable
```

Bei `NO_CHANGE_COMMITTED` muessen Quelle, aktueller Zustand und Vorschlag
inhaltlich identisch sein; zurueckgegeben wird exakt das Objekt
`current_d3_raw_bytes`. Bei `PROJECTED_COMMITTED` wird exakt das vollstaendig
gepruefte Objekt `proposed_target_d3_raw_bytes` zurueckgegeben. Alle
Fehlerstatus geben `not_computable` statt Zustandsbytes aus.

## Commitphasen und Fehlercodes

Die spaetere Commitauswahl bindet diese Reihenfolge:

```text
api_intake
source_projection_recomputation
proposed_target_validation
proposed_target_comparison
current_source_validation
stale_source_gate
atomic_selection
persistence_guard
commit_receipt
```

Die oeffentlich erreichbaren Einzelfehlercodes sind:

```text
OK_COMMIT_PROJECTION_RECOMPUTATION_FAILED
OK_COMMIT_PROPOSED_TARGET_INVALID
OK_COMMIT_PROPOSED_TARGET_MISMATCH
OK_COMMIT_CURRENT_SOURCE_INVALID
OK_COMMIT_STALE_SOURCE
```

Pro Beleg ist hoechstens ein Fehlercode erlaubt. Der erste Fehler beendet die
weitere Auswahl. Ein gueltiger, aber von der intern neu berechneten Projektion
abweichender Vorschlag wird nicht angepasst. Ein gueltiger aktueller Zustand
mit anderer `anatomy_record_digest` als die Originalquelle ist
`STALE_SOURCE` und erzeugt keine Zustandsbytes.

## Erhaltung und Persistenzsperre

Die Zielbytes muessen alle S1-OJ-Bedingungen erfuellen. Insbesondere:

```text
target.bound_unconfigured = source.bound_unconfigured - m
target.bound_configured = source.bound_configured + m
target.capacity = source.capacity
target.free = source.free
target.blocked = source.blocked
target.aggregate_projection_digest = source.aggregate_projection_digest
```

Bei positivem Betrag muessen Ressourcenaccount- und Anatomierecorddigest neu
und verschieden von der Quelle sein. Grenz-, Ereignis-, Kontakt-, Betrags-,
Beleg-, Historien- und Schalterrollen bleiben in D3-Zielbytes verboten.

Projektions- und Commitbelege duerfen nicht in D3, O3, Feldzustand,
Snapshot, Runnerzustand oder Sequenzhistorie geschrieben werden. Es gibt
keinen I/O-, Medien-, Netzwerk- oder Runtimepfad.

## Falsifikation und Aussagegrenze

Die Schnittstellenform wird verworfen, wenn ein externer Beleg benoetigt
wird, ein Vorschlag den erwarteten Zustand bestimmen kann, ein veralteter
Quellzustand akzeptiert wird, ein Nullpfad neue Bytes erzeugt, ein Fehler
Teilbytes ausgibt oder eine andere D3-Sachrolle veraendert werden muss.

S1-OK weist keine Bildungs-, Lern- oder Feldfunktion nach. Es ist nur die
statische Grundlage fuer die weitere Entwicklung einer hypothetischen
MCM-Memory. Die angepassten Gegenbaselines bleiben erforderlich.

## Naechster erlaubter Schritt

S1-OL darf ausschliesslich Implementierungsdateien, gueltige Fixtures,
Fehlermutationen und ein endliches Einmaltestbudget fuer die reine
Projektionsstufe binden. Die Commitimplementierung bleibt dabei noch
gesperrt, damit Projektion und atomare Auswahl getrennt abgenommen werden.

S1-OL darf keine Produktions- oder Testimplementierung, keinen Runtimecommit,
keine O3-Auswertung und keinen Feld-, Transfer- oder Runnerpfad ausfuehren.
