# Z4-A4: Skalares Ergebnis, Entscheidung und Lauf-197-Sperre

Stand: 2026-08-06

Status:

- persistierbares skalares Ergebnisschema implementiert und synthetisch
  abgenommen;
- reine und vollstaendige Entscheidungsfunktion implementiert und
  synthetisch abgenommen;
- skalarer Messadapter von vier Z4-A3-Paketen in das Ergebnisschema
  implementiert und synthetisch abgenommen;
- `lauf-197` als kuenftige einmalige Z4-A-Vollmatrix reserviert, aber nicht
  ausgefuehrt;
- one-shot Einstieg implementiert und ausschliesslich an temporaeren
  Testpfaden synthetisch abgenommen;
- Z4-A bleibt bis zu allen Quellen- und Implementierungsabnahmen gesperrt.

## Zweck

Z4-A4 schliesst die letzte statische Methodenluecke der
[Z4-A-Mehrwelt-Vorregistrierung](Z4A_MEHRWELT_FELDENCODER_VORREGISTRIERUNG_UND_AUSFUEHRUNGSSPERRE.md).
Der Vertrag legt vor jeder Implementierung fest:

- welche skalaren Werte spaeter persistiert werden duerfen;
- wie technische Abbrueche von Sachentscheidungen getrennt werden;
- wie die vier Weltfamilien und drei Feldformen rein ausgewertet werden;
- wann keine vorregistrierte Entscheidung moeglich ist;
- wie der einmalige kuenftige Lauf 197 gesperrt wird.

Z4-A4 fuehrt keine Quelle, keinen Runner und keinen Forschungswert aus.
Lauf 196 bleibt der letzte tatsaechlich ausgefuehrte Forschungslauf.

## Identitaeten

```text
preregistration_id:   mcm.z4a.multiworld-field-encoder.v1
runner_contract_id:   z4a.generic-field-trajectory-runner.v1
decision_contract_id: z4a.multiworld-field-encoder-decision.v1
schema_id:            mcm.z4a.multiworld-field-encoder.run197.v1
reserved_run_id:      lauf-197
output_path:          reports/mcm_z4a_field_encoder_lauf_197.json
```

Die Reservierung ist keine Ausfuehrung und kein Befund. Der Dateipfad darf
vor der spaeteren ausdruecklichen Ausfuehrung nicht existieren.

## Eingangsgrenze der Entscheidung

Die reine Funktion

```text
evaluate_z4a_technical_packet(packet) -> Z4AEvaluationResult
```

darf nur ein vollstaendig validiertes technisches Paket gemaess
[Z4-A3](Z4A3_GENERISCHER_P0_F3_B3_TRAJEKTORIENRUNNERVERTRAG.md) lesen. Sie
darf nicht:

- Dateien, Netzwerk, Uhrzeit, Zufall oder Umgebungsvariablen lesen;
- Quellen neu erzeugen oder einen Browser starten;
- Feldgleichungen erneut ausfuehren;
- Schwellen, Huellen oder Parameter an Messwerte anpassen;
- eine Entscheidung in einen Feldzustand zurueckschreiben;
- Rohtrajektorien serialisieren.

## Welt- und Modellreihenfolge

```text
worlds:
  1. z4a.video.street-traffic.v1
  2. z4a.av.nasa-earthrise.v1
  3. z4a.audio.sound-mute-sound.v1
  4. z4a.browser.direct.reference.v2

models:
  1. p0.exact
  2. f3.candidate
  3. b3.linear-coupled

arms:
  1. reference
  2. reproduction
  3. partitioned
  4. reversed
  5. permuted
  6. independent
```

Jede Abweichung in Anzahl, Identitaet oder Reihenfolge ist ein technischer
Abbruch, keine auswertbare Teilmatrix.

## Skalare Komponentenmessung

Je Welt, Modell, Arm und aktive Komponente darf das Ergebnis enthalten:

```text
component_id
reference_path_length
n_to_2n_distance
two_n_to_4n_distance
numerical_envelope
distance_from_reference
comparison_envelope
within_comparison_envelope
above_comparison_envelope
```

Fuer P0 sind `n_to_2n_distance` und `two_n_to_4n_distance` `null`; seine
exakte Huelle ist `1e-12`. Fuer `reference` ist
`distance_from_reference = 0.0`.

Vergleichsoperatoren sind fest:

```text
within = distance <= comparison_envelope
above  = distance >  comparison_envelope
```

Gleichheit mit der Huelle zaehlt damit nicht als kausale Trennung.

## Modellentscheidung je Welt

Ein Modell ist in einer Welt `technically_stable`, wenn gleichzeitig:

- alle Quellen-, Handoff-, Support-, Invarianten- und Observerkontrollen
  gelten;
- `reproduction` in jeder aktiven Komponente innerhalb ihrer Huelle liegt;
- `partitioned` in jeder aktiven Komponente innerhalb ihrer Huelle liegt;
- fuer F3 und B3 komponentenweise
  `D(2n,4n) <= D(n,2n)` gilt;
- keine erforderliche S- oder H-Referenztrajektorie unmessbar ist.

Nur bei technischer Stabilitaet wird `stable_causal_separation` bestimmt. Es
ist genau dann wahr, wenn jeder der drei Arme

```text
reversed, permuted, independent
```

in mindestens einer aktiven Komponente strikt oberhalb seiner
Vergleichshuelle liegt.

Fuer F3 wird zusaetzlich `fast_component_causal_separation` gebildet. Es ist
nur wahr, wenn jeder der drei Kausalarme in `activation` oder `afterimage`
strikt oberhalb der jeweiligen Huelle liegt. Eine reine M-Trennung reicht
damit nicht fuer einen F3-Vorteil.

## Technischer Vorrang

Vor jeder Sachentscheidung werden alle projektweiten Kontrollen ausgewertet.
Scheitert mindestens eine, lautet die einzige Gesamtentscheidung:

```text
FIELD_ENCODER_NOT_TECHNICALLY_STABLE
```

In diesem Fall werden keine `stable_causal_separation`-Werte als Befund
ausgegeben. Das Ergebnis darf nur Fehlerstufe, fehlgeschlagene Kontrollen,
Digests, bis dahin abgeschlossene Taskzahlen und technische Diagnosen
enthalten.

## Vollstaendige Gesamtentscheidung

Nach bestandener Technik werden folgende Mengen gebildet:

```text
stable_worlds(model) = Welten mit stable_causal_separation fuer model

f3_advantage_worlds = Welten, in denen gleichzeitig:
  - F3 stable_causal_separation traegt;
  - F3 fast_component_causal_separation traegt;
  - P0 stable_causal_separation nicht traegt;
  - B3 stable_causal_separation nicht traegt.
```

Die Gesamtentscheidung wird in exakt dieser Reihenfolge bestimmt:

### 1. F3-Vorteil

```text
F3_TECHNICAL_TRAJECTORY_ADVANTAGE
```

genau dann, wenn:

- F3 in allen vier Welten technisch stabil ist;
- `len(f3_advantage_worlds) >= 2`.

### 2. Kausaler Feldencoder auf Baseline-Niveau

```text
FIELD_ENCODER_CAUSAL_BUT_BASELINE_EQUIVALENT
```

genau dann, wenn kein F3-Vorteil vorliegt und mindestens eine Bedingung gilt:

- P0 traegt in mindestens drei Welten `stable_causal_separation`;
- B3 traegt in mindestens drei Welten `stable_causal_separation`;
- F3 traegt in mindestens drei Welten `stable_causal_separation` und in jeder
  dieser Welten traegt mindestens P0 oder B3 ebenfalls
  `stable_causal_separation`.

### 3. Keine ausreichend breite stabile Trennung

```text
NO_STABLE_CAUSAL_FIELD_SEPARATION
```

genau dann, wenn kein vorheriger Fall gilt und kein Modell in mindestens drei
Welten `stable_causal_separation` traegt.

Der vorherige F3-Vorteil besitzt bewusst Vorrang: Ein streng von beiden
Baselines getrennter F3-Befund in zwei Welten darf nicht durch die
Drei-Welten-Breite des allgemeinen Nullentscheids verdeckt werden.

### 4. Nicht abgedecktes Mischmuster

```text
Z4A_DECISION_UNRESOLVED
```

fuer jedes verbleibende technisch gueltige Muster.

Dieser Stopstatus ist notwendig, weil beispielsweise F3 in drei Welten
stabil sein kann, ohne in zwei Welten beide Baselines zu schlagen und ohne
vollstaendig von den Baselines abgedeckt zu sein. Ein solches Muster darf
weder als Vorteil noch als Gleichwertigkeit oder Nullbefund erzwungen werden.
Es erfordert eine neue, vorab begruendete Forschungsfrage und keine
Nachinterpretation von Lauf 197.

## Persistierbares Ergebnisschema

Das ASCII-JSON besitzt auf oberster Ebene exakt:

```text
schema_id
run_id
preregistration_id
runner_contract_id
decision_contract_id
execution_status
technical_abort_stage
world_order
model_order
arm_order
binding_digests
technical_controls
world_results
task_budget
overall_decision
decision_basis
raw_payload_retained
raw_receptor_sequences_retained
raw_trajectories_retained
memory_claim_allowed
organization_claim_allowed
topology_claim_allowed
semantics_claim_allowed
self_regulation_claim_allowed
ai_claim_allowed
```

Feste Werte:

```text
run_id:                         lauf-197
raw_payload_retained:           false
raw_receptor_sequences_retained:false
raw_trajectories_retained:      false
memory_claim_allowed:           false
organization_claim_allowed:     false
topology_claim_allowed:         false
semantics_claim_allowed:        false
self_regulation_claim_allowed:  false
ai_claim_allowed:               false
```

`technical_controls` besitzt exakt diese geordnete Identitaet:

```text
all_world_bindings_match
all_world_packages_complete
task_inventory_complete
all_handoffs_complete
all_models_share_handoffs
all_base_fields_match
all_completion_supports_complete
reference_reproduction_stable
partition_invariant
refinement_converges
state_invariants_hold
observer_passive
persistence_boundary_holds
```

Jeder Eintrag ist ein Paar aus Kontroll-ID und Boolwert. Freie
Fehlerinterpretationen oder nachtraeglich ergaenzte Kontrollnamen sind nicht
zulaessig.

`decision_basis` enthaelt ausschliesslich:

```text
stable_world_ids_by_model
f3_advantage_world_ids
baseline_covered_f3_world_ids
unresolved_reason_id
```

`unresolved_reason_id` ist `null` oder
`mixed_stable_separation_not_preregistered`. Freier Begruendungstext gehoert
nicht in das Forschungsartefakt.

`execution_status` ist genau `completed` oder `technical_abort`.
`technical_abort_stage` ist bei Erfolg `null`, sonst genau einer aus:

```text
source_preflight
world_package
runner
completion_support
evaluation
serialization
```

## Weltresultat

Jeder der vier Eintraege in `world_results` enthaelt nur:

```text
world_id
execution_status
failed_controls
source_binding_digests
sequence_digests
proposal_digests
base_layer_digest
dock_map_digest
source_event_count
completion_group_count
technical_support_count
decision_support_count
model_results
task_count_planned
task_count_completed
runtime_seconds
```

Noch nicht gestartete Welten eines technischen Abbruchs bleiben in der festen
Viererreihenfolge und tragen `execution_status = not_started`, leere
`model_results` und `task_count_completed = 0`.

Auf Weltebene ist `execution_status` genau `completed`, `technical_abort`
oder `not_started`.

## Modellresultat

Ein `model_result` enthaelt nur:

```text
model_id
component_ids
dynamic_scalar_state_budget
technically_stable
stable_causal_separation
fast_component_causal_separation
failed_controls
arm_results
runtime_seconds
substep_count
maximum_abs_activation
maximum_abs_afterimage
maximum_auxiliary_conservation_error
minimum_auxiliary_value
```

Fuer P0 sind die beiden Auxiliary-Diagnosen `null` und
`fast_component_causal_separation` entspricht seiner normalen kausalen
Trennung in S/H. Fuer B3 darf `minimum_auxiliary_value` nicht als M-Mass
bezeichnet werden.

## Armresultat

Ein `arm_result` enthaelt nur:

```text
arm_id
execution_digest
final_snapshot_digest
technical_support_count
decision_support_count
component_measurements
refinement_task_summaries
```

Eine `refinement_task_summary` enthaelt nur:

```text
refinement
integration_method
final_snapshot_digest
diagnostic_count
substep_count
runtime_seconds
maximum_step_seconds
maximum_abs_activation
maximum_abs_afterimage
maximum_auxiliary_conservation_error
minimum_auxiliary_value
```

Es werden keine Zustandsvektoren, Einzelereignisse oder Trajektorienpunkte
persistiert.

## Taskbudget

```text
world_count:          4
tasks_per_world:      42
task_count_planned:   168
task_count_completed: 0..168
```

`task_count_completed = 168` ist fuer `execution_status = completed`
zwingend. Eine Teilmatrix erhaelt niemals eine Sachentscheidung.

## One-shot Reihenfolge

Der kuenftige Einstieg

```text
tools/run_z4a_field_encoder_197.py
```

darf nach gesonderter Implementierungs- und Ausfuehrungsfreigabe genau:

1. abbrechen, wenn die Zieldatei bereits existiert;
2. alle vier Quellen, Implementierungsmodule und Browserbindungen statisch
   gegen ihre finalen Digests pruefen;
3. alle vier Weltpakete vollstaendig materialisieren und validieren;
4. den technischen Z4-A3-Runner genau einmal mit 168 Aufgaben ausfuehren;
5. den Completion-Support anwenden;
6. die reine Z4-A4-Entscheidungsfunktion genau einmal aufrufen;
7. das skalare Ergebnis als ASCII-JSON in eine temporaere Datei schreiben;
8. die temporaere Datei nach erfolgreicher JSON-Validierung atomar auf den
   reservierten Zielpfad verschieben.

Er darf keine Parameter, Quellen, Huellen oder Entscheidungen veraendern und
keinen automatischen Wiederholungslauf starten.

## Verhalten bei technischem Abbruch

Ein erwarteter Vertragsfehler wird als `technical_abort` mit
`FIELD_ENCODER_NOT_TECHNICALLY_STABLE` atomar persistiert. Bereits erzeugte
Rohdaten und Trajektorien werden verworfen. Lauf 197 gilt danach als
tatsaechlich versucht und darf nicht ueberschrieben oder wiederholt werden.

Eine spaetere technische Korrektur benoetigt einen separaten
Korrekturvertrag, neue Implementierungsdigests und eine neue Laufnummer. Die
Sachschwellen von Z4-A bleiben dabei unveraendert.

Ein harter Prozessabbruch vor der atomaren Ergebnisdatei wird dokumentiert,
aber nicht durch blindes erneutes Starten umgangen. Vor einem weiteren
Versuch muss geklaert werden, ob Feldaufgaben bereits ausgefuehrt wurden.

## Serialisierungsgrenze

Vor dem atomaren Schreiben wird der vollstaendige JSON-Text rekursiv gegen
verbotene Schluessel geprueft. Verboten sind mindestens:

```text
samples
raw_samples
raw_audio
raw_video
pixels
frames
receptor_sequences
full_trajectories
decision_trajectories
trajectory_samples
field_vectors
activation_vector
afterimage_vector
mass_vector
baseline_state_vector
```

Alle Zahlen muessen endlich sein; `allow_nan=False` ist zwingend. JSON wird
mit `indent=2`, `sort_keys=True` und ASCII-Encoding geschrieben.

## Aussagegrenze

Auch `F3_TECHNICAL_TRAJECTORY_ADVANTAGE` bezeichnet nur eine eng
vorregistrierte technische Trajektorienfunktion gegen P0 und B3 in den
kontrollierten Welten. Keine Entscheidung erlaubt Aussagen ueber
Wiedererkennung, Lernen, Praegung, Semantik, Organisation, relative Feldzeit,
Memory, Selbstregulation oder KI.

## Aktuelle Entscheidung

`Z4A4_TECHNICALLY_BOUND`

Das rohtrajektorienfreie Schema, die rekursive Persistenzgrenze und alle fuenf
Zweige der reinen Entscheidungsfunktion sind technisch implementiert. Die
fokussierte Abnahme bestand mit `9 passed`, die verbundene Regression mit
`31 passed` und 6 Subtests. Es wurde kein JSON geschrieben, kein Runner
aufgerufen und keine Laufnummer ausgefuehrt.

Der reine Messadapter verarbeitet vier geordnete Z4-A3-Pakete, berechnet die
gebundene 101-Punkt-Pfadmetrik, n/2n/4n-Huellen, Armabstaende und
Welt-/Modellflags und gibt nur das skalare Schema zurueck. Seine fokussierte
Abnahme bestand mit `8 passed`; die verbundene Regression bestand mit
`39 passed` und 6 Subtests. Dabei wurden vier Kopien einer kleinen
synthetischen Welt mit zusammen 168 technischen Aufgaben verwendet. Das
In-Memory-Ergebnis ist kein Forschungslauf und kein Befund.

Der injizierbare one-shot Einstieg erzwingt Ziel- und Versuchssperre,
vollstaendigen Preflight, genau einen Matrix- und einen Auswertungsaufruf,
168 abgeschlossene Aufgaben, ASCII-JSON-Rueckvalidierung und atomare
Publikation. Seine fokussierte Abnahme bestand mit `5 passed`; die verbundene
Z4-Kette bestand mit `45 passed` und 6 Subtests. Verwendet wurden nur
synthetische Pakete und temporaere Testpfade. Der reservierte reale Zielpfad
wurde nicht angelegt und Lauf 197 wurde weder gestartet noch versucht.

Z4-A4 ist damit technisch geschlossen. Die reale Vollmatrix bleibt wegen der
noch fehlenden Weltbindung Z4-A2 gesperrt.

## Bester naechster Schritt

Z4-A2 implementieren: kontrollierte v2-Browserassets, direkten kamerafreien
Browser-zu-Rezeptor-Adapter und eine unabhaengige Kontrollquelle technisch
binden. Zunaechst nur statisch und technisch pruefen; den reservierten
Lauf-197-Pfad nicht anlegen und keinen Forschungslauf starten.
