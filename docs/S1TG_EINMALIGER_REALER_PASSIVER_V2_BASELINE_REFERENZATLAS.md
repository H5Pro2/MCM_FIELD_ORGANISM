# S1-TG: Einmaliger realer passiver v2-Baseline-Referenzatlas

## Status und Ausfuehrungsgrenze

S1-TG fuehrte den in S1-TF gebundenen passiven v2-Einmallauf exakt einmal
und unveraendert aus. Vor dem Start war der Arbeitsbaum sauber und alle vier
S1-TG-Zielpfade fehlten.

```text
python -B -m mcm_field_organism.four_node_baseline_reference_single_run --authorization S1-TG_REAL_BASELINE_REFERENCE_ATLAS_ONCE_V2
```

Es gab keinen Retry, keine Reparatur, keinen Modellproducer und keinen
Feldschritt.

## Technisches Laufergebnis

```text
execution_id                = mcm.s1tg.baseline-reference-atlas.once.v2
status                      = BASELINE_REFERENCE_ATLAS_COMPUTABLE
candidate_gate_status       = S1PX_CANDIDATE_GATES_NOT_APPLICABLE
failure_code_count          = 0
input_file_count            = 3
adapter_reconstruction_count = 1
profile_count               = 14
checkpoint_count_per_profile = 40
comparator_call_count       = 1
contrast_count              = 322
pair_count                  = 91
model_producer_count        = 0
field_step_count            = 0
```

Der Comparatorlauf endete nach rund vier Sekunden mit Exitcode null. Diese
Zeit ist nur Prozessprovenienz und kein Leistungsbefund.

## Kanonisches Ergebnisartefakt

```text
path
  reports/s1tg_baseline_reference_atlas_once_v2.json
file_size
  1346921 bytes
file_sha256
  b8df5c0cb010169432b93b1af42b3e5720edc8299060a994298e996bfcbefe3a
artifact_digest
  b63c12967fbab69740341af2f011839652762efcd71c8b29c851511ce0c20a9f
baseline_reference_result_digest
  dd38f95829e04934ffd678956d52e380729042fe5d7710e99d672a92885b3a56
source_inventory_digest
  c202cd042cc20ce2efedb55d7dada447c211050538ab5c67a67f4649bd30a620
source_file_count
  96
```

Nach erfolgreicher atomarer Publikation fehlen Attempt-, Lock- und
Staging-Datei wie vertraglich vorgesehen. Nur das Ergebnisartefakt bleibt
als neue Datei bestehen.

## Nullabilitaetskontrolle

Alle 14 Profile besitzen je 40 Checkpoints. Exakt 14 Records enthalten vier
nullable R-Marker, jeweils nur an:

```text
plan_role       = C_GAP
checkpoint_role = POST_COMPETITION
R               = (None, None, None, None)
```

Weitere nullable Lagen wurden nicht gefunden. S und H bleiben numerisch.

## Gebundene Paarverteilung

Unter der vor S1-TG festgelegten Grenze `D_rel <= 0.05` liefert das Artefakt:

```text
PROFILE_EQUIVALENT = 15
PROFILE_DISTINCT   = 76
total              = 91
```

Die 15 aequivalenten Paare sind vollstaendig die paarweisen Verbindungen
zwischen diesen sechs Baselineprofilen:

```text
A1_FAST_SH
A2_B1_FIXED_ADAPTER
A2_B4_LINEAR_COUPLED
A2_B5_F3_FULL
A2_B6_CONST_V
M4_DTS1_T1
```

Das kleinste gebundene relative Paarmass liegt bei
`0.0018389933951504312` zwischen `A2_B4_LINEAR_COUPLED` und
`A2_B5_F3_FULL`. Das groesste liegt bei `0.9703130772793706` zwischen
`A2_B2_INTEGRATOR` und `M2_DELAY`.

Diese Verteilung beschreibt ausschliesslich Profilnaehe unter der
vorregistrierten 320-Komponenten-Metrik. Sie erzeugt keine Rangfolge, keinen
Sieger und keinen Befund zu Bildung, Abschwaechung, Interferenz, Kapazitaet,
Freigabe, Wiederverwendung oder einer hypothetischen MCM-Memory.

## Entscheidung und naechster Schritt

```text
S1_TG_REAL_PASSIVE_V2_BASELINE_REFERENCE_ATLAS_COMPLETED_ONCE
BASELINE_REFERENCE_ATLAS_COMPUTABLE_WITH_14_PROFILES_322_CONTRASTS_91_PAIRS
NO_CANDIDATE_GATE_NO_FUNCTIONAL_DECISION_NO_MEMORY_CLAIM
```

Der einzige naechste Schritt ist S1-TH als statischer, kandidatneutraler
Atlas-Abnahme- und Redundanzaudit. Er darf nur die kanonische Integritaet,
die gebundene 15/76-Paarstruktur und ihre Bedeutung fuer die spaetere faire
Baselineabdeckung pruefen. Keine Gleichung, keine Parameteranpassung, kein
Comparator-Retry, kein Modelllauf, kein Feldlauf und keine
Kandidatenentscheidung sind dabei zulaessig.
