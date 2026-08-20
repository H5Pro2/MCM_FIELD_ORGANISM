# S1-PF G2/D3 Free/Blocked-Interventionsvalidator: Implementierungs-, Fehlermutations- und Testbudgetvertrag

## Status und Umfang

S1-PF bindet ausschliesslich die spaetere Implementierungsgrenze fuer die in
S1-PE festgelegte statische Fixture. Der Schritt bestimmt Dateien, API,
Abhaengigkeiten, Validierungsphasen, Fehlerrollen, Fehlermutationen und ein
endliches Einmaltestbudget.

S1-PF implementiert nichts und fuehrt keinen Test aus. Wirkungsgleichung,
Bindungsdynamik, Kandidatenintegration, O3-, Feld- und Runtimepfad bleiben
gesperrt.

Entscheidung:

```text
G2_D3_FREE_BLOCKED_INTERVENTION_VALIDATOR_IMPLEMENTATION_AND_SINGLE_TEST_BUDGET_BOUND
```

## Gebundene Dateigrenze

S1-PG darf genau drei neue Dateien anlegen:

| Datei | Aufgabe |
|---|---|
| `mcm_field_organism/g2_d3_free_blocked_intervention_validator.py` | reiner passiver Interventionspaarvalidator |
| `tests/g2_d3_s1pg_free_blocked_intervention_fixtures.py` | kanonische S1-PE-Bytes und kontrollierte Fehlermutationen |
| `tests/test_g2_d3_s1pg_free_blocked_intervention_validator.py` | fokussierte technische Abnahme |

Bestehende Produktions-, Paket-, Fixture- und Testdateien bleiben
unveraendert. Insbesondere werden `mcm_field_organism/__init__.py`, D3-, O3-,
Commit-, Feld-, Runtime-, Runner- und Medienmodule nicht bearbeitet.

Nach dem einzigen Testlauf duerfen nur `AKTUELLER_FORSCHUNGSWEG.md`,
`README.md` und `docs/AKTUELLE_TECHNISCHE_PROJEKTGRENZE.md` um das
tatsaechliche Ergebnis ergaenzt werden.

## Eingefrorene Grundlage

Vor S1-PG gelten exakt:

```text
mcm_field_organism/g2_d3_schema_validator.py
= 666f38ef49ddfa1538a301f43f265d60e7e0f1f48834e3df0653551d03f18c0d

mcm_field_organism/kfs1_schema_validator.py
= c0355f6b98f129f2ce3743a409850b2d777f1c4b6ecc02d0971c2a523843162e

tests/g2_d3_s1nr_fixtures.py
= 76351b57709f2af5a249a76a48a8cd08a7ac51f5b79855e592f69087fd80724d

tests/test_g2_d3_s1nr_schema_validator.py
= 244aecbe65b057f22080503390e52fc8cdb20e9a4b713c093ca8e990bb8dcb87
```

Diese vier Dateien muessen nach S1-PG byteidentisch dieselben Digests tragen.
Die zehn vorhandenen S1-NR-Testmethoden werden unveraendert in den
gemeinsamen Einmallauf aufgenommen.

## Import- und Informationsgrenze

Das neue Produktionsmodul darf ausschliesslich importieren:

- Python-Standardbibliothek fuer unveraenderliche Datentypen, JSON und
  endliche Zahlenpruefung;
- `G2D3ValidationRegistry` und `validate_g2_d3_anatomy_record` aus
  `g2_d3_schema_validator`;
- `canonical_json_bytes` und `sha256_hex` aus
  `kfs1_schema_validator`.

`validate_g2_d3_f1_pair` darf weder importiert noch aufgerufen werden. Der
neue Validator darf keine Records erzeugen, umbuchen, committen oder an einen
Kandidatenpfad weitergeben. Er liest nur vollstaendige Bytes und erzeugt
einen passiven unveraenderlichen Receipt.

Armname, Fixturemanifest und Ereignismetadaten duerfen nur im externen
Validatorrahmen gelesen werden. In den drei D3-Records bleiben sie verboten.

## Oeffentliche Oberflaeche

Das Modul darf genau folgende Funktionsoberflaeche bereitstellen:

```text
build_g2_d3_free_blocked_intervention_registry()
-> G2D3FreeBlockedInterventionRegistry

validate_g2_d3_free_blocked_intervention(
    prestate_raw_bytes,
    free_available_post_raw_bytes,
    blocked_held_post_raw_bytes,
    event_identity_raw_bytes,
    fixture_manifest_raw_bytes,
    intervention_registry,
    anatomy_registry,
) -> G2D3FreeBlockedInterventionReceipt
```

Alle fuenf Byteeingaben muessen exakt `bytes` sein. Beide Registries muessen
exakt ihren gebundenen Typen und Inhalten entsprechen. Falsche API-Typen
scheitern vor einem Receipt. Private Parser oder Teilvalidatoren fehlen in
`__all__`.

Der Vertragsdigest lautet:

```text
5d91f9c6c5d07cf098bfc9bb9e10131025d2e177795b6ab583b595ad75a244c1
```

Er ist SHA-256 ueber die ASCII-Bytes:

```text
g2.d3.free_blocked.intervention.validator.contract.s1pf.v1
```

## Registrybindung

Die Registry bindet mindestens:

```text
fixture_schema_id = g2_d3_free_blocked_intervention_fixture
event_schema_id = g2_d3_fresh_binding_event_identity
schema_version = s1pe.v1
fixture_id = S1_PE_G2_D3_FREE_BLOCKED_PAIR_V1
causal_source_id = REGISTERED_EXTERNAL_TEST_INTERVENTION
free_available_arm_id = FREE_AVAILABLE
blocked_held_arm_id = BLOCKED_HELD
fresh_event_id = S1_PE_IDENTICAL_FRESH_BINDING_EVENT_V1
transfer_amount = 0.125
```

Ausserdem bindet sie die fuenf S1-PE-Inputbytes-Digests und den
S1-PF-Vertragsdigest. Ein Aufrufer darf diese Werte nicht ersetzen.

## Validierungsphasen

Die vollstaendige Reihenfolge lautet:

```text
byte_intake
schema_validation
digest_validation
causal_source_validation
anatomy_record_validation
transfer_validation
pair_control_validation
event_identity_validation
metadata_exposure_validation
validation_receipt
```

Der bestehende Einzelrecordvalidator wird fuer Vorzustand und beide
Nachzustaende jeweils genau einmal aufgerufen. Erst drei vollstaendig
gueltige Einzelreceipts erlauben die Paarpruefung.

Es gibt keinen Teilreceipt pro Arm, keinen Zustandsoutput und keinen Commit.
Fehlergruende werden sortiert, eindeutig und deterministisch ausgegeben.

## Receiptoberflaeche

Der unveraenderliche Receipt bindet exakt:

```text
receipt_schema_id
receipt_schema_version
validation_status
completed_checks
failure_reasons
prestate_input_bytes_digest
free_available_input_bytes_digest
blocked_held_input_bytes_digest
event_identity_input_bytes_digest
fixture_manifest_input_bytes_digest
prestate_record_digest
free_available_record_digest
blocked_held_record_digest
event_identity_digest
fixture_digest
validator_contract_digest
validation_receipt_digest
```

`validation_status` ist ausschliesslich `valid` oder `invalid`. Nicht
berechenbare Digestrollen tragen exakt `not_computable`. Der
`validation_receipt_digest` wird ueber den kanonischen Receiptpayload ohne
dieses eigene Feld berechnet.

## Maschinenlesbare Fehlerrollen

S1-PG muss exakt folgende Fehlercodes binden:

```text
PE_UNKNOWN_SCHEMA_OR_VERSION
PE_MISSING_OR_UNKNOWN_FIELD
PE_NONCANONICAL_SERIALIZATION
PE_EVENT_IDENTITY_DIGEST_MISMATCH
PE_FIXTURE_DIGEST_MISMATCH
PE_ANATOMY_RECORD_INVALID
PE_EVENT_PAYLOAD_BOUND
PD_INVALID_CAUSAL_SOURCE
PD_INVALID_COMMON_PRESTATE
PD_INVALID_ARM_SET
PD_INVALID_TRANSFER_AMOUNT
PD_INSUFFICIENT_SOURCE_RESOURCE
PD_NON_TARGET_ROLE_CHANGED
PD_PAIR_CONTROL_MISMATCH
PD_LOCAL_CONSERVATION_FAILED
PD_NONFINITE_OR_NEGATIVE_RESOURCE
PD_PARTIAL_COMMIT_ATTEMPT
PD_FORBIDDEN_METADATA_PERSISTENCE
```

`PD_PARTIAL_COMMIT_ATTEMPT` bleibt ein defensiver Gatecode. Die oeffentliche
API besitzt absichtlich keinen Teilcommitpfad; falsche API-Typen oder
fehlende Byteeingaben scheitern vor einem Receipt.

## Gebundene externe Fehlermutationen

Die Fixturedatei muss genau 17 einzelne kontrollierte Mutationen enthalten:

| Mutation | Einziger erwarteter Code |
|---|---|
| Fixtureversion geaendert | `PE_UNKNOWN_SCHEMA_OR_VERSION` |
| Fixturefeld entfernt | `PE_MISSING_OR_UNKNOWN_FIELD` |
| unbekanntes Ereignisfeld ergaenzt | `PE_MISSING_OR_UNKNOWN_FIELD` |
| Fixturebytes nichtkanonisch serialisiert | `PE_NONCANONICAL_SERIALIZATION` |
| Ereigniseigendigest auf Null gesetzt | `PE_EVENT_IDENTITY_DIGEST_MISMATCH` |
| Fixtureeigendigest auf Null gesetzt | `PE_FIXTURE_DIGEST_MISMATCH` |
| Kausalquellen-ID geaendert | `PD_INVALID_CAUSAL_SOURCE` |
| Vorzustandsreferenz geaendert | `PD_INVALID_COMMON_PRESTATE` |
| beide Arm-IDs gleichgesetzt | `PD_INVALID_ARM_SET` |
| Umbuchungsbetrag auf null gesetzt | `PD_INVALID_TRANSFER_AMOUNT` |
| Umbuchungsbetrag ueber eine Quellrolle gesetzt | `PD_INSUFFICIENT_SOURCE_RESOURCE` |
| leitende Unterrolle in einem gueltigen Nachrecord geaendert | `PD_NON_TARGET_ROLE_CHANGED` |
| gueltiger Nachrecord auf andere Kante gesetzt | `PD_PAIR_CONTROL_MISMATCH` |
| gueltiger Nachrecord mit falscher tatsaechlicher Umbuchung eingesetzt | `PD_LOCAL_CONSERVATION_FAILED` |
| negative Ressourcenrolle eingesetzt | `PD_NONFINITE_OR_NEGATIVE_RESOURCE` |
| Armmetadatum in einem Nachrecord eingesetzt | `PD_FORBIDDEN_METADATA_PERSISTENCE` |
| Ereignispayloadstatus auf `BOUND` gesetzt | `PE_EVENT_PAYLOAD_BOUND` |

Jede Mutation muss alle abhaengigen Digests neu berechnen, ausser wenn gerade
eine Digestabweichung geprueft wird. Dadurch bleibt genau die bezeichnete
Ursache isoliert. Es gibt kein Reparieren oder Mehrdeutigmachen der
Fehlerfixtures.

Zusaetzlich muss ein separat digestmutierter D3-Record den einzigen Code
`PE_ANATOMY_RECORD_INVALID` erzeugen. Er gehoert zur defensiven
Einzelrecordgrenze und nicht zu den 17 semantischen Mutationen.

## Genau 15 neue Testmethoden

Die neue Abnahme bindet exakt:

1. Registrywerte, Vertragsdigest und oeffentliche Oberflaeche;
2. fuenf positive Inputbytes-Digests;
3. drei gueltige Einzelrecordreceipts des bestehenden Validators;
4. kanonische Ereignis- und Fixturedigests;
5. vollstaendigen positiven Paarreceipt;
6. exakte S1-PE-Ressourcenwerte und Umbuchungen;
7. alle 17 semantischen Mutationen mit jeweils genau einem Code;
8. separat ungueltigen D3-Record mit `PE_ANATOMY_RECORD_INVALID`;
9. sortierte eindeutige deterministische Fehlerrollen;
10. byteidentische Eingaben und unveraenderte Registries;
11. falsche API-Typen ohne Teilreceipt;
12. Abwesenheit einer Teilcommit- oder Zustandsoutputoberflaeche;
13. Abwesenheit von Armmetadaten in allen drei D3-Records;
14. getrennte Digestrollen und reproduzierbarer Receiptdigest;
15. isolierte Importoberflaeche ohne F1-Paarvalidator, Feld oder Runtime.

Subtests aendern die Zahl der Testmethoden nicht.

## Endliches S1-PG-Ausfuehrungsbudget

S1-PG darf nach Implementierung genau einmal ausfuehren:

```powershell
python -m unittest `
  tests.test_g2_d3_s1nr_schema_validator `
  tests.test_g2_d3_s1pg_free_blocked_intervention_validator
```

Erwartet werden exakt 25 Testmethoden: zehn unveraenderte S1-NR-Regressionen
und 15 neue S1-PG-Tests. Kein weiterer Test-, Kandidaten-, Feld- oder
Runtimelauf ist freigegeben.

## Abbruchbedingungen

S1-PG ist vor dem Lauf abzubrechen, wenn:

- eine eingefrorene Datei nicht mehr ihren gebundenen Digest besitzt;
- mehr oder andere Dateien bearbeitet werden muessen;
- der bestehende F1-Paarvalidator erforderlich erscheint;
- ein Teilcommit, Zustandsoutput oder Kandidatenpfad benoetigt wird;
- eine Mutation nicht auf genau einen erwarteten Fehlercode isolierbar ist;
- Wirkungsgleichung, Bindungsdynamik, O3-, Feld- oder Runtimezugriff noetig
  wird.

## Aussagegrenze

S1-PF ist nur ein Implementierungs- und Abnahmevertrag. Er erzeugt keinen
Funktionsbefund. Die hypothetische MCM-Memory bleibt eine
Entwicklungsrichtung.

## Naechster erlaubter Schritt

S1-PG darf ausschliesslich die drei gebundenen Dateien implementieren, die
vier eingefrorenen Digests vor und nach der Aenderung pruefen und den einen
25-Test-Lauf ausfuehren. Anschliessend darf nur das tatsaechliche technische
Ergebnis dokumentiert werden. Bindungsdynamik, Kandidatenintegration und
Feldlauf bleiben gesperrt.
