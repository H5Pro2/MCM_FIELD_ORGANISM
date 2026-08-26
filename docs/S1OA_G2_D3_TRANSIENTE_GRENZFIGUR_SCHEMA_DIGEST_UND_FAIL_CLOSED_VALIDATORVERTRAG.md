# S1-OA G2/D3 transiente Grenzfigur: Schema-, Digest- und Fail-Closed-Validatorvertrag

## Status

S1-OA bindet ausschliesslich ein maschinenlesbares Schema, getrennte Digests
und das spaetere reine Fail-Closed-Validatorverhalten fuer die transiente
S1-NZ-Zweiintervallgrenze. Der Schritt implementiert oder fuehrt keinen
Validator aus und bindet keine Umordnungsmenge, Bildungsgleichung, Runtime
oder Feldwirkung.

Entscheidung:

```text
G2_D3_TRANSIENT_BOUNDARY_SCHEMA_DIGEST_AND_VALIDATOR_CONTRACT_BOUND
```

## Additives transientes Schema

Die Grenzfigur erhaelt ein eigenes additives Recordformat:

```text
schema_id = g2_d3_transient_boundary_record
schema_version = s1oa.v1
```

Das bestehende `g2_d3_anatomy_record/s1np.v1` und sein akzeptierter Validator
bleiben unveraendert. Ein Grenzrecord ist weder ein D3-Anatomierecord noch ein
persistierbarer Feldzustand.

## Kanonische Byteform

Ein spaeterer Validator verwendet exakt die bestehende reine Konvention:

- UTF-8 ohne BOM und ohne abschliessenden Zeilenumbruch;
- lexikographisch sortierte JSON-Objektschluessel;
- keine ueberfluessigen Leerzeichen;
- nur JSON-Grundtypen mit Stringschluesseln;
- endliche Zahlen ohne negative Null;
- nichtnegative ganzzahlige Ordinale, Bool ausgeschlossen;
- exakte Pflichtfelder ohne unbekannte Ergaenzungen;
- SHA-256 als 64 kleingeschriebene Hexzeichen;
- keine Reparatur oder Neuserialisierung der Eingabebytes.

Nichtkanonische Bytes werden abgelehnt und nicht normalisiert.

## Pflichtfelder des Grenzrecords

Jeder Record besitzt exakt:

```text
schema_id
schema_version
candidate_class_id

current_edge_id
current_field_reference_digest
current_interval_ordinal
current_orientation
current_interval_closed
current_contact_digest

prior_edge_id
prior_field_reference_digest
prior_interval_ordinal
prior_orientation
prior_interval_closed
prior_contact_digest

source_d3_anatomy_record_digest
boundary_record_digest
```

`candidate_class_id` lautet exakt:

```text
G2_D3_TRANSIENT_LOCAL_CONTINUATION_GATED_REPARTITION
```

Aktuelle Kontaktfelder sind niemals `null`. Beim ersten Kontakt sind alle
sechs Vorgaengerfelder exakt `null`. Bei jedem folgenden Kontakt sind alle
sechs Vorgaengerfelder vollstaendig und nicht `null`. Gemischte Nullbelegung
ist unzulaessig.

Der Ereigniswert ist ausdruecklich kein Eingabefeld. Ebenso fehlen
Umordnungsbetrag, D3-Nachzustand und Ergebnisentscheidung.

## Kontakt-Digestpayload

Aktueller und vorheriger Kontaktdigest verwenden denselben normalisierten
Payload:

```text
edge_id
field_reference_digest
interval_ordinal
orientation
interval_closed
```

Fuer den aktuellen Digest werden die `current_*`-Werte, fuer den vorherigen
Digest die `prior_*`-Werte eingesetzt. Beim ersten Kontakt ist
`prior_contact_digest=null`; es wird kein Nullkontaktdigest erfunden.

Der Digest bindet nur den reduzierten technischen Kontakt. Er enthaelt keine
Rohdaten, S/H-Folge, Armkennung oder Ereignisrolle.

## Grenzrecorddigest

`boundary_record_digest` bindet alle Pflichtfelder ausser sich selbst. Er
schliesst insbesondere beide Kontaktdigests und den
`source_d3_anatomy_record_digest` ein.

Kein Digest ist selbstbeziehend. Ein falscher deklarierter Digest wird nicht
durch den berechneten Wert ersetzt.

## D3-Quellbindung

Die spaetere reine Validierung erhaelt Grenzbytes und D3-Quellbytes getrennt:

```text
validate_g2_d3_transient_boundary(
    boundary_raw_bytes,
    d3_raw_bytes,
    boundary_registry,
    d3_registry,
) -> G2D3TransientBoundaryValidationReceipt
```

Zuerst muss `d3_raw_bytes` durch den akzeptierten
`validate_g2_d3_anatomy_record`-Pfad gueltig sein. Danach muessen exakt gelten:

```text
source_d3_anatomy_record_digest
= validierter D3-Anatomierecorddigest

current_edge_id = D3 edge_id
current_field_reference_digest = D3 field_reference_digest
```

Bei vorhandenem Vorgaenger muessen auch dessen Kante und Feldreferenz mit dem
aktuellen Kontakt und D3 uebereinstimmen. Der Grenzvalidator darf D3 nicht
mutieren oder neu serialisieren.

## Registrygrenze

Eine spaetere unveraenderliche S1-OA-Registry bindet nur:

- Schema-ID und Version;
- Kandidatenklassen-ID;
- Orientierungen `X` und `Y`;
- Ereignisrollen `NO_PREDECESSOR`, `LOCAL_CONTINUATION`, `LOCAL_SWITCH`;
- erlaubte Validierungsphasen und Fehlercodes;
- den akzeptierten D3-Validatorvertragsdigest;
- den eigenen Validatorvertragsdigest.

Sie enthaelt keine Kontaktfolge, Arm-ID, Felddaten, D3-Ressourcenwerte,
Umordnungsmenge, Rate, Schwelle oder Ergebniswerte.

Der S1-OA-Validatorvertragsdigest lautet:

```text
7a84b6f6dee9ba8f6e7f5cce9ee7655a63104cda669aabe35101072036fdebd0
```

Er ist SHA-256 der ASCII-Kennung
`g2.d3.transient-boundary.validator.contract.s1oa.v1`.

Der akzeptierte und unveraenderte D3-Validatorvertragsdigest lautet:

```text
b113a2deb46d3f42e07a110335d6a665a89d8a39686a1e86700e8e971bf6ab9c
```

## Reine Validierungsreihenfolge

Die gebundene Reihenfolge lautet:

```text
byte_intake
schema_validation
contact_digest_validation
d3_source_validation
adjacency_validation
event_classification
persistence_guard
validation_receipt
```

Ein frueher Fehler sperrt nur abhaengige Folgepruefungen. Unabhaengig sicher
feststellbare Fehler werden weiterhin gesammelt. Abgeleitete Folgefehler
duerfen nicht erfunden werden.

## Ereignisklassifikation

Nur nach vollstaendiger Schema-, Kontakt-, D3- und Nachbarschaftsvalidierung
wird genau ein Ereignis berechnet:

```text
all prior fields null
+ current_interval_ordinal = 0
-> NO_PREDECESSOR

complete prior fields
+ current_interval_ordinal = prior_interval_ordinal + 1
+ prior_orientation = current_orientation
-> LOCAL_CONTINUATION

complete prior fields
+ current_interval_ordinal = prior_interval_ordinal + 1
+ prior_orientation != current_orientation
-> LOCAL_SWITCH
```

X und Y werden nur auf Gleichheit verglichen. Es gibt keine
orientierungsspezifische Ausgaberegel und keinen vierten Sachwert.

## Verbotene Eingabe- und Persistenzfelder

Fail-closed verboten sind insbesondere:

```text
event_role
event_history
history_id
arm_id
sequence
sequence_buffer
continuation_count
switch_count
formation_amount
transfer_amount
post_d3_state
raw_data
raw_audio
raw_video
label
target
reward
readout
```

`event_role` bis `post_d3_state` erzeugen
`OA_TRANSIENT_PERSISTENCE_FIELD_PRESENT`. `raw_data` bis `readout` erzeugen
`OA_FORBIDDEN_PAYLOAD_PRESENT`. Sie werden nicht nur als unbekannte
Zusatzfelder behandelt. Verschachtelte Vorkommen sind ebenfalls verboten.

## Passiver Einzelgrenzenbeleg

`G2D3TransientBoundaryValidationReceipt` bindet genau:

```text
receipt_schema_id = g2_d3_transient_boundary_validation_receipt
receipt_schema_version = s1oa.v1
boundary_input_bytes_digest
d3_input_bytes_digest
declared_boundary_schema_id oder unreadable
source_d3_validation_receipt_digest oder not_computable
source_d3_anatomy_record_digest oder not_computable
computed_current_contact_digest oder not_computable
computed_prior_contact_digest oder not_applicable oder not_computable
computed_boundary_record_digest oder not_computable
event_role oder not_computable
validation_status = valid oder invalid
completed_checks
failure_reasons
validator_contract_digest
boundary_validation_receipt_digest
```

Der Beleg ist unveraenderlich und digestiert alle eigenen Felder ausser seinem
Digest. Er liegt ausschliesslich auf einer passiven Test- und Auditoberflaeche.
Er darf nicht an D3, O3, Feld, Baseline oder eine folgende Grenzvalidierung
zurueckgegeben werden.

Die Ereignisrolle im Beleg ist externe technische Evidenz. Sie ist kein
persistenter Kandidatenzustand.

## Kanonische Fehlercodes

```text
OA_UNKNOWN_SCHEMA_OR_VERSION
OA_MISSING_OR_UNKNOWN_FIELD
OA_NONCANONICAL_SERIALIZATION
OA_CLASS_ID_MISMATCH
OA_FORBIDDEN_PAYLOAD_PRESENT
OA_CURRENT_CONTACT_DIGEST_MISMATCH
OA_PRIOR_NULLABILITY_MISMATCH
OA_PRIOR_CONTACT_DIGEST_MISMATCH
OA_D3_SOURCE_RECORD_INVALID
OA_D3_SOURCE_DIGEST_MISMATCH
OA_EDGE_OR_FIELD_REFERENCE_MISMATCH
OA_INVALID_INTERVAL_ORDINAL
OA_INTERVAL_NOT_CLOSED
OA_UNKNOWN_ORIENTATION
OA_BOUNDARY_RECORD_DIGEST_MISMATCH
OA_TRANSIENT_PERSISTENCE_FIELD_PRESENT
```

Fehlercodes werden lexikographisch sortiert und ohne Duplikate ausgegeben.

## Fail-Closed-Pruefungen

Der Validator muss insbesondere ablehnen:

- nichtkanonische oder nicht lesbare Bytes;
- fehlende, unbekannte oder verbotene Felder;
- falsches Schema oder falsche Kandidatenklasse;
- falsche Kontakt- oder Grenzrecorddigests;
- ungueltige oder gemischt-nullbare Vorgaengerrollen;
- negative, boolesche, nichtganzzahlige oder nicht aufeinanderfolgende
  Ordinale;
- nicht abgeschlossene aktuelle oder vorherige Intervalle;
- unbekannte Orientierungen;
- verschiedene Kanten oder Feldreferenzen;
- ungueltigen oder digestfremden D3-Quellrecord;
- jedes bereits in der Eingabe vorgegebene Ereignis;
- jeden Versuch, Kontakt- oder Ereignisgeschichte als Kandidatenzustand
  einzubetten.

Bei einem ungueltigen Record gilt:

```text
validation_status = invalid
event_role = not_computable
```

Es gibt keine Teilklassifikation und keine D3-Aenderung.

## Erlaubte spaetere Testgrenze

Eine spaetere fokussierte Abnahme darf nur pruefen:

- alle sechs gueltigen Tabellenfaelle;
- die drei S1-NZ-Vierereignismuster aus getrennten Einzelbelegen;
- kanonische Kontakt-, Grenz- und Belegdigests;
- ersten Kontakt und vollstaendige Vorgaengernullbarkeit;
- direkte Nachbarschaft, Edge-/Field-/D3-Bindung;
- Spiegelinvarianz der Fortsetzungsrollen;
- jeden sicheren Fehlercode mit vorab gebundener Mutation;
- deterministische Wiederholung und Eingabeimmutabilitaet;
- Abwesenheit transienter Felder im D3-Record;
- passive Nicht-Rueckfuehrbarkeit des Belegs;
- Abwesenheit von Feld-, Transfer-, Runner-, Medien-, Netzwerk- und
  Dateischreibpfaden.

Nicht erlaubt sind Umordnungsbetrag, D3-Nachzustand, O3-Auswertung,
Bildungsgleichung, Abschwaechung, Interferenz oder Feldwirkung.

## Aussagegrenze

S1-OA bindet nur Schema, Digests und spaeteres Validatorverhalten. Es gibt
noch keinen Grenzvalidator, kein klassifiziertes Ereignis, keine Umordnung,
Bildung oder Feldwirkung, keine Lernfunktion und keinen Befund zur
hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

S1-OB darf ausschliesslich den Implementierungs-, Fixture- und
Testbudgetvertrag fuer den isolierten S1-OA-Validator binden. Er muss
Dateigrenzen, reine APIs, konkrete kanonische Grenzbytes, erwartete Digests,
Einzelmutationen und ein endliches Einmalbudget vorab schliessen.

S1-OB darf den Validator noch nicht implementieren oder ausfuehren und keine
Umordnungsmenge, Rate, Schwelle, Bildungsgleichung, Runtime oder Feldwirkung
einfuehren.
