# Auditierte passive visuelle Verlaufskarte

## Auftrag und Grenze

Nach dem auditieren oeffentlichen visuellen Weltlauf wurde die bereits
vorhandene passive zeitliche Verlaufskarte mit derselben lokalen Originalquelle
erneut ausgefuehrt.

Der Lauf bleibt ein Observerartefakt. Er schreibt nichts an Rezeptor, Dock,
Neuronenschicht, Feldsnapshot, Effektor oder Memory zurueck. Er fuehrt keine
Labels, Bedeutung, Rewards, Zielrollen, Segmenterkennung oder KI-Auswertung ein.

## Quellenaudit

```text
source_id:                public.visual.street-traffic.commons.2013-02-02
file_present:             true
observed_size_bytes:      26490572
size_matches:             true
observed_sha1:            7f916030f14d84a65aa92077339f472897915fef
sha1_matches:             true
accepted:                 true
receptor_release_granted: false
```

Der Temporal-Map-Runner wurde an dieselbe observerseitige Integritaetskontrolle
gekoppelt. Fehlt die Quelle oder weichen Groesse oder SHA-1 ab, endet der Runner
vor jeder Decodierung mit technischem Auditbefund.

## Ausfuehrung

```powershell
.\.venv\Scripts\python.exe tools\run_public_visual_temporal_map.py `
  "sources\media\Street traffic.webm" `
  --section-ms 0 5000 10000 15000 20000 25000 30000 35000 `
  --output debug\public_visual_temporal_map_lauf_085.json
```

## Ergebnis

```text
duration_ms:                       35000
sampling_interval_ms:              125
interval_count:                    280
reduced_sequence_digest:           f147109d3ac2c411328b0a514119df8fd18abd0bded487056d4a6502bc70780f
repeated_sequence_digest:          f147109d3ac2c411328b0a514119df8fd18abd0bded487056d4a6502bc70780f
temporal_map_digest:               cbfab967f9d67325e153a4845053155c42524bfd7af278396c688232f54afefa
actual_repeat_max_abs_residual:    0.0
static_repeat_max_abs_residual:    0.0
```

Die reduzierte Bildfolge wurde exakt reproduziert. Auch die reale Verlaufskarte
und die statische Baseline wiederholen sich ohne numerischen Rest.

## Aeussere Abschnittssummen

Die Abschnittsgrenzen wurden vor der Feldauswertung als aeussere Zeitwerte
festgelegt:

```text
0, 5000, 10000, 15000, 20000, 25000, 30000, 35000
```

```text
section  start_ms  end_ms  activation_change_l2_sum  projection_change_l2_sum  projection_afterimage_dot_sum
0        0         5000    5.1760447501894085        8.307181311954762         541.9764973390807
1        5000      10000   3.453645214834121         13.124772615429276        704.3386774675043
2        10000     15000   2.8245940025481255        8.624412338600742         841.3394759235044
3        15000     20000   2.968547456956698         8.820886410167622         716.8891704392313
4        20000     25000   2.2639054155697154        7.427014952507242         807.4590339100956
5        25000     30000   1.8235470334471429        4.842836505812233         868.858818966863
6        30000     35000   2.4065964210648056        13.262670528969135        879.696780162542
```

Diese Werte sind technische Verlaufssummen ueber aktuelle Rezeptorprojektion,
feste symmetrische Diffusion und schnellen Nachhall. Sie begruenden keine
Segment-, Bedeutungs-, Memory- oder Organisationsrolle.

## Aussagegrenze

Getragen ist nur:

> Die auditierte oeffentliche Bildfolge erzeugt im bestehenden visuellen
> Rezeptor-MCM-Pfad eine reproduzierbare passive zeitliche Verlaufskarte, deren
> reale und statische Kontrollpfade getrennt nachgerechnet werden koennen.

Nicht getragen sind Memory, fortwirkende Feldbeziehung nach Angleichung,
natuerliche Organisation, Semantik, autonome Weltteilnahme oder KI.

## Technische Pruefung

```text
13 passed in 1.14s
```

Nach Ergaenzung des Temporal-Runner-Gate-Tests:

```text
14 passed
```

`git diff --check` meldete keinen Befund.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `mcm_field_organism/public_media_source_contract.py`;
- `mcm_field_organism/public_visual_temporal_map.py`;
- `mcm_field_organism/public_visual_world.py`;
- `tools/audit_public_media_source.py`;
- `tools/run_public_visual_temporal_map.py`;
- `tests/test_public_visual_temporal_map.py`;
- lokale Originaldatei `sources/media/Street traffic.webm`;
- `docs/forschung/084_AUDITIERTE_OEFFENTLICHE_VISUELLE_WELT_REPLIKATION.md`.

Eine Zielabweichung ist nicht erkennbar.
