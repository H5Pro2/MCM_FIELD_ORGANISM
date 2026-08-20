# S1-NP G2/D3 Schema-, Digest- und Fail-Closed-Validatorvertrag

## Status

S1-NP bindet ausschliesslich das maschinenlesbare Schema, die Digestgrenzen
und das spaetere Fail-Closed-Validatorverhalten fuer die S1-NO-
Einkantenanatomie. Der Schritt implementiert oder fuehrt keinen Validator aus
und bindet keine Dynamik, Admissibilitaetsfunktion, Parameter, Runtime oder
Feldrueckwirkung.

Entscheidung:

```text
G2_D3_SCHEMA_DIGEST_AND_FAIL_CLOSED_VALIDATOR_CONTRACT_BOUND
```

## Additive Schemagrenze

D3 erhaelt ein eigenes additives Recordformat:

```text
schema_id = g2_d3_anatomy_record
schema_version = s1np.v1
```

Das bestehende `kfs1_anatomy_record` der Version `s1my.v1` wird weder
veraendert noch uminterpretiert. Seine Dreirollenrecords bleiben gueltige
aggregierte Baseline- und Kompatibilitaetsrecords. Ein D3-Record darf nicht
unter der alten Schema-ID gespeichert werden.

## Kanonische Serialisierung

Ein spaeterer Validator muss exakt die vorhandene reine KFS-1-Konvention
verwenden:

- JSON-Grundtypen und Stringschluessel;
- lexikographisch sortierte Objektschluessel;
- UTF-8 ohne BOM;
- keine ueberfluessigen Leerzeichen;
- endliche Zahlen ohne negative Null;
- keine impliziten Standardwerte oder unbekannten Zusatzfelder;
- SHA-256 als kleingeschriebener Digest mit 64 Hexzeichen;
- unveraenderte Eingabebytes als Pruefgegenstand.

Nichtkanonische Bytes werden abgelehnt und nicht neu serialisiert oder
repariert.

## D3-Anatomierecord

Jeder `g2_d3_anatomy_record` besitzt genau diese Pflichtfelder:

| Feld | Bindung |
|---|---|
| `schema_id` | exakt `g2_d3_anatomy_record` |
| `schema_version` | exakt `s1np.v1` |
| `candidate_class_id` | exakt `G2_CONSERVATIVE_BOUND_SUBPARTITION` |
| `geometry_digest` | registrierte lokale Geometrie |
| `field_reference_digest` | registrierter read-only S/H-Probenraum |
| `edge_id` | registrierte kanonische Einkantenidentitaet |
| `carrier_a_id` | erster kanonischer Traeger |
| `carrier_b_id` | zweiter kanonischer Traeger |
| `capacity` | positive endliche Gesamtkapazitaet |
| `free` | nichtnegative freie Ressource |
| `bound_unconfigured` | nichtnegative unkonfigurierte gebundene Ressource |
| `bound_configured` | nichtnegative konfigurierte gebundene Ressource |
| `blocked` | nichtnegative blockierte Ressource |
| `aggregate_projection_digest` | Digest der abgeleiteten Dreirollenprojektion |
| `resource_account_digest` | Digest der vollstaendigen D3-Ressourcenunterteilung |
| `anatomy_record_digest` | Digest des vollstaendigen Records ohne dieses Feld |

Listen, Mehrkantenfelder, Nachbarschaftsrollen und gespeichertes aggregiertes
`bound` sind unzulaessig.

## Digestpayloads

### D3-Ressourcenkonto

`resource_account_digest` bindet kanonisch genau:

```text
edge_id
capacity
free
bound_unconfigured
bound_configured
blocked
```

### Aggregierte Projektion

Vor der Digestbildung wird nur der abgeleitete Wert berechnet:

```text
bound = bound_unconfigured + bound_configured
```

`aggregate_projection_digest` bindet danach exakt den bestehenden
S1-MY-Ressourcenpayload:

```text
edge_id
capacity
free
bound
blocked
```

Damit muss der Projektionsdigest bitgleich zum
`resource_account_digest` eines wertgleichen alten Dreirollen-Kantenrecords
sein. Der alte Record erhaelt keine D3-Unterrollen.

### Vollstaendiger Record

`anatomy_record_digest` bindet alle Pflichtfelder ausser sich selbst. Der
Digest darf weder einen Validierungsstatus noch ein spaeteres Ergebnis
enthalten.

Kein Digest ist selbstbeziehend. Ein falscher deklarierter Digest wird nicht
durch einen berechneten Wert ersetzt.

## Registrygrenze

Eine spaetere unveraenderliche D3-Registry enthaelt nur:

- Schema-ID und Version;
- Kandidatenklassen-ID;
- registrierte Geometrie, Kante und kanonisches Traegerpaar;
- registrierten Feldreferenzdigest;
- die C0/C1-Fixture-IDs und ihre statischen Erwartungsrollen;
- kanonische Pruefphasen und Fehlercodes.

Die Registry enthaelt keine Felddaten, Rohdaten, Expositionssequenz,
Admissibilitaetsfunktion, Dynamikparameter oder Ergebniswerte.

## Reiner Einzelrecord-Validator

Die spaetere reine API-Rolle lautet:

```text
validate_g2_d3_anatomy_record(raw_bytes, registry)
-> G2D3ValidationReceipt
```

Sie muss:

1. den SHA-256-Digest der unveraenderten Eingabebytes bilden;
2. kanonische Byteform und exakte Pflichtfelder pruefen;
3. Schema, Klasse, Geometrie, Kante und Feldreferenz pruefen;
4. Endlichkeit, Nichtnegativitaet und Vierrollenerhaltung pruefen;
5. Aggregation und alle drei Digests getrennt pruefen;
6. sichere Fehlercodes sortiert und ohne Duplikate ausgeben;
7. niemals Werte ergaenzen, normalisieren, reparieren oder mutieren.

## Reiner F1-Paarvalidator

Die zweite spaetere API-Rolle lautet:

```text
validate_g2_d3_f1_pair(c0_raw_bytes, c1_raw_bytes, registry)
-> G2D3PairValidationReceipt
```

Sie darf nur zwei einzeln gueltige Records vergleichen und muss pruefen:

- C0 entspricht exakt `(free,unconfigured,configured,blocked)=(0.5,0.5,0,0)`;
- C1 entspricht exakt `(0.5,0,0.5,0)`;
- Schema, Klasse, Geometrie, Feldreferenz, Kante und Kapazitaet sind bitgleich;
- beide `aggregate_projection_digest`-Werte sind bitgleich;
- die berechnete reine Ablation von C1 entspricht C0 in allen
  Ressourcenrollen;
- die Eingaberecords bleiben unveraendert.

Der Paarvalidator berechnet weder `local_admissible_engagement` noch eine
F1-Entscheidung. Er prueft nur die statische Vergleichbarkeit.

## Pruefphasen

Die gebundene Reihenfolge lautet:

```text
byte_intake
schema_validation
identity_validation
ledger_validation
projection_validation
digest_validation
pair_validation
validation_receipt
```

Beim Einzelrecord bleibt `pair_validation` explizit `not_applicable`. Ein
frueher Fehler verhindert nur abhaengige Folgepruefungen; unabhaengig sicher
feststellbare Fehler werden weiterhin gesammelt.

## Validierungsbelege

### Einzelrecordbeleg

`G2D3ValidationReceipt` bindet:

```text
receipt_schema_id = g2_d3_validation_receipt
receipt_schema_version = s1np.v1
input_bytes_digest
declared_record_schema_id oder unreadable
validation_status = valid oder invalid
completed_checks
failure_reasons
computed_resource_account_digest oder not_computable
computed_aggregate_projection_digest oder not_computable
computed_anatomy_record_digest oder not_computable
validator_contract_digest
validation_receipt_digest
```

### Paarbeleg

`G2D3PairValidationReceipt` bindet:

```text
receipt_schema_id = g2_d3_pair_validation_receipt
receipt_schema_version = s1np.v1
c0_input_bytes_digest
c1_input_bytes_digest
c0_record_digest oder not_computable
c1_record_digest oder not_computable
aggregate_projection_digest oder not_computable
validation_status = valid oder invalid
completed_checks
failure_reasons
validator_contract_digest
pair_validation_receipt_digest
```

Alle Belegdigests schliessen ihr eigenes Digestfeld aus.

## Kanonische Fehlercodes

```text
D3_UNKNOWN_SCHEMA_OR_VERSION
D3_MISSING_OR_UNKNOWN_FIELD
D3_NONCANONICAL_SERIALIZATION
D3_CLASS_ID_MISMATCH
D3_EDGE_ID_GEOMETRY_MISMATCH
D3_FIELD_REFERENCE_MISMATCH
D3_NEGATIVE_OR_NONFINITE_RESOURCE_ROLE
D3_CAPACITY_MISMATCH
D3_FORBIDDEN_PAYLOAD_PRESENT
D3_RESOURCE_ACCOUNT_DIGEST_MISMATCH
D3_AGGREGATE_PROJECTION_DIGEST_MISMATCH
D3_ANATOMY_RECORD_DIGEST_MISMATCH
D3_PAIR_RECORD_INVALID
D3_PAIR_IDENTITY_MISMATCH
D3_C0_FIXTURE_MISMATCH
D3_C1_FIXTURE_MISMATCH
D3_PAIR_AGGREGATE_MISMATCH
D3_ABLATION_MISMATCH
```

Fehlercodes werden lexikographisch sortiert. Fehlende Voraussetzungen duerfen
keine erfundenen Folgedefekte erzeugen.

## Gebundene Fixtureklassen

### Positive Einzelrecords

| Fixture | Rolle |
|---|---|
| `D3_V_C0` | exakter S1-NO-C0-Record |
| `D3_V_C1` | exakter S1-NO-C1-Record |
| `D3_V_MIXED` | gueltige dyadische gemischte Unterteilung bei gleicher Gesamtidentitaet |

### Positive Paarpruefung

| Fixture | Rolle |
|---|---|
| `D3_V_F1_PAIR` | `D3_V_C0` und `D3_V_C1`, bitgleiche Aggregation und exakte Ablation |

### Einzeldefekte

Mindestens je ein Fixture bindet genau eine Mutation fuer:

- unbekannte Version;
- fehlendes Pflichtfeld;
- unbekanntes oder verbotenes Zusatzfeld;
- nichtkanonische Bytes;
- falsche Klasse, Geometrie, Kante oder Feldreferenz;
- negative, nicht endliche oder boolesche Ressource;
- verletzte Vierrollenerhaltung;
- falschen Ressourcenkonto-, Projektions- oder Recorddigest.

### Paardefekte

Mindestens je ein Fixture bindet:

- einen einzeln ungueltigen Arm;
- abweichende Identitaetsfelder;
- falsche C0- oder C1-Ressourcenrollen;
- verschiedene Aggregatprojektionen;
- eine C1-Unterteilung, deren reine Ablation nicht C0 ergibt.

Konkrete kanonische Bytes und erwartete Digests werden erst im spaeteren
Implementierungsvertrag materialisiert. Sie sind statische Testwerte und
keine Dynamikparameter.

## Erlaubte Testmatrix

Eine spaetere fokussierte Abnahme darf nur pruefen:

- drei positive Einzelrecords und ein positives Paar;
- jeden Einzel- und Paardefekt mit genau den sicheren Fehlercodes;
- Digeststabilitaet und Trennung der drei Digestrollen;
- bitgleiche Aggregation von C0 und C1;
- exakte reine Ablation C1 nach C0;
- Eingabeimmutabilitaet und deterministische Wiederholung;
- Abwesenheit von Feld-, Runner-, Audio-/Video-, Netzwerk- und I/O-Pfaden;
- Abwesenheit von Admissibilitaets-, Transfer-, Bildungs- oder
  Funktionsentscheidung.

## Aussagegrenze

S1-NP macht die D3-Anatomie nur maschinenlesbar und pruefbar. Ein gueltiger
Record oder ein gueltiges C0/C1-Paar zeigt keine G2-Wirkung. Es gibt keine
Dynamik, keine Feldwirkung, keine Lernfunktion und keinen Befund zur
hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-NQ darf ausschliesslich den Implementierungsvertrag fuer einen neuen,
isolierten und additiven D3-Schema- und Paarvalidator binden. Er muss
Dateigrenzen, reine APIs, konkrete Fixturebytes, erwartete Digests, ein
endliches Testbudget und die unveraenderte bestehende KFS-1-/DTS-1-Grenze
festlegen.

Validatorimplementierung, Admissibilitaetsfunktion, Dynamik und
Feldrueckwirkung bleiben in S1-NQ noch gesperrt.
