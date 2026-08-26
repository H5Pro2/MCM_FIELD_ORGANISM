# S1-ND KFS-1 Uebergangsrecord-Schema und Digestvertrag

## Status

S1-ND bindet ausschliesslich das maschinenlesbare Schema fuer lokale
KFS-1-Uebergangsrecords, ihre Digestrollen und ihre lueckenlose Verkettung.
Der Schritt implementiert keine Uebergangsregel und enthaelt keine Gleichung,
Rate, Dynamikparameter, Runtimeintegration oder Feldlauf.

Ein gueltiger Uebergangsrecord belegt nur eine konsistente technische
Ereignisbeschreibung. Er belegt nicht, dass KFS-1 eine solche Zustandsaenderung
selbst hervorbringt oder dass daraus eine spaetere Feldwirkung entsteht.

## Recordidentitaet

Jeder Uebergangsrecord besitzt:

| Rolle | Bindung |
|---|---|
| `schema_id` | exakt `kfs1_transition_record` |
| `schema_version` | exakt `s1nd.v1` |
| `candidate_id` | exakt `KFS-1` |
| `event_id` | eindeutige Ereignis-ID innerhalb der registrierten Feldfolge |
| `transition_id` | eine der vier Wechsel- oder drei Stillstands-IDs aus S1-NC |
| `edge_id` | genau eine registrierte lokale Kante |
| `field_interval_id` | Identitaet der technischen Feldgrenze |
| `event_ordinal` | positive, innerhalb der Feldfolge streng steigende Ganzzahl |
| `source_role` | `free`, `bound` oder `blocked` |
| `target_role` | `free`, `bound` oder `blocked` |
| `transfer_amount` | statischer Bilanzwert des Ereignisses, kein Dynamikparameter |
| `pre_ledger` | vollstaendiger lokaler Vorzustand |
| `post_ledger` | vollstaendiger lokaler Nachzustand |
| `anatomy_digest` | Referenz auf die unveraenderte KFS-1-Anatomie |
| `field_reference_digest` | Referenz auf denselben lokalen read-only Feldprobenraum |
| `exposure_history_digest` | Referenz auf die relevante geordnete Vorgeschichte |
| `trigger_class` | die zu `transition_id` registrierte Ausloeserklasse |
| `trigger_observation_digest` | lokaler Beobachtungsdigest oder bei Stillstand exakt `null` |
| `prior_event_digest` | bei erstem Ereignis `null`, sonst Digest des direkten Vorgaengers |
| `event_digest` | Digest des vollstaendigen Records ohne dieses Feld |

`event_id` und `event_ordinal` sind technische Ordnungsrollen. Sie enthalten
keine Rechnerzeit und keine semantische Bewertung.

## Lokales Ledgerschema

`pre_ledger` und `post_ledger` besitzen jeweils genau:

| Feld | Bindung |
|---|---|
| `edge_id` | identisch mit der `edge_id` des Ereignisses |
| `capacity` | endliche, nichtnegative registrierte Kantenkapazitaet |
| `free` | endlicher, nichtnegativer Rollenwert |
| `bound` | endlicher, nichtnegativer Rollenwert |
| `blocked` | endlicher, nichtnegativer Rollenwert |
| `resource_account_digest` | Digest ueber `edge_id`, `capacity`, `free`, `bound`, `blocked` |

Beide Ledger muessen fuer sich die lokale Erhaltungsidentitaet erfuellen. Ihre
Kapazitaet muss bitgleich bleiben.

## Gebundene Wechselpaare

Schema und Rollenpaar muessen exakt zusammenpassen:

| `transition_id` | Quelle | Ziel | `trigger_class` |
|---|---|---|---|
| `LOCAL_CONTACT_BIND` | `free` | `bound` | `LOCAL_CONTACT_OBSERVATION` |
| `LOCAL_BOUND_RELEASE` | `bound` | `free` | `LOCAL_BOUND_RELEASE_OBSERVATION` |
| `LOCAL_REFRACTORY_ENTRY` | `bound` | `blocked` | `LOCAL_BOUND_COMPLETION_OBSERVATION` |
| `LOCAL_REFRACTORY_RELEASE` | `blocked` | `free` | `LOCAL_BLOCKED_RELEASE_OBSERVATION` |
| `HOLD_FREE` | `free` | `free` | `NO_TRIGGER` |
| `HOLD_BOUND` | `bound` | `bound` | `NO_TRIGGER` |
| `HOLD_BLOCKED` | `blocked` | `blocked` | `NO_TRIGGER` |

Tatsaechliche Wechsel verlangen einen positiven endlichen `transfer_amount`
und einen registrierten `trigger_observation_digest`. Stillstand verlangt
`transfer_amount = 0`, `trigger_class = NO_TRIGGER` und
`trigger_observation_digest = null`.

Der Bilanzwert beschreibt nur die im Record behauptete Verschiebung. S1-ND
legt nicht fest, wie dieser Wert aus einem Feldzustand berechnet wird.

## Lokale Bilanzpruefung

Bei einem tatsaechlichen Wechsel darf sich ausschliesslich das registrierte
Quell-/Zielpaar veraendern:

- die Quellrolle nimmt genau um `transfer_amount` ab;
- die Zielrolle nimmt genau um denselben Wert zu;
- die dritte Rolle bleibt bitgleich;
- Kapazitaet und `edge_id` bleiben bitgleich;
- keine Rolle wird negativ oder nicht endlich.

Bei Stillstand muessen Vor- und Nachledger vollstaendig bitgleich sein. Diese
Pruefregeln sind Erhaltungs- und Identitaetsbedingungen, keine
Dynamikgleichung.

## Ausloeserreferenz

Ein registrierter Ausloeserbeleg fuer einen tatsaechlichen Wechsel muss
dieselbe `edge_id`, dieselbe `field_interval_id`, denselben
`field_reference_digest` und eine fruehere lokale Beobachtungsordnung binden.
Der Uebergangsrecord speichert nur dessen Digest. Rohdaten, Label, Zielwert,
Reward, Sequenzpuffer oder Ergebniswertung duerfen nicht in den Record oder
Ausloeserbeleg gelangen.

Der Validator prueft nur Identitaet und Reihenfolge der gebundenen Referenz.
Er entscheidet nicht, ob die Beobachtung stark genug fuer einen Wechsel ist.

## Ereignisverkettung

Fuer das erste Ereignis einer registrierten Feldfolge gilt:

- `event_ordinal` ist `1`;
- `prior_event_digest` ist `null`;
- `pre_ledger.resource_account_digest` entspricht dem gebundenen Startledger.

Fuer jedes spaetere Ereignis gilt:

- `event_ordinal` ist exakt um eins erhoeht;
- `prior_event_digest` entspricht dem `event_digest` des direkten Vorgaengers;
- `pre_ledger` ist bitgleich zum `post_ledger` des direkten Vorgaengers;
- `edge_id`, Anatomie- und Feldreferenz bleiben innerhalb derselben lokalen
  Kette unveraendert.

Fehlt ein Vorgaenger oder ist die Kette lueckenhaft, wird der Record nicht
isoliert als gueltige Folge uminterpretiert.

## Digestmodell

Die kanonische Serialisierung bleibt UTF-8 ohne BOM, lexikographisch
sortierte Objektfelder, kompakte JSON-Trennzeichen, keine unbekannten Felder,
keine Nichtendlichkeit und keine negative Null. Digestverfahren bleibt
SHA-256 mit 64 kleingeschriebenen Hexzeichen.

Getrennte Digestrollen:

| Digest | Payload |
|---|---|
| `pre_ledger.resource_account_digest` | vollstaendiges Vorledger ohne Digestfeld |
| `post_ledger.resource_account_digest` | vollstaendiges Nachledger ohne Digestfeld |
| `trigger_observation_digest` | externer lokaler read-only Beobachtungsbeleg |
| `prior_event_digest` | vollstaendiger direkter Vorgaengerrecord |
| `event_digest` | aktueller Uebergangsrecord ohne `event_digest` |
| `input_bytes_digest` | unveraenderte Eingabebytes im getrennten Validierungsbeleg |

Digestunterschiede bezeichnen nur unterschiedliche gebundene Inhalte und
keine Wirkung.

## Fail-Closed-Fehlercodes

Die Validatorerweiterung muss mindestens diese eindeutigen Codes binden:

- `UNKNOWN_TRANSITION_SCHEMA_OR_VERSION`;
- `MISSING_OR_UNKNOWN_TRANSITION_FIELD`;
- `NONCANONICAL_TRANSITION_SERIALIZATION`;
- `UNKNOWN_TRANSITION_ID`;
- `TRANSITION_ROLE_PAIR_MISMATCH`;
- `INVALID_TRANSFER_AMOUNT`;
- `PRE_LEDGER_INVALID`;
- `POST_LEDGER_INVALID`;
- `EDGE_ID_MISMATCH`;
- `CAPACITY_CHANGED`;
- `LOCAL_CONSERVATION_MISMATCH`;
- `TRIGGER_BINDING_MISMATCH`;
- `FIELD_REFERENCE_MISMATCH`;
- `ANATOMY_DIGEST_MISMATCH`;
- `EXPOSURE_HISTORY_MISSING_OR_MISMATCHED`;
- `EVENT_ORDER_OR_PREDECESSOR_MISMATCH`;
- `EVENT_DIGEST_MISMATCH`;
- `FORBIDDEN_TRANSITION_PAYLOAD_PRESENT`.

Abhaengige Folgefehler duerfen nicht erfunden werden. Mehrere unabhaengig
feststellbare Fehler werden eindeutig sortiert protokolliert. Ungueltige
Records werden nicht repariert oder neu verkettet.

## Erlaubte Validatorerweiterung

S1-NE darf unmittelbar:

- `mcm_field_organism/kfs1_schema_validator.py` um das neue Schema, eine reine
  Einzelrecordpruefung und eine reine Vorgaengerpruefung erweitern;
- `tests/kfs1_s1ne_transition_fixtures.py` mit sieben positiven
  Alphabetfixtures und gezielten Fehlerfixtures anlegen;
- `tests/test_kfs1_s1ne_transition_validator.py` als fokussierte
  `unittest`-Abnahme anlegen.

Andere Produktionsmodule, Runner, Feldmodule, Medienpfade und vorhandene
DTS-1-Komponenten bleiben unveraendert.

Die einmalige fokussierte Abnahme darf hoechstens 64
Uebergangsvalidatoraufrufe, genau null MCM-Feldschritte und keine Runner-,
Medien-, Browser-, Netzwerk- oder Reportaufrufe enthalten.

## Aussagegrenze

Auch ein vollstaendig gueltiger Record waere nur ein Schema- und
Bilanzbefund. S1-ND behauptet keine KFS-1-Wirkung, keine
Aufnahmeaenderung und keinen Befund zur hypothetischen MCM-Memory.

## Naechster erlaubter Schritt

Der naechste Schritt ist S1-NE, ausschliesslich als Implementierung und
einmalige fokussierte Abnahme der statischen Uebergangsvalidatorerweiterung
innerhalb der gebundenen Dateigrenze. Kandidatengleichung, Rate,
Dynamikparameter, Runtimeintegration, Feldlauf, Baselineurteil und
Funktionsentscheidung bleiben gesperrt.
