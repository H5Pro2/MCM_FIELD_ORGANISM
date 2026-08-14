# NASA-Sechs-Arm-Feldrunner: Verdrahtung mit Ausfuehrungssperre

## Entscheidung

Die Implementierung eines noch nicht ausfuehrbaren Sechs-Arm-Feldrunners ist
technisch freigegeben und umgesetzt. Die Umsetzung verdrahtet nur die
korrigierte Vorregistrierung, die Feldparameter, die Dockgeometrie und die
Messrollen.

Ein Feldlauf wurde nicht ausgefuehrt. Die Ausfuehrung bleibt konstruktiv
gesperrt.

## Verdrahtete Arme

```text
joint.coarse
joint.fine
joint.fine.reproduction
joint.fine.permuted
auditory_only.fine
visual_only.fine
```

Jeder Arm traegt:

- seine vorregistrierten Modalitaeten;
- die vorregistrierte grobe oder completion-feine Zeitteilung;
- die vorregistrierte Sequenzdeklaration;
- einen frischen Feldanfang;
- identische Dockgeometrie;
- identische Feldparameter;
- identische Messrollen.

## Fixierte technische Vertrage

```text
runner_id:
public.av.nasa-earthrise.passive-field.runner.wiring.v1

preregistration_id:
public.av.nasa-earthrise.passive-field.v1

source_id:
public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20

clock_id:
public.media.pts_ns

duration_limit_ticks:
500000000
```

Dockgeometrie:

```text
auditory -> dock.auditory -> 48 Traeger
visual   -> dock.visual   -> 240 Traeger
```

Feldparametervertrag:

```text
fresh_shared_field_per_arm
neutral_local_field_substrate_config_1.0
neutral_fast_afterimage_config_0.5
orthogonal_field_sample_offsets
```

## Freigabegrenze

```text
wiring_complete:                         true
all_arms_structurally_supported:          true
implementation_allowed_for_wiring_only:   true
executable:                              false
field_run_allowed:                       false
raw_payload_retained:                    false
metadata_used_by_field:                  false
memory_claim_allowed:                    false
meaning_claim_allowed:                   false
organization_claim_allowed:              false
ai_claim_allowed:                        false
```

Der Runner enthaelt einen absichtlich gesperrten Ausfuehrungspunkt. Ein Aufruf
der Ausfuehrung bricht mit einer Freigabefehlermeldung ab.

## Grenze

Diese Umsetzung ist kein Feldlauf und kein Ergebnisvergleich. Sie erzeugt
keine Feldzustaende, keine Snapshots, keine Aktivierungs- oder
Nachhallmessungen und keine Armabstaende.

Der Befund belegt nur, dass die korrigierten sechs Arme technisch konsistent
fuer eine spaetere gesondert freizugebende Feldlaufimplementierung verdrahtet
sind.

Er belegt weder Memory noch Bedeutung, innere Organisation oder eigenstaendige
KI.

## Naechster begrenzter Schritt

Vor einer tatsaechlichen Feldausfuehrung ist separat zu pruefen, ob die
konstruktive Ausfuehrungssperre fuer genau diesen Sechs-Arm-Runner aufgehoben
werden darf. Dabei muessen Laufdauer, Feldparameter, Dockgeometrie,
Messrollen, Rohdatenverbot und Claim-Grenzen unveraendert bleiben.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `mcm_field_organism/public_av_field_preregistration.py`;
- `mcm_field_organism/public_av_field_path_compatibility.py`;
- `mcm_field_organism/public_av_receptor_run.py`;
- `mcm_field_organism/neutral_asynchronous_field_runtime.py`;
- `docs/forschung/096_KORRIGIERTE_NASA_FELD_VORREGISTRIERUNG.md`;
- lokale Datei `sources/media/NASA Earthrise Realtime Apollo 8.mp4`.

Externe Quellen wurden nicht verwendet. Eine Zielabweichung ist nicht
erkennbar.
