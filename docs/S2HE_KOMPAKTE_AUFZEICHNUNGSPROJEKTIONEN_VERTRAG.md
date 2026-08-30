# S2-HE: Vertrag kompakter Aufzeichnungsprojektionen

Status: `S2HE_STATIC_COMPACT_RECORDING_PROJECTION_CONTRACT_BOUND`

## Zweck und Grenze

S2-HE bindet ausschliesslich drei kompakte Aufzeichnungsprojektionen fuer den
privaten S2-GT-Laufpfad:

1. `CompactCompositeFormationReceiptV1`;
2. `CompactS2GCProjectionReceiptV1`;
3. `CompactS2GIProjectionReceiptV1`.

Die Projektionen sind Belegformen. Sie sind keine neuen Funktionsobjekte und
keine Speicherzustaende. Die vollstaendigen In-Memory-Objekte
`B4TSPM1StepResult`, `PerceptualContextBundle` und `TwoAreaContextBundle`
bleiben unveraendert und werden unveraendert an ihre funktionalen Nachfolger
weitergereicht.

Nicht freigegeben sind Implementierung, Import, Test, Zustandsaufruf,
Rezeptorausfuehrung oder erneuter Funktionslauf. S2-HC bleibt dauerhaft
`NOT_EVALUABLE`.

## Gemeinsame Regeln

Fuer alle drei Projektionen gilt:

- Die Recorderhuelle bleibt unveraendert und enthaelt `schema`,
  `operation_id`, `owner_id`, `reservation_digest`, `start_event_digest` und
  `artifact.result`.
- Die Projektion wird ausschliesslich aus dem bereits vollstaendig validierten
  In-Memory-Ergebnis derselben Operation erzeugt.
- Kein nachfolgender Funktionsschritt darf aus der kompakten Projektion einen
  Zustand, Kandidaten oder Wertevektor rekonstruieren.
- Nicht aufgezeichnete Vollobjekte werden nur dort durch Digests referenziert,
  wo ihre Quelle im laufenden In-Memory-Pfad und ihre vorangehende
  Aufzeichnungsquelle eindeutig gebunden sind.
- Der semantische Objekt- oder Ergebnisdigest und der vom Recorder erzeugte
  Artefaktdigest bleiben getrennte Rollen.
- Jede Projektion besitzt einen eigenen `projection_digest` ueber alle
  Projektionsfelder ausser diesem Digest.
- Alle positionalen Listen besitzen die hier festgelegte Reihenfolge. Ein
  Umordnen ist ungueltig.
- Jede Huelle muss kanonisches ASCII-JSON mit genau einem abschliessenden LF
  sein.
- Zusaetzlich zur unveraenderten Registrygrenze von 4.096 Byte gilt fuer jede
  der drei Huellen `COMPACT_PROJECTION_MAX_ARTIFACT_BYTES = 3200`.
- Ueberschreitungen bleiben `E008`. Die Fehlerentscheidung aus S2-GY/S2-GZ
  bleibt unveraendert.
- Die bestehenden Erfolgs- und Gesamtbudgets werden nicht erhoeht.

Der Verifikator verwendet weiterhin die strengere Bedingung
`Dateigroesse < 4096`. Die effektive Registryobergrenze betraegt deshalb 4.095
Byte.

## Formation

### Quelle und Fortsetzung

`CompactCompositeFormationReceiptV1` wird aus genau einem validierten
`B4TSPM1StepResult` gebildet. Der vollstaendige `poststate` verbleibt im
Runner und ist die einzige Quelle fuer die naechste Formation oder Probe.

Direkte Eltern sind:

- der START-Ereignisdigest der eigenen Formation;
- der Artefaktdigest des unmittelbar vorausgehenden kompakten
  `ReceptorReceipt`;
- der semantische Composite-Vorzustandsdigest.

Die naechste Formation muss ihren Vorzustandsdigest gegen
`composite_poststate_digest` pruefen. Der Ereignisgraph bindet zusaetzlich den
Artefaktdigest dieser Formation. Weder der Nachzustand noch einzelne Slots
werden aus dem Receipt wieder aufgebaut.

### Exakte Felder

```text
schema
execution_plan_digest
source_digest
receptor_receipt_artifact_digest
config_digest
input_digest
composite_prestate_digest
composite_poststate_digest
b4_event
b4_slot_id
b4_poststate_digest
tspm_result_digest
tspm_receipt_digest
tspm_poststate_digest
step_receipt_digest
generation
parent_state_digest
last_input_digest
ledger_operation
ledger_counts
resource_ledger_digest
coordinator_owner_ids
owner_authorized_digests
owner_status
owner_attempt_count
owner_use_count
owner_committed_result_digest
owner_state_digest
result_digest
projection_digest
```

`ledger_counts` besitzt exakt diese Reihenfolge:

```text
common_projection_terms
b4_functional_write_words
b4_functional_distance_terms
tspm_functional_write_words
tspm_functional_distance_terms
coordinator_validation_terms
coordinator_digest_operations
coordinator_write_words
total_functional_write_words
total_functional_distance_terms
total_control_terms
```

`coordinator_owner_ids` ist exakt
`owner_id, authorization_id, consumption_id`.
`owner_authorized_digests` ist exakt
`authorized_config_digest, authorized_prestate_digest,
authorized_input_digest`.

Die Projektion ist nur fuer einen erfolgreichen Ownerzustand gueltig:
`CONSUMED`, `attempt_count = 1`, `use_count = 1`, gueltiger
`committed_result_digest`, kein Fehlercode und kein Fehlerdigest. Die beiden
leeren Fehlerfelder werden nicht erneut gespeichert, muessen aber vor der
Projektion am Vollobjekt geprueft werden.

Nicht aufgezeichnet werden B4-Eintraege, Fast-Slots, PPB-1-Baenke,
Prototypwerte oder der vollstaendige Composite-Nachzustand. Fuer die spaetere
Funktionsauswertung erforderliche Ereignis-, Owner-, Generation-, Komponenten-
und Ressourcenangaben bleiben explizit erhalten.

## S2-GC

### Quelle und Fortsetzung

`CompactS2GCProjectionReceiptV1` wird aus genau einem validierten
`PerceptualContextBundle` erzeugt. Der vollstaendige Bundlegegenstand bleibt
der einzige In-Memory-Eingang fuer S2-GI.

Direkte Eltern sind:

- der eigene START-Ereignisdigest;
- der Artefaktdigest des zugehoerigen `ContextReadOnlyReceipt`;
- dessen semantischer `finding_digest`.

Die vollstaendigen Komponentenwerte sind bereits im gebundenen
`ContextReadOnlyReceipt` vorhanden. S2-GC zeichnet deshalb ihre Werte-,
Quellen- und Komponentendigests sowie die funktionalen Auswahlmerkmale auf,
aber nicht dieselben Werte erneut. Weder Runner noch Verifikator duerfen aus
einem Digest fehlende Werte rekonstruieren.

### Exakte Felder

```text
schema
execution_plan_digest
source_finding_artifact_digest
source_finding_digest
contract_digest
binding_digest
config_digest
composite_state_digest
probe_digest
source_digest
role_statuses
role_absence_reasons
role_finding_digests
candidate_digests
component_roles
component_digests
component_source_digests
component_values_digests
component_native_distances
component_functional_distances
component_support_counts
component_stable_flags
component_last_selected_steps
component_formation_indices
sequence_status
sequence_reference_digests
sequence_finding_digest
ledger_counts
resource_ledger_digest
prestate_digest
poststate_digest
automatic_selection
bundle_digest
projection_digest
```

Die Rollenreihenfolge ist exakt
`B4_RECENT, TSPM_FAST, TSPM_SLOW`. Alle Rollenlisten sind positionsgleich.
Komponenten folgen der Rollenreihenfolge; innerhalb von `TSPM_SLOW` gilt
`AUDITORY, VISUAL`. Alle Komponentenlisten sind positionsgleich.

`ledger_counts` besitzt exakt diese Reihenfolge:

```text
validated_evidence_records
validated_digest_count
role_projection_count
candidate_count
component_count
value_count
sequence_reference_count
digest_operation_count
```

Damit bleiben Status, gueltige Abwesenheit, Distanzen, Support, Stabilitaet,
zeitliche Auswahl und Ressourcen explizit auswertbar. Der konkrete Werteinhalt
bleibt ueber den vorausgehenden read-only Befund vollstaendig vorhanden und
wird durch `component_values_digests` eindeutig gebunden.

S2-GI muss beim START sowohl `bundle_digest` als auch den Recorder-
Artefaktdigest dieser kompakten S2-GC-Aufzeichnung binden.

## S2-GI

### Quelle und Fortsetzung

`CompactS2GIProjectionReceiptV1` wird aus genau einem validierten
`TwoAreaContextBundle` erzeugt. Der vollstaendige Bundlegegenstand bleibt der
einzige In-Memory-Eingang fuer Kontextverbraucher und direkte Baseline.

Direkte Eltern sind:

- der eigene START-Ereignisdigest;
- der Artefaktdigest des zugehoerigen kompakten S2-GC-Receipts;
- der semantische `source_bundle_digest`.

### Exakte Felder

```text
schema
execution_plan_digest
source_s2gc_artifact_digest
source_bundle_digest
contract_digest
binding_digest
config_digest
composite_state_digest
probe_digest
source_digest
area_roles
area_finding_digests
a_recent_status
a_recent_finding_digest
a_fast_status
a_fast_finding_digest
a_sequence_status
a_sequence_finding_digest
b_stable_status
b_candidate_digest
b_component_digests
b_values_digests
b_source_digests
ledger_counts
source_ledger_digest
resource_ledger_digest
prestate_digest
poststate_digest
automatic_selection
bundle_digest
projection_digest
```

`area_roles` ist exakt `A_RECENT, B_STABLE`. Die B-Komponentenreihenfolge ist
bei vollstaendiger Belegung exakt `AUDITORY, VISUAL`. Bei `ABSENT_VALID` sind
Kandidat und Komponentenlisten leer; es darf kein Inhalt erfunden werden.

`ledger_counts` besitzt exakt diese Reihenfolge:

```text
validated_bundle_count
validated_role_count
candidate_reference_count
component_reference_count
value_reference_count
sequence_reference_count
area_projection_count
digest_operation_count
```

Die nachfolgenden Arme binden sowohl `bundle_digest` als auch den
S2-GI-Artefaktdigest. Funktional erhalten sie weiterhin ausschliesslich den
vollstaendigen unveraenderten In-Memory-Gegenstand. Die Aufzeichnung erzeugt
keine dritte Ebene, keine Auswahl und keine Wertevervollstaendigung.

## Groessenbindung aller Vorkommen

Die Vorausberechnung verwendet kanonisches ASCII-JSON einschliesslich LF und
der vollstaendigen unveraenderten Recorderhuelle. Um eine spaetere neutrale
Lauf-ID nicht von der bisherigen Ownerlaenge abhaengig zu machen, wurde fuer
`owner_id` die maximal zulaessige Laenge von 96 ASCII-Zeichen angesetzt.

### 52 Formation-Receipts

- Schritte 1 bis 9 jeder Geschichte: 2.697 Byte je Huelle.
- Schritte 10 bis 13 jeder Geschichte: 2.710 Byte je Huelle.
- Maximum: 2.710 Byte.
- Reserve zur effektiven 4.095-Byte-Grenze: 1.385 Byte.

Die vollstaendige Operationsliste und Gruppierung ist im maschinenlesbaren
S2-HE-Beleg gebunden.

### Vier S2-GC-Receipts

- `op-0116`, `op-0117`, `op-0118`: stabile Vollform, hoechstens 3.112 Byte.
- `op-0119`: gueltige Abwesenheitsform, hoechstens 2.596 Byte.
- Maximum: 3.112 Byte.
- Reserve zur effektiven 4.095-Byte-Grenze: 983 Byte.

### Vier S2-GI-Receipts

- `op-0120`, `op-0121`, `op-0122`: stabile Vollform, hoechstens 2.977 Byte.
- `op-0123`: gueltige Abwesenheitsform, hoechstens 2.509 Byte.
- Maximum: 2.977 Byte.
- Reserve zur effektiven 4.095-Byte-Grenze: 1.118 Byte.

Alle 60 Vorkommen bleiben zusaetzlich unter der engeren 3.200-Byte-Grenze.
Die kleinste Reserve zur unveraenderten Registrygrenze ist damit nicht mehr
90 Byte, sondern 983 Byte.

## Validierungs- und Nichtzirkularitaetsregeln

Ein spaeterer Materialisierbarkeitsaudit muss fuer jedes konkrete Vorkommen
mindestens pruefen:

1. exakte Datentyp- und Feldquelle im jeweiligen Vollobjekt;
2. kanonische Feldmenge und Positionsreihenfolge;
3. `projection_digest` gegen die Projektion ohne Digest;
4. Recorderhuelle gegen Operation, Owner, Reservierung und START;
5. direkte Elternartefakte und semantische Elterndigests;
6. Nachfolgerbindung an Artefakt- und semantischen Digest;
7. Identitaet der In-Memory-Objekte vor und nach Projektion;
8. Groesse gegen 3.200 und 4.096 Byte;
9. keine Werte-, Zustands- oder Kandidatenrekonstruktion;
10. keine rueckwaerts gerichtete Kante aus Evaluation oder Abschluss.

Der Digestgraph verlaeuft ausschliesslich vorwaerts:

```text
ReceptorReceipt-Artefakt
  -> CompactCompositeFormationReceiptV1
  -> spaeterer Composite-Vorzustandsbezug

ContextReadOnlyReceipt-Artefakt
  -> CompactS2GCProjectionReceiptV1
  -> CompactS2GIProjectionReceiptV1
  -> ArmReceipt
  -> Evaluation
```

Die Evaluation ist keine Quelle einer Aufzeichnungsprojektion.

## Stoppbedingungen

S2-HE gilt im folgenden Audit als nicht materialisierbar, wenn:

- ein Feld nicht direkt im gebundenen Vollobjekt oder seiner aktuellen
  Recorder-/Registryquelle existiert;
- ein fuer die Funktionsauswertung erforderlicher Wert in keiner frueheren
  vollstaendigen Belegquelle vorhanden ist;
- ein Nachfolger zur Funktionsausfuehrung aus einem Digest Inhalte
  rekonstruieren muesste;
- eine der 60 Huellen mehr als 3.200 Byte benoetigt;
- Owner-, Quellen-, Zustands- oder Elternbindung mehrdeutig wird;
- eine Digestkante zyklisch oder evaluierungsabhaengig ist;
- ein bestehendes Budget oder eine Fehlercodeentscheidung geaendert werden
  muesste.

## Entscheidung

Der enge S2-HE-Korrekturvertrag ist statisch gebunden. Er beseitigt noch keinen
Laufblocker, weil keine Implementierung freigegeben ist. Als naechster Schritt
ist ausschliesslich ein statischer Materialisierbarkeits-, Groessen- und
Nichtzirkularitaetsaudit dieser drei Schemas zulaessig. Erst ein bestandener
Audit darf eine getrennte Implementierung und neutrale Qualifikation
begrunden.
