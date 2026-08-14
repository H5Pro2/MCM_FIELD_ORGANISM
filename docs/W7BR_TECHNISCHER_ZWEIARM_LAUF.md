# W7-BR: Technischer Baseline-Lauf

Stand: 2026-08-10

Status: `TECHNISCH_AUSGEFUEHRT_DREIARME_VERGLICHEN`

## Umfang

Ausgefuehrt wurde der freigegebene synthetische Audio-/Video-Testpfad mit
der gebundenen Weltfamilie:

```text
controlled_history_holdout_world_family()
contact.0 -> gap.0 -> contact.1 -> probe.0
```

Es wurden keine Kamera, kein Live-Mikrofon, keine physische Sensorik und
keine externen Medien verwendet.

## Vergleichsarme

| Arm | technische Konfiguration |
| --- | --- |
| `p0.null` | `lambda_sm_per_second = 0.0`, `kappa = 0.5`, `eta = 1.0` |
| `leaky` | gleiche Integration, Kopplungsrechner `compute_mcm_f3_local_leaky_baseline` |
| `f3` | `lambda_sm_per_second = 1.0`, `kappa = 0.5`, `eta = 1.0` |

Beide Arme erhielten dieselben vier kontrollierten Batches pro Welt und
`refinement = 1`.

## Ergebnisse

```text
world.history.same
source_batches = 4
f3_snapshot_digest = 13311b4f7048c6ace79a0e1b0b1879aee5d9b6ea035e1d643cdf74d6047a456d
p0_vs_f3_activation_linf = 0.0003416765167586766
p0_vs_f3_afterimage_linf = 0.00030065739231099897
snapshot_digest_equal = false
leaky_vs_f3_activation_linf = 0.0005792702651734039
leaky_vs_f3_afterimage_linf = 0.0005028223364473561
snapshot_digest_equal = false

world.history.changed
source_batches = 4
f3_snapshot_digest = 02ceb46be533d1e0ba5f4eac7717fe39f65a44b195b3320022ae9e2aec711f04
p0_vs_f3_activation_linf = 0.00039217251074041837
p0_vs_f3_afterimage_linf = 0.0002861588916314439
snapshot_digest_equal = false
leaky_vs_f3_activation_linf = 0.0006914457616601366
leaky_vs_f3_afterimage_linf = 0.0005115956939305
snapshot_digest_equal = false
```

## Einordnung

Der Lauf zeigt nur, dass der aktive F3-Arm und der Nullarm unter derselben
synthetischen Rezeptorfolge unterschiedliche technische Feldsnapshots
erzeugen. Das ist ein Kausal- und Reproduzierbarkeitsbefund des vorhandenen
F3-Mechanismus.

Der Lauf belegt nicht:

- Memory oder Praegung;
- Lernen oder Vergessen;
- Feldzeit oder inneren Kontext;
- Organisation, Semantik oder Selbstregulation;
- eine feldbasierte KI.

Der leaky Arm wurde nun mit demselben technischen Integrator und denselben
Eingabebatches ausgefuehrt. Die leaky Kopplungsfunktion ist eine vorhandene
Gegenbaseline und keine neue MCM-Substratarchitektur.

## Laufgrenze

Der zuerst versuchte vollstaendige historische Mehrarm-Runner wurde wegen
der Laufzeitgrenze beendet, bevor ein Ergebnis vorlag. Er erzeugte keinen
Forschungsbefund und wurde nicht als W7-BR-Ergebnis verwendet.

## Wiederholungspruefung

Jede Welt wurde mit identischer Konfiguration ein zweites Mal ausgefuehrt.
Alle drei Baseline-Digests waren pro Welt exakt gleich:

```text
world.history.same
p0.null = 4bd9d41761a352d27ef0806241ab7208f6d3e2b96e6d957369a6d4bdf9549ca7
leaky   = 72c7343ff0d76b34552c2e4fb36658770d5a8c682db9f8661b8525ad84671d56
f3      = 13311b4f7048c6ace79a0e1b0b1879aee5d9b6ea035e1d643cdf74d6047a456d

world.history.changed
p0.null = a29834c8d0140d85ce3070b01c55a2289a333c17ed2daa97a351085dbd1b04d3
leaky   = bebb5e2c04d361e5c234602f5f5ab19b554870ae51944cb8ca70c34cb42599ca
f3      = 02ceb46be533d1e0ba5f4eac7717fe39f65a44b195b3320022ae9e2aec711f04
```

Damit ist fuer diesen technischen Lauf die Wiederholbarkeit der drei
Baselinepfade bestaetigt. Der Befund sagt nichts ueber Lernen oder Memory.

## Entscheidung

```text
synthetischer Dreiarm-Lauf:     abgeschlossen
Nullarm gegen F3:               numerisch verglichen
leaky Arm:                      numerisch verglichen
Memory-Claim:                   nein
Forschungslauf mit Claim:       nein
```

## Bester naechster Schritt

Den technischen Lauf als abgeschlossene Baseline-Charakterisierung
behandeln. Eine Wiedereroeffnung der Substratlinie ist daraus nicht
abzuleiten.
