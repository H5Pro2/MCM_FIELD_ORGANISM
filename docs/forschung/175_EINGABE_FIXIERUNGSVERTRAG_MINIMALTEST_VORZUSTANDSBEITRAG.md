# Eingabe-Fixierungsvertrag Minimaltest Vorzustandsbeitrag

Stand: 2026-07-30

## 1. Zweck und Sperre

Dieses Dokument fixiert ausschliesslich die synthetischen Eingaben A, B und C
sowie die gemeinsame technische Konfiguration fuer die in den Dokumenten 172
bis 174 beschriebene Untersuchung.

Es implementiert keinen Runner, konstruiert kein Feld, startet keinen Testlauf
und berechnet kein Feldergebnis. Die bestehenden Hypothesen, Messpunkte,
Messrollen, Schwellen und Abbruchbedingungen bleiben unveraendert.

## 2. Gemeinsamer Ereignisvertrag

Jede Tabellenzeile bildet spaeter genau einen `ReceptorContactFrame` ab. Die
Wertespalten stehen in der festen Reihenfolge der Traegerkennungen.

```text
modality_id:     synthetic
geometry_id:     synthetic.line3.v1
clock_id:        source.synthetic.v1
carrier_ids:     [carrier.0, carrier.1, carrier.2]
```

Fuer jede Ereigniszeile werden `CommonFieldTime` und `MCMFieldStepTime` aus
demselben Start- und Endtick abgeleitet:

```text
CommonFieldTime.clock_id:       organism.minimal.v1
MCMFieldStepTime.clock_id:      organism.minimal.v1
MCMFieldStepTime.ticks_per_second: 10.0
```

Es gibt keine Zwischenereignisse, Leerschritte, Resets oder abweichenden
Zeitfenster.

## 3. Fixierte Vorgeschichte A

| Reihenfolge | snapshot_id | Starttick | Endtick | Werte `[carrier.0, carrier.1, carrier.2]` |
|---:|---|---:|---:|---|
| 1 | `history.a.e1` | 0 | 10 | `[0.75, 0.0, 0.0]` |
| 2 | `history.a.e2` | 10 | 20 | `[0.0, 0.5, 0.0]` |
| 3 | `history.a.e3` | 20 | 30 | `[0.0, 0.0, 0.25]` |

## 4. Fixierte Vorgeschichte B

| Reihenfolge | snapshot_id | Starttick | Endtick | Werte `[carrier.0, carrier.1, carrier.2]` |
|---:|---|---:|---:|---|
| 1 | `history.b.e1` | 0 | 10 | `[0.0, 0.0, 0.75]` |
| 2 | `history.b.e2` | 10 | 20 | `[0.0, 0.5, 0.0]` |
| 3 | `history.b.e3` | 20 | 30 | `[0.25, 0.0, 0.0]` |

A und B unterscheiden sich in den Kontaktwerten ausschliesslich durch die
raeumliche Vertauschung von `carrier.0` und `carrier.2`. Die zeitlichen Fenster
und die Folge der Ereignisstaerken `0.75`, `0.5`, `0.25` bleiben gleich.

## 5. Fixierter gemeinsamer Kontakt C

| Reihenfolge | snapshot_id | Starttick | Endtick | Werte `[carrier.0, carrier.1, carrier.2]` |
|---:|---|---:|---:|---|
| 1 | `contact.c.e1` | 30 | 40 | `[0.2, -0.1, 0.4]` |

Diese eine Definition von C ist in allen 24 Lauf-IDs bytegleich zu verwenden.
Insbesondere duerfen Snapshot-ID, Zeitfenster, Traegerreihenfolge und Werte
nicht pro Arm neu erzeugt werden.

## 6. Maschinell pruefbare Gleichheitsbedingungen

Die Kontaktstaerkensumme ist fuer diese Eingabekontrolle eindeutig als Summe
der Absolutwerte aller Traegerwerte einer Vorgeschichte definiert. Sie ist
keine Ergebnis- oder Bedeutungsmetrik.

```text
event_count(A):                  3
event_count(B):                  3
total_duration_ticks(A):        30
total_duration_ticks(B):        30
absolute_contact_sum(A):        1.5
absolute_contact_sum(B):        1.5
geometry_id(A):                 synthetic.line3.v1
geometry_id(B):                 synthetic.line3.v1
modality_sequence(A):           [synthetic, synthetic, synthetic]
modality_sequence(B):           [synthetic, synthetic, synthetic]
carrier_sequence(A):            identisch zu carrier_sequence(B)
time_windows(A):                identisch zu time_windows(B)
event_absolute_strengths(A):    [0.75, 0.5, 0.25]
event_absolute_strengths(B):    [0.75, 0.5, 0.25]
```

Jede Abweichung macht das Manifest vor Feldkonstruktion ungueltig.

## 7. Fixierte Feld- und Laufkonfiguration

```text
ReceptorDock:
  dock_id:                    dock.synthetic
  modality_id:                synthetic
  receptor_geometry_id:      synthetic.line3.v1

ReceptorDockAnatomy:
  dock_id:                    dock.synthetic
  modality_id:                synthetic
  positions:                  [[0], [1], [2]]

build_shared_mcm_field:
  reference_frame:            contact.c.e1
  field_id:                   organism.mcm_field
  layer_id:                   organism.mcm_layer
  geometry_id:                organism.shared.v1
  sample_offsets:             [[-1], [1]]

NeutralLocalFieldSubstrateConfig:
  response_time_seconds:      1.0

NeutralFastAfterimageConfig:
  time_constant_seconds:      0.5

dissipation_config:           None
numeric_zero:                 1e-12
rtol:                         0.0
```

`NeutralFieldDissipationConfig` darf weder konstruiert noch als impliziter
Standardwert eingesetzt werden.

## 8. Kanonische Serialisierung

Die kanonische Darstellung verwendet UTF-8-kodiertes JSON mit folgenden festen
Regeln:

```text
allow_nan:    false
sort_keys:    true
separators:   [",", ":"]
ensure_ascii: true
newline:      keine
hash:         SHA-256 ueber die exakten UTF-8-Bytes
```

Die Ereignisobjekte enthalten genau diese Schluessel:

```text
carrier_ids, clock_id, geometry_id, modality_id, snapshot_id, values,
window_end_tick, window_start_tick
```

Die Reihenfolge der Objekte in A, B und C ist die Ereignisreihenfolge und darf
nicht sortiert werden. Nur die Objektschluessel werden lexikografisch sortiert.

### 8.1 Kanonische Bytes A

```json
[{"carrier_ids":["carrier.0","carrier.1","carrier.2"],"clock_id":"source.synthetic.v1","geometry_id":"synthetic.line3.v1","modality_id":"synthetic","snapshot_id":"history.a.e1","values":[0.75,0.0,0.0],"window_end_tick":10,"window_start_tick":0},{"carrier_ids":["carrier.0","carrier.1","carrier.2"],"clock_id":"source.synthetic.v1","geometry_id":"synthetic.line3.v1","modality_id":"synthetic","snapshot_id":"history.a.e2","values":[0.0,0.5,0.0],"window_end_tick":20,"window_start_tick":10},{"carrier_ids":["carrier.0","carrier.1","carrier.2"],"clock_id":"source.synthetic.v1","geometry_id":"synthetic.line3.v1","modality_id":"synthetic","snapshot_id":"history.a.e3","values":[0.0,0.0,0.25],"window_end_tick":30,"window_start_tick":20}]
```

```text
sha256(A): 2d435c4331f083939796920ec2ae3e5864992d2cf11f447f9cab8f75e17e9998
```

### 8.2 Kanonische Bytes B

```json
[{"carrier_ids":["carrier.0","carrier.1","carrier.2"],"clock_id":"source.synthetic.v1","geometry_id":"synthetic.line3.v1","modality_id":"synthetic","snapshot_id":"history.b.e1","values":[0.0,0.0,0.75],"window_end_tick":10,"window_start_tick":0},{"carrier_ids":["carrier.0","carrier.1","carrier.2"],"clock_id":"source.synthetic.v1","geometry_id":"synthetic.line3.v1","modality_id":"synthetic","snapshot_id":"history.b.e2","values":[0.0,0.5,0.0],"window_end_tick":20,"window_start_tick":10},{"carrier_ids":["carrier.0","carrier.1","carrier.2"],"clock_id":"source.synthetic.v1","geometry_id":"synthetic.line3.v1","modality_id":"synthetic","snapshot_id":"history.b.e3","values":[0.25,0.0,0.0],"window_end_tick":30,"window_start_tick":20}]
```

```text
sha256(B): 66ffdb19bdb743d5fb86a7e65dbb7c8c7f8e2045087aee74999bb5fa5d62da31
```

### 8.3 Kanonische Bytes C

```json
[{"carrier_ids":["carrier.0","carrier.1","carrier.2"],"clock_id":"source.synthetic.v1","geometry_id":"synthetic.line3.v1","modality_id":"synthetic","snapshot_id":"contact.c.e1","values":[0.2,-0.1,0.4],"window_end_tick":40,"window_start_tick":30}]
```

```text
sha256(C): 81a6cf62a13cbdf246f8309c99eea564c64e035ca8ca094bb391c129036d3be3
```

### 8.4 Kanonische Bytes der gemeinsamen Konfiguration

```json
{"afterimage_config":{"time_constant_seconds":0.5},"common_clock_id":"organism.minimal.v1","dissipation_config":null,"dock":{"dock_id":"dock.synthetic","modality_id":"synthetic","receptor_geometry_id":"synthetic.line3.v1"},"dock_anatomy":{"dock_id":"dock.synthetic","modality_id":"synthetic","positions":[[0],[1],[2]]},"field":{"field_id":"organism.mcm_field","geometry_id":"organism.shared.v1","layer_id":"organism.mcm_layer","sample_offsets":[[-1],[1]]},"numeric_zero":1e-12,"rtol":0.0,"substrate_config":{"response_time_seconds":1.0},"ticks_per_second":10.0}
```

```text
sha256(config): fa13c44abcfaf7e80aa396b217eeea7ed28c50a3021bbccd62c59a15ecfd0e6a
```

### 8.5 Gesamtbundle

Das Gesamtbundle ist das Objekt
`{"a": A, "b": B, "c": C, "config": config}` unter denselben
Serialisierungsregeln.

```text
sha256(bundle): 2b3286d2ca5a5a815e2002674736c828e9ae30ba12de5f60ac7fbca0bf1bdbd0
```

## 9. Armzuordnung

Die in Dokument 173 festgelegte Armzuordnung bleibt unveraendert:

- `history_a.*` verwendet A und danach C.
- `history_b.*` verwendet B und danach C.
- `equalized_a.none` und `equalized_b.none` verwenden beide A und danach C.
- `permuted_a.*` verwendet B und danach C.
- `permuted_b.*` verwendet A und danach C.
- `.r1` und `.r2` verwenden jeweils dieselben kanonischen Eingabebytes.

## 10. Harte Eingabe-Gates

Vor jeder spaeteren Feldkonstruktion muessen alle vier Einzeldigests und der
Gesamtbundle-Digest den Werten dieses Vertrags entsprechen. Zusaetzlich muessen
die Gleichheitsbedingungen aus Abschnitt 6 maschinell bestehen.

Bei einer Abweichung darf weder ein Feld konstruiert noch ein Teillauf erzeugt
werden. Ein Digest darf nicht nach Sichtung eines Ergebnisses aktualisiert
werden.

## 11. Unveraenderte Sperren

```text
runner_implementation_allowed: false
field_construction_allowed:    false
test_run_allowed:              false
effect_run_allowed:            false
public_av_run_allowed:         false
production_switch_allowed:     false
dynamics_change_allowed:       false
```

Der naechste Schritt ist ausschliesslich eine erneute begrenzte
Ausfuehrungsvorabnahme gegen die Dokumente 172 bis 175.
