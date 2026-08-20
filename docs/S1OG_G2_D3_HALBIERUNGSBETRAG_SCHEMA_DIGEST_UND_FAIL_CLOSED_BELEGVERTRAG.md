# S1-OG G2/D3 Halbierungsbetrag: Schema-, Digest- und Fail-Closed-Belegvertrag

## Status

S1-OG bindet ausschliesslich Registry, reine API, Digestrollen,
Auswertungsreihenfolge, Fehlercodes und passiven Beleg fuer eine spaetere
Halbierungsbetragsermittlung nach S1-OF. Der Schritt implementiert nichts,
erzeugt keinen D3-Zielzustand und fuehrt keinen Commit, keine O3-Auswertung
und keinen Feld- oder Runtimelauf aus.

Entscheidung:

```text
G2_D3_HALVING_AMOUNT_SCHEMA_DIGEST_AND_FAIL_CLOSED_RECEIPT_BOUND
```

## Gebundene reine API

Eine spaetere Implementierung darf genau folgende oeffentliche Funktionen
bereitstellen:

```text
build_g2_d3_halving_amount_registry()
-> G2D3HalvingAmountRegistry

evaluate_g2_d3_continuation_halving_amount(
    boundary_raw_bytes,
    d3_raw_bytes,
    formation_enabled,
    amount_registry,
    boundary_registry,
    d3_registry,
) -> G2D3HalvingAmountEvaluationReceipt
```

Die API akzeptiert keinen externen S1-OC-Beleg, keinen Ereigniswert, keinen
D3-Zielrecord und keine Historie. `boundary_raw_bytes` und `d3_raw_bytes`
muessen exakte `bytes` sein. `formation_enabled` muss exakt `bool` sein. Alle
drei Registries muessen unveraenderlich und exakt vertragsgleich sein.

Falsche API-Typen oder Registries scheitern vor einem Teilbeleg mit
`TypeError` beziehungsweise `ValueError`.

## Operatoridentitaet

```text
operator_class_id
= G2_D3_CONTINUATION_RESIDUAL_HALVING_AMOUNT

receipt_schema_id
= g2_d3_halving_amount_evaluation_receipt

receipt_schema_version
= s1og.v1
```

Der Operator besitzt keine eigene Eingaberecorddatei. Seine Sachquellen sind
ausschliesslich die zwei bereits kanonischen Bytefolgen und der binaere,
vorregistrierte Ablationsschalter.

## Registrygrenze

`G2D3HalvingAmountRegistry` bindet genau:

- Receipt-Schema-ID und -Version;
- Operator-Klassen-ID;
- Ereignisrollen `NO_PREDECESSOR`, `LOCAL_CONTINUATION`, `LOCAL_SWITCH`;
- `halving_numerator=1` und `halving_denominator=2`;
- die erlaubten Auswertungsphasen;
- die kanonischen Fehlercodes;
- den akzeptierten S1-OC-Grenzvalidatorvertragsdigest;
- den akzeptierten D3-Validatorvertragsdigest;
- den eigenen Operatorvertragsdigest.

Die Registry enthaelt keine Grenzbytes, D3-Ressourcenwerte, Arm-ID,
Kontaktfolge, Ereignishistorie, Zielwerte oder Ergebnisdaten.

## Gebundene Vertragsdigests

S1-OG akzeptiert unveraendert:

```text
S1-OC Grenzvalidatorvertragsdigest
= 7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0

D3-Validatorvertragsdigest
= b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c
```

Der S1-OG-Operatorvertragsdigest lautet:

```text
396bd7b9fde4b7ee3b268e1d53245fd2a950cf4d8d9464f084d9b498c17de83b
```

Er ist SHA-256 der ASCII-Kennung:

```text
g2.d3.halving-amount.evaluator.contract.s1og.v1
```

## Reine Auswertungsphasen

Die spaetere Implementierung muss exakt diese geordnete Phasenregistry
verwenden:

```text
api_intake
source_boundary_validation
source_d3_projection
null_gate
numeric_domain_validation
halving_evaluation
exact_ledger_preview
persistence_guard
evaluation_receipt
```

Abhaengige Phasen werden nach einem Fehler nicht als erfolgreich
abgeschlossen ausgegeben. Es gibt keinen Ersatzbetrag und keine Reparatur.

## Quellvalidierung

Die API muss innerhalb desselben Aufrufs exakt den akzeptierten S1-OC-Pfad
verwenden:

```text
validate_g2_d3_transient_boundary(
    boundary_raw_bytes,
    d3_raw_bytes,
    boundary_registry,
    d3_registry,
)
```

Nur bei `validation_status=valid` duerfen Ereignis und D3-Identitaeten intern
weiterverwendet werden. Ein ungueltiger S1-OC-Beleg fuehrt nur zu
`OG_SOURCE_BOUNDARY_VALIDATION_FAILED`; seine internen Fehlercodes werden im
neuen Beleg nicht uminterpretiert.

Danach werden dieselben unveraenderten D3-Bytes rein gelesen. Der im
S1-OC-Beleg bereits validierte D3-Anatomierecorddigest bleibt die einzige
Quellidentitaet. Die API darf D3 weder neu serialisieren noch mutieren.

## Gebundene Nullpfade

Erst nach gueltiger Quellvalidierung gilt:

```text
formation_enabled = false
-> computed_repartition_amount = 0.0

event_role in {NO_PREDECESSOR, LOCAL_SWITCH}
-> computed_repartition_amount = 0.0

event_role = LOCAL_CONTINUATION
and source_bound_unconfigured = 0
-> computed_repartition_amount = 0.0
```

Nullpfade benoetigen keine positive Float-Operationsdomaene. Ein gueltiger
Integer-D3-Record darf daher im Nullpfad einen gueltigen Nullbeleg liefern.

Eine unbekannte oder nicht berechenbare Ereignisrolle ist kein Nullpfad und
liefert keinen Betrag.

## Positive Halbierung

Nur bei gueltiger Quelle, `formation_enabled=true`,
`event_role=LOCAL_CONTINUATION` und positiver Restressource wird die
S1-OF-Domaene geprueft.

Alle fuenf D3-Rollen muessen nach Parsing exakt `float` sein. Danach gilt:

```text
U = source_bound_unconfigured
C = source_bound_configured
m = U * 0.5

m is finite
m > 0.0
m + m == U
m < U
```

Intern werden ausschliesslich zur Pruefung berechnet:

```text
preview_U = U - m
preview_C = C + m
```

Die exakten rationalen Werte aller binary64-Rollen muessen Vor- und
Nachbilanz nach S1-OF identisch halten. `preview_U` und `preview_C` werden
nicht in den Beleg aufgenommen und nach der Pruefung verworfen.

## Passiver Betragsbeleg

`G2D3HalvingAmountEvaluationReceipt` bindet genau:

```text
receipt_schema_id
receipt_schema_version
operator_class_id
boundary_input_bytes_digest
d3_input_bytes_digest
formation_enabled
source_boundary_validation_receipt_digest oder not_computable
source_d3_validation_receipt_digest oder not_computable
source_d3_anatomy_record_digest oder not_computable
source_boundary_record_digest oder not_computable
event_role oder not_computable
source_bound_unconfigured oder not_computable
source_bound_configured oder not_computable
halving_numerator = 1
halving_denominator = 2
computed_repartition_amount oder not_computable
evaluation_status = valid oder invalid
completed_checks
failure_reasons
accepted_boundary_validator_contract_digest
accepted_d3_validator_contract_digest
operator_contract_digest
amount_evaluation_receipt_digest
```

Der Beleg ist unveraenderlich. Listenrollen werden fuer die kanonische
Serialisierung als JSON-Arrays dargestellt. Sein Digest ist SHA-256 der
kanonischen Belegpayloadbytes ohne
`amount_evaluation_receipt_digest`.

## Digesttrennung

Folgende Rollen bleiben getrennt und duerfen nicht gleichgesetzt werden:

```text
boundary_input_bytes_digest
d3_input_bytes_digest
source_boundary_validation_receipt_digest
source_d3_validation_receipt_digest
source_d3_anatomy_record_digest
source_boundary_record_digest
operator_contract_digest
amount_evaluation_receipt_digest
```

Der Beleg uebernimmt keine deklarierte Eingabedigestrolle ungeprueft als
berechneten Wert. Er enthaelt keinen Zielrecorddigest, weil S1-OG keinen
Zielrecord erlaubt.

## Kanonische Fehlercodes

```text
OG_SOURCE_BOUNDARY_VALIDATION_FAILED
OG_NUMERIC_DOMAIN_MISMATCH
OG_HALVING_INVARIANT_MISMATCH
OG_TARGET_REPRESENTATION_MISMATCH
OG_EXACT_LEDGER_IDENTITY_MISMATCH
```

Fehlercodes werden lexikographisch sortiert, nicht dupliziert und nur nach
erreichter Voraussetzung erzeugt.

## Fehlerzuordnung

| Bedingung | Sicherer Code |
|---|---|
| S1-OC-Quellbeleg ungueltig | `OG_SOURCE_BOUNDARY_VALIDATION_FAILED` |
| positiver Pfad enthaelt Nicht-Float oder unzulaessigen Zahlenwert | `OG_NUMERIC_DOMAIN_MISMATCH` |
| Halbierungswert ist nicht endlich, nicht strikt innen oder es gilt `m+m!=U` | `OG_HALVING_INVARIANT_MISMATCH` |
| Previewwerte sind nicht exakt als erlaubte binary64-Werte darstellbar | `OG_TARGET_REPRESENTATION_MISMATCH` |
| rationale Vor-/Nachbilanz oder Kapazitaet weicht ab | `OG_EXACT_LEDGER_IDENTITY_MISMATCH` |

Ein Quellfehler erzeugt keine abgeleiteten Numerikfehler. Ein Domaenenfehler
erzeugt keine erfundenen Halbierungs-, Preview- oder Bilanzfehler.

## Persistenz- und Oberflaechensperre

Im Beleg und in jeder oeffentlichen S1-OG-Rolle sind verboten:

```text
prior_orientation
current_orientation
event_history
history_id
arm_id
sequence
continuation_count
post_d3_state
target_bound_unconfigured
target_bound_configured
commit_status
field_state
o3_value
reward
label
readout
```

Die geprueften Previewwerte sind lokale Zwischenwerte desselben reinen
Aufrufs und werden nicht persistiert. Der Beleg darf nicht als Eingang fuer
eine weitere Grenz-, Betrags-, D3-, O3-, Feld- oder Baselineauswertung
akzeptiert werden.

## Erlaubte spaetere Testgrenze

Eine spaetere fokussierte Abnahme darf nur pruefen:

- Nullbetrag fuer Erstkontakt, Switch, Ablation und leere Restressource;
- Betrag `0.25` fuer eine gueltige erste F2-Fortsetzung aus `U=0.5`;
- X/X- und Y/Y-Spiegelgleichheit;
- exakte Registry- und Vertragsdigests;
- getrennte Quell-, Record-, Vertrags- und Belegdigests;
- jeden Fehlercode mit einer vorab gebundenen Mutation;
- Integer- und nicht exakt halbierbare positive Domaenenfaelle;
- deterministische Wiederholung und unveraenderte Eingaben;
- passive Nicht-Rueckfuehrbarkeit des Belegs;
- Abwesenheit von D3-Ziel-, Commit-, O3-, Feld-, Transfer-, Runner-, Medien-,
  Netzwerk- und Dateischreibpfaden.

Nicht erlaubt sind eine D3-Umbuchung, ein Zielrecord, die zweite sequenzielle
F2-Halbierung, O3-Komposition, Abschwaechung, Interferenz oder Feldwirkung.

## Aussagegrenze

S1-OG bindet nur Schema, Digests und Fail-Closed-Beleg einer spaeteren reinen
Betragsermittlung. Es gibt noch keinen implementierten Betrag, keinen
D3-Nachzustand, keinen Commit, keine ausgefuehrte O3- oder Feldwirkung, keine
Lernfunktion und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OH darf ausschliesslich Dateigrenzen, unveraenderliche Fixtures,
Fehlermutationen und ein endliches Einmaltestbudget fuer die isolierte
S1-OG-Implementierung binden. Alle erwarteten Bytes, Digests und Fehlercodes
muessen vor der Implementierung feststehen.

S1-OH darf den Operator noch nicht implementieren oder ausfuehren und keinen
D3-Zielzustand, Commit-, O3-, Feld-, Runner- oder Runtimepfad oeffnen.
