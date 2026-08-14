# 178 - Implementierungsvorabnahme privater Executor Minimaltest Vorzustandsbeitrag

## 1. Zweck und harte Grenze

Dieses Dokument bindet ausschliesslich die technischen Entscheidungen, die vor
einer moeglichen privaten Executor-Implementierung des in den Dokumenten 172
bis 177 festgelegten Minimaltests offen waren. Es implementiert keinen
Executor, konstruiert kein Feld, verteilt keinen Rezeptorkontakt und fuehrt
keinen Integrator, Hook, Runner oder Effektvergleich aus.

Der Einstiegspunkt `execute_previous_state_minimal_runner(...)` bleibt immer
abbrechend. Die in Dokument 177 genannten Ausfuehrungs- und Einsichtssperren
bleiben unveraendert.

## 2. Einheitliche kanonische Kodierung

Jeder in diesem Dokument neu definierte JSON-Digest verwendet ohne Ausnahme:

```text
json.dumps(value,
    allow_nan=False,
    ensure_ascii=True,
    separators=(",", ":"),
    sort_keys=True)
UTF-8 ohne BOM und ohne abschliessenden Zeilenumbruch
SHA-256 ueber genau diese UTF-8-Bytes
Hexausgabe in Kleinbuchstaben
```

Listen behalten ihre angegebene Reihenfolge. Tupel werden als JSON-Listen
kodiert. `None` wird `null`. Python-, NumPy- oder Plattform-Repraesentationen
duerfen nicht direkt gehasht werden. Jeder numerische Wert muss vor der
Kodierung ein endlicher Python-`int` oder Python-`float` sein; Boolesche Werte
sind als Zahlen unzulaessig.

## 3. Vorab fixierte Quelldateidigests

Die Sollwerte sind SHA-256 ueber die unveraenderten rohen Dateibytes im
aktuellen Vertragsstand:

```text
mcm_field_organism/_previous_state_minimal_runner.py
f25aa5e4f5affe9755ae5f011b029a2ad46aa5a6560532706b7db7a40d12ae72

mcm_field_organism/previous_state_contribution_hook.py
2a3f2f355ba3c713296156abb08553dc4ce0cbe5a0701e12258ea286caf8371e
```

Die Pfade werden relativ zur Projektwurzel aufgeloest. Symlinks, ein anderer
Pfad, fehlende Dateien, nicht regulaere Dateien oder abweichende Bytes fuehren
vor jeder Feldkonstruktion zu `source_or_hook_not_frozen`. Sollwerte duerfen
nicht waehrend eines Laufs erzeugt oder aktualisiert werden.

## 4. Exaktes Runner-Snapshotschema M0 bis M3

Der punktuebergreifende Zustandsdigest verwendet an allen vier Messpunkten
exakt das folgende Objekt. Weitere Schluessel sind unzulaessig:

```json
{
  "activation": [],
  "afterimage": [],
  "common_interval": null,
  "docks": [],
  "field": {},
  "field_tick": 0,
  "geometry_digest": "",
  "layer_digest": "",
  "pending_or_last": {
    "boundary_digest": null,
    "generator_digest": null,
    "receptor_distribution_digest": null
  },
  "schema_version": 1
}
```

Die Rollen sind fest:

- `activation`: Python-Floats in der Reihenfolge `field.layer.neurons`.
- `afterimage`: Python-Floats in derselben Neuronenreihenfolge.
- `common_interval`: an M0 `null`, sonst exakt
  `{"clock_id": str, "window_end_tick": int, "window_start_tick": int}`.
- `docks`: nach `dock_id` sortierte Objekte mit exakt `dock_id`,
  `modality_id`, `pairs` und `receptor_geometry_id`; `pairs` bleibt die
  Reihenfolge aus `dock.dock_map.pairs` und wird als Liste zweielementiger
  Listen kodiert.
- `field`: exakt `field_id`, `geometry_id`, `layer_id`, `sample_offsets` und
  `neuron_ids`; beide Listen behalten die Runtime-Reihenfolge.
- `field_tick`: `field.layer.tick` als Integer.
- `geometry_digest`: Digest aus Abschnitt 5.1.
- `layer_digest`: unveraendert `field.layer.digest()`.
- `pending_or_last`: an M0 drei `null`-Werte; an M1 die Digests der letzten
  A/B-Verteilung, an M2 die Digests der anstehenden C-Verteilung und an M3
  die Digests derselben abgeschlossenen C-Verteilung.
- `schema_version`: Integer `1`.

`run_id` und `point` duerfen nicht in diesem Zustandsobjekt vorkommen. Der
Messumschlag enthaelt exakt:

```json
{"point":"M0","run_id":"...","state":{},"state_digest":"..."}
```

`state` ist das oben definierte Objekt und `state_digest` dessen Digest. Der
Punkt ist genau einer aus `M0`, `M1`, `M2`, `M3`. Ab M1 darf der vorhandene
`SharedMCMFieldSnapshot.digest()` ausserhalb von `state` als zusaetzliche
technische Diagnose gespeichert werden; er ist kein Bestandteil des
Runner-Zustandsdigests. M0 ruft `SharedMCMField.snapshot()` niemals auf.

## 5. Exakte Digest-Payloads

### 5.1 Geometrie

Der Geometrie-Digest wird ueber exakt dieses konstante Objekt gebildet:

```json
{"dock_anatomy":{"dock_id":"dock.synthetic","modality_id":"synthetic","positions":[[0],[1],[2]]},"field":{"field_id":"organism.mcm_field","geometry_id":"organism.shared.v1","layer_id":"organism.mcm_layer","sample_offsets":[[-1],[1]]},"reference":{"carrier_ids":["carrier.0","carrier.1","carrier.2"],"geometry_id":"synthetic.line3.v1","modality_id":"synthetic"},"schema_version":1}
```

Werte, Snapshot-ID und Zeit von C gehoeren nicht zum Geometrie-Digest.

Der statisch reproduzierte Sollwert ist:

```text
geometry_digest:
a9701d5524be56f21d1f8351e5c82f2e2d84d639cd08f231f09e7ea9e5391ecb
```

### 5.2 Konstruktion

Der Konstruktionsdigest wird ueber exakt dieses Objekt gebildet:

```json
{"afterimage_config":{"time_constant_seconds":0.5},"common_clock_id":"organism.minimal.v1","dissipation_config":null,"dock":{"dock_id":"dock.synthetic","modality_id":"synthetic","receptor_geometry_id":"synthetic.line3.v1"},"geometry_digest":"a9701d5524be56f21d1f8351e5c82f2e2d84d639cd08f231f09e7ea9e5391ecb","numeric_zero":1e-12,"rtol":0.0,"schema_version":1,"substrate_config":{"response_time_seconds":1.0},"ticks_per_second":10.0}
```

Der statisch reproduzierte Sollwert ist:

```text
construction_digest:
1d1817784190c26d883c744b305634ee72cdabde84767bcc38aaee7c9f6a2b8e
```

Der Digest muss in allen 24 frischen Kontexten gleich sein.

### 5.3 Rezeptorverteilung

Der Verteilungsdigest ist ausschliesslich
`ReceptorDistribution.digest()`. Seine Payload ist unveraendert
`ReceptorDistribution.canonical_payload()`; sie darf nicht kopiert,
umgeordnet oder um einen Runner-Schluessel erweitert werden.

### 5.4 Generator und Boundary

`_generator_and_boundary(field, distribution, substrate_config)` wird genau
einmal pro zu pruefendem Feldschritt aufgerufen. Der Generator wird als
zeilenweise verschachtelte Liste, die Boundary als einfache Liste von
Python-Floats kodiert. Die Digest-Payload ist jeweils unmittelbar die Liste,
nicht ein umschliessendes Objekt:

```text
generator_digest = sha256(canonical_json(generator.tolist()))
boundary_digest  = sha256(canonical_json(boundary.tolist()))
```

Form, Endlichkeit und Reihenfolge werden vor dem Hashen geprueft. Rundung,
Clipping, Stringformatierung oder dtype-spezifische Bytehashes sind verboten.

## 6. Vollstaendige Runtime-Signaturbindung

Die privaten Helfer aus Dokument 177 sind exakt wie folgt gebunden:

- `_validate_preflight(manifest)`: nur Manifestkonstruktor, rohe Dateibytes,
  `hashlib.sha256`, `json.loads` und die kanonische JSON-Funktion; keinerlei
  Runtime-Konstruktion.
- `_build_fresh_run_context(manifest, run_id)`: erzeugt
  `ReceptorContactFrame(...)`, `ReceptorDockAnatomy(...)`, danach exakt
  `build_shared_mcm_field(reference_frames=(c_reference_frame,),
  anatomies={"synthetic": anatomy}, sample_offsets=((-1,), (1,)),
  field_id="organism.mcm_field", layer_id="organism.mcm_layer",
  geometry_id="organism.shared.v1")`; anschliessend
  `ReceptorDistributor()`, `attach(ReceptorDock("dock.synthetic",
  "synthetic", "synthetic.line3.v1"))`,
  `NeutralLocalFieldSubstrateConfig(1.0)` und
  `NeutralFastAfterimageConfig(0.5)`.
- `_frame(contact)`: positionsgetreue Konstruktion von
  `ReceptorContactFrame(modality_id, geometry_id, snapshot_id, clock_id,
  window_start_tick, window_end_tick, carrier_ids, values)`; keine
  Normalisierung oder Umbenennung.
- `_distribution(context, frame)`: erzeugt
  `CommonFieldTime("organism.minimal.v1", frame.window_start_tick,
  frame.window_end_tick)` und ruft ausschliesslich
  `context.distributor.distribute((frame,), common_field_time)` auf.
- `_step_time(frame)`: erzeugt ausschliesslich
  `MCMFieldStepTime("organism.minimal.v1", frame.window_start_tick,
  frame.window_end_tick, 10.0)`.
- `_measure(context, point, pending)`: liest nur `field.layer.digest()`,
  `field.layer.neurons`, `field.layer.tick`, `field.docks`, Geometrierollen
  und die in Abschnitt 4 festgelegten Digests. Keine mutierende Methode.
- `_advance_history(...)`: genau ein
  `advance_neutral_fast_shared_field(field, distribution, step_time,
  substrate_config, afterimage_config, dissipation_config=None)`.
- `_advance_c(...)`: genau ein
  `advance_with_previous_state_operator(field, distribution, step_time,
  substrate_config, afterimage_config, dissipation_config=None,
  previous_state_operator=operator)`.

Positions- und Keywordbindung duerfen nicht durch Wrapper mit Defaults
aufgeweicht werden. `run_neutral_asynchronous_field`, Transient-Funktionen und
`NeutralFieldDissipationConfig` bleiben ausgeschlossen.

## 7. Abbruchcheckpoints und Diagnosen

Ein Diagnosewert ist immer ein Tupel sortierter `(name, value)`-Paare mit
Stringwerten. Es werden keine Messvektoren, Teilresultate oder fachlichen
Vergleiche ausgegeben. Die folgende Tabelle ist vollstaendig und geordnet:

| ID | Fruehester Checkpoint | Einzige Diagnoseschluessel |
|---|---|---|
| `source_or_hook_not_frozen` | Vor jeder Kontextkonstruktion | `path`, `expected_sha256`, `actual_sha256` |
| `dissipation_active_or_patch_not_isolated` | Vor jeder Kontextkonstruktion und unmittelbar vor jedem Feldaufruf | `role`, `actual` |
| `none_identity_not_bit_equal` | Nach M3 von `history_b.identity.r2`, vor `history_a.zero.r1` | `left_run_id`, `right_run_id`, `point`, `left_digest`, `right_digest` |
| `replicate_digest_mismatch` | Nach M3 des jeweils zweiten Replikats, vor dem naechsten Arm | `arm_id`, `point`, `r1_digest`, `r2_digest` |
| `replicate_count_or_fresh_field_invalid` | Vor erster Konstruktion fuer Anzahl; direkt nach jeder Konstruktion fuer Identitaet | `run_id`, `expected`, `actual` |
| `history_budget_duration_geometry_or_modality_mismatch` | Vor Konstruktion und erneut vor jeder A/B-Verteilung | `run_id`, `contact_id`, `role`, `expected`, `actual` |
| `current_contact_c_not_byte_equal` | Vor Konstruktion der Geometriereferenz und erneut vor C-Verteilung | `run_id`, `expected_sha256`, `actual_sha256` |
| `generator_boundary_time_or_distribution_mismatch` | Nach Verteilung, vor dem zugehoerigen Integrator | `run_id`, `point`, `role`, `expected`, `actual` |
| `field_dynamics_or_measurement_path_changed` | Vor erster Konstruktion fuer Signaturen; an jedem Messpunkt fuer Schema | `run_id`, `point`, `role`, `expected`, `actual` |
| `nonfinite_or_normalized_domain_violation` | An M0 bis M3 unmittelbar nach dem Zustandslesen | `run_id`, `point`, `role`, `index`, `actual` |
| `equalized_baseline_not_equal` | Nach M3 von `equalized_b.none.r2`, vor `permuted_a.none.r1` | `left_run_id`, `right_run_id`, `point`, `left_digest`, `right_digest` |
| `results_viewed_before_all_arms_complete` | Vor dem ersten Lauf und vor jeder moeglichen Ausgabe-/Callback-Grenze | `role`, `actual` |

Fuer `none_identity_not_bit_equal`, `replicate_digest_mismatch` und
`equalized_baseline_not_equal` werden die festgelegten Messpunktdigests M0 bis
M3 paarweise in dieser Reihenfolge geprueft. Beim ersten Unterschied wird
abgebrochen. Nach einem Abbruch wird kein weiterer Lauf begonnen und kein
Messbundle gebildet.

Nur Sollwerte, deren Erzeugung eine Rezeptorverteilung, Feldkonstruktion,
Generator-/Boundary-Bildung oder Feldfortschreibung benoetigt, duerfen nicht
aus dem ersten Forschungslauf als Referenz gewonnen werden. Insbesondere
Generator- und Boundary-Sollwerte bleiben offen und muessen vor einer
spaeteren Ausfuehrungsfreigabe durch einen separaten, ausdruecklich
genehmigten Fixierungsschritt erzeugt und in einen weiteren Vertrag
aufgenommen werden. Geometrie- und Konstruktionsdigest sind dagegen in den
Abschnitten 5.1 und 5.2 bereits vollstaendig statisch fixiert. Bis zur
Fixierung aller runtimeabhaengigen Sollwerte kann die reale
Executor-Ausfuehrung nicht freigegeben werden.

## 8. Nachweis geschlossener Implementierungsentscheidungen

Durch die Abschnitte 2 bis 7 sind JSON-Regeln, Schluessel, Listenreihenfolgen,
Nullrollen, Messumschlag, Runtime-Aufrufe, Parameterwerte, Dateidigests,
Abbruchreihenfolge und Diagnoseschluessel festgelegt. Eine spaetere
Implementierung darf diese Festlegungen nur mechanisch abbilden.

Bewusst noch nicht vorhanden sind ausschliesslich Sollwerte, deren Erzeugung
Rezeptorverteilung, Feldkonstruktion, Generator-/Boundary-Bildung oder
Feldfortschreibung benoetigt. Dazu gehoeren insbesondere Generator und
Boundary, nicht aber Geometrie oder Konstruktion. Die Erzeugung der
runtimeabhaengigen Werte ist kein Teil dieser Vorabnahme. Diese offene externe
Fixierung ist eine Ausfuehrungssperre und keine frei waehlbare
Implementierungsentscheidung.

## 9. Freigabezustand und Aussagegrenze

```text
executor_implementation_released: false
runner_execution_released:        false
field_construction_released:       false
receptor_distribution_released:   false
integration_released:             false
hook_execution_released:          false
effect_evaluation_released:        false
public_av_released:                false
production_switch_released:        false
dynamics_change_released:          false
```

Aus dieser Implementierungsvorabnahme folgt kein Befund zu Feldwirkung,
Kontaktgeschichte, Memory, Organisation, Bedeutung, Semantik, Bewusstsein,
Eigenstaendigkeit oder KI.

## 10. Naechster ausfuehrbarer Auftrag

Pruefe dieses Dokument statisch gegen Dokument 177 und die genannten
Runtime-Signaturen. Pruefe insbesondere die Dateidigests, das identische
M0-bis-M3-Schema, die Payload-Eindeutigkeit, die Signaturbindung und alle
zwoelf Abbruchcheckpoints. Keine Executor-Implementierung und keine
Runtime-Ausfuehrung.
