# S1-MY KFS-1 Schema- und Digestvertrag

## Status

S1-MY bindet ausschliesslich das statische, maschinenlesbare Schema fuer
`KFS-1`-Anatomierecords und Messrollenrecords sowie deren Digestgrenzen.
Der Schritt enthaelt keine Gleichung, keine Parameter, keine Runtime, keinen
Feldlauf und keine Funktionsentscheidung.

`KFS-1` bleibt ein offener Kandidatenraum. Ein gueltiger Record belegt nur,
dass Anatomie, Ressourcenbilanz, Feldbezug und Expositionshistorie eindeutig
und reproduzierbar beschrieben sind. Er belegt keine Wirkung und keine
hypothetische MCM-Memory.

## Zweck

Das Schema verhindert, dass spaetere Kandidaten- oder Baselinerecords durch
wechselnde Feldnamen, uneindeutige IDs, ausgelassene Vorgeschichte oder
nachtraeglich veraenderte Digestinhalte vergleichbar erscheinen.

## Kanonische Serialisierung

Alle Records muessen vor der Digestbildung nach demselben registrierten
Verfahren serialisiert werden:

- UTF-8 ohne Byte Order Mark;
- Objektfelder lexikographisch sortiert;
- Listen nur in der fuer das jeweilige Feld registrierten Reihenfolge;
- Zahlen in einer vorab gebundenen endlichen Darstellung;
- keine impliziten Standardwerte und keine unbekannten Zusatzfelder;
- Digestverfahren `sha256`;
- `schema_id` und `schema_version` sind Bestandteil jedes Digests.

S1-MY bindet keine Zahlenwerte fuer eine spaetere Dynamik. Die Regel zur
Zahldarstellung verhindert nur mehrere Byteformen desselben statischen Werts.

## Anatomie-Record

Jeder `kfs1_anatomy_record` besitzt genau folgende Pflichtfelder:

| Feld | Rolle |
|---|---|
| `schema_id` | exakt `kfs1_anatomy_record` |
| `schema_version` | registrierte S1-MY-Schemaversion |
| `candidate_id` | exakt `KFS-1` |
| `geometry_digest` | Identitaet der unveraenderten lokalen MCM-Geometrie |
| `carrier_ids` | geordnete, eindeutige lokale Traeger-IDs |
| `edge_records` | geordnete Kantenrecords |
| `anatomy_digest` | Digest ueber alle vorstehenden Felder |

Jeder Eintrag in `edge_records` besitzt:

| Feld | Rolle |
|---|---|
| `edge_id` | aus registriertem Traegerpaar und Geometrie eindeutig ableitbar |
| `carrier_a_id` | erster gebundener lokaler Traeger |
| `carrier_b_id` | zweiter gebundener lokaler Traeger |
| `capacity` | endliche registrierte Gesamtkapazitaet |
| `free` | freie lokale Ressourcenrolle |
| `bound` | gebundene lokale Ressourcenrolle |
| `blocked` | refraktaere lokale Ressourcenrolle |
| `field_reference_digest` | Referenz auf den read-only S/H-Probenraum |
| `resource_account_digest` | Digest des vollstaendigen lokalen Ledgers |

`field_reference_digest` identifiziert nur den gebundenen Probenraum. Er darf
keine Rohdaten, Labels, Zielwerte oder Sequenzpuffer in den Feldzustand
uebernehmen.

## Messrollen-Record

Jeder `kfs1_measurement_record` besitzt genau folgende Pflichtfelder:

| Feld | Rolle |
|---|---|
| `schema_id` | exakt `kfs1_measurement_record` |
| `schema_version` | registrierte S1-MY-Schemaversion |
| `measurement_slot_id` | eindeutige passive Messstellen-ID |
| `measurement_role` | eine in S1-MX zugelassene Messrolle |
| `candidate_or_baseline_id` | eindeutige Kandidaten- oder Baseline-ID |
| `anatomy_digest` | Referenz auf die unveraenderte Anatomie |
| `field_reference_digest` | Referenz auf denselben relevanten Feldprobenraum |
| `exposure_history_digest` | Digest der vollstaendigen relevanten A/B/Gap-Vorgeschichte |
| `read_scope` | vorregistrierter passiver Lesebereich |
| `validation_status` | ausschliesslich `valid` oder `invalid` |
| `failure_reasons` | kanonisch geordnete Ablehnungsgruende |
| `measurement_record_digest` | Digest ueber alle vorstehenden Felder |

Ein Messrollenrecord enthaelt in S1-MY keinen Messwert. Er bindet nur die
Identitaet der spaeteren Messstelle und ihrer kausalen Vorgeschichte.

## Digesttrennung

Folgende Digests bleiben getrennt und duerfen nicht durch einen gemeinsamen
Sammeldigest ersetzt werden:

| Digest | Bindet | Bindet nicht |
|---|---|---|
| `geometry_digest` | lokale Traeger- und Kantenanordnung | Feldwirkung |
| `field_reference_digest` | read-only Feldprobenraum | Rohdateninhalt oder Ergebnis |
| `resource_account_digest` | Kapazitaet und drei Ressourcenrollen einer Kante | Dynamik |
| `anatomy_digest` | vollstaendige KFS-1-Anatomie | Expositionshistorie |
| `exposure_history_digest` | relevante geordnete A/B/Gap-Vorgeschichte | Bewertung |
| `measurement_record_digest` | Messrollenbindung und Validierungszustand | Funktionsnachweis |

Digestgleichheit bedeutet nur Bytegleichheit des gebundenen Inhalts.
Digestungleichheit ist kein Nachweis einer funktionalen Differenz.

## Fail-Closed-Gruende

Ein Record wird mit `validation_status = invalid` abgelehnt, sobald mindestens
einer dieser kanonischen Gruende gilt:

- `UNKNOWN_SCHEMA_OR_VERSION`;
- `MISSING_OR_UNKNOWN_FIELD`;
- `NONCANONICAL_SERIALIZATION`;
- `DUPLICATE_CARRIER_OR_EDGE_ID`;
- `EDGE_ID_GEOMETRY_MISMATCH`;
- `NEGATIVE_OR_NONFINITE_RESOURCE_ROLE`;
- `RESOURCE_CAPACITY_MISMATCH`;
- `RESOURCE_DOUBLE_COUNTING`;
- `FIELD_REFERENCE_MISMATCH`;
- `ANATOMY_DIGEST_MISMATCH`;
- `EXPOSURE_HISTORY_MISSING_OR_MISMATCHED`;
- `UNREGISTERED_MEASUREMENT_ROLE`;
- `READ_SCOPE_NOT_PASSIVE`;
- `RAW_DATA_LABEL_TARGET_OR_SEQUENCE_BUFFER_PRESENT`;
- `DIGEST_MISMATCH`.

Bei mehreren Fehlern werden alle festgestellten Gruende lexikographisch
geordnet protokolliert. Ein ungueltiger Record darf nicht repariert,
uminterpretiert oder in einen Vergleich aufgenommen werden.

## Vergleichsbindung

Kandidat und zustandsbehaftete Baselines sind nur vergleichbar, wenn ihre
Records mindestens dieselbe registrierte Geometrie, denselben relevanten
Feldprobenraum und eine formal aequivalente Expositionshistorie ausweisen.
Nicht zutreffende Ressourcenrollen einer Baseline werden explizit als nicht
vorhandene Anatomie behandelt; sie werden nicht durch erfundene Null-Ledger
an KFS-1 angeglichen.

## Erlaubte Vertragstests

S1-MY erlaubt spaeter nur statische Tests auf:

- Vollstaendigkeit und Eindeutigkeit der Pflichtfelder;
- stabile kanonische Serialisierung und Digests;
- getrennte Digestrollen ohne Zirkularitaet;
- lokale Erhaltungsidentitaet pro Kante;
- unveraenderte Anatomie- und Feldreferenzen;
- aequivalente Expositionshistorie;
- passive Messrollen;
- deterministische Fail-Closed-Ablehnung.

Nicht erlaubt sind Tests auf Wirkung, Abschwaechung, Interferenz, Lernen,
Systemfaehigkeit oder hypothetische MCM-Memory.

## Ergebnis von S1-MY

S1-MY bindet reproduzierbare Recordgrenzen fuer KFS-1, ohne den Kandidaten
funktional aufzuwerten. Damit ist die Ueberlegung technisch weiterverfolgbar:
Spaetere Dynamik kann gegen feste Anatomie, faire Vorgeschichte und getrennte
Baselines geprueft werden.

## Naechster erlaubter Schritt

Der naechste Schritt ist S1-MZ, ausschliesslich als statischer Validator- und
Fixturevertrag fuer S1-MY. Er darf gueltige Minimalrecords, einzelne
Ungueltigkeitsfaelle, Digeststabilitaet und Fail-Closed-Verhalten festlegen.
Gleichung, Parameter, Runtime, Feldlauf und Funktionsentscheidung bleiben
gesperrt.
