# NASA passiver Feldpfad-Kompatibilitaetsaudit

## Zweck

Dieser Audit prueft rein strukturell, ob der vorhandene lineare asynchrone
Feldpfad die sieben vorregistrierten Vergleichsarme aus Forschung 094 mit
identischer Dockgeometrie und identischen Feldparametern darstellen kann.

Es wurde kein Feldrunner implementiert und kein Feldlauf ausgefuehrt.

## Gepruefte Grundlage

- Vorregistrierung: `public.av.nasa-earthrise.passive-field.v1`
- Quelle: `public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20`
- Uhr: `public.media.pts_ns`
- Dauer: `500000000` Ticks
- Auditive Eingangssequenz:
  `501476111cdd3d17e9b5249b3774dc7918c8ffb8123264c16ce775ba5f6a175f`
- Visuelle Eingangssequenz:
  `86e9d1a2b1c01959f52d2446f855078dc313341f638bc8e23f43fcf79ea48d93`

## Dockgeometrie

Der bestehende gemeinsame Audio-Video-Dockvertrag kann fuer alle Arme aus dem
gemeinsamen Referenzvertrag abgeleitet werden:

```text
auditory -> dock.auditory -> 48 Traeger
visual   -> dock.visual   -> 240 Traeger
```

Die Einzelmodalitaetsarme benoetigen dadurch keine andere Dockgeometrie. Sie
koennen als Teilmenge der vorhandenen Rezeptorsequenzen gegen dieselbe
Feldanatomie auditiert werden.

## Armbefund

```text
joint.coarse                         existing_runtime_accepts_arm: true
joint.fine                           existing_runtime_accepts_arm: true
joint.fine.reproduction              existing_runtime_accepts_arm: true
joint.fine.permuted                  existing_runtime_accepts_arm: true
auditory_only.fine                   existing_runtime_accepts_arm: true
visual_only.fine                     existing_runtime_accepts_arm: true
auditory_visual.withheld_control     existing_runtime_accepts_arm: false
```

Der blockierte Arm ist der vollstaendig zurueckgehaltene Kontrollarm:

```text
blocker:
existing neutral asynchronous runtime requires at least one receptor sequence
and positive source support
```

## Entscheidung

Der vorhandene lineare Feldpfad ist fuer die vier gemeinsamen Arme und beide
Einzelmodalitaetsarme strukturell kompatibel. Der vollstaendig zurueckgehaltene
Kontrollarm ist dagegen mit dem vorhandenen Runtime-Vertrag nicht ohne
Sonderregel darstellbar.

Damit sind nicht alle sieben vorregistrierten Arme durch den bestehenden
Feldpfad abgedeckt. Eine Feldrunner-Implementierung ist auf dieser Grundlage
nicht freigegeben.

## Freigabegrenze

```text
all_preregistered_arms_representable_by_existing_runtime: false
single_modality_arms_supported:                         true
withheld_control_supported_without_special_rule:         false
field_runner_implementation_allowed:                     false
field_run_allowed:                                       false
synthetic_media_introduced:                              false
special_rules_introduced:                                false
memory_claim_allowed:                                    false
meaning_claim_allowed:                                   false
organization_claim_allowed:                              false
ai_claim_allowed:                                        false
```

Es wurden keine kuenstlichen Medieninhalte eingefuehrt, keine Medienmetadaten
verwendet und keine Sonderregel implementiert.

## Naechster begrenzter Schritt

Vor jeder Feldrunner-Implementierung muss ein korrigierter, rein technischer
Kontrollarmvertrag formuliert und vorregistriert werden. Dieser muss den
vollstaendig zurueckgehaltenen Kontrollarm entweder als gueltigen Nullereignis-
Arm im bestehenden Feldpfad nachweisbar machen oder den Arm aus der
Vergleichsmenge entfernen und die Vorregistrierung entsprechend korrigieren.

Eine Feldausfuehrung bleibt gesperrt.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `mcm_field_organism/public_av_field_preregistration.py`;
- `mcm_field_organism/public_av_receptor_run.py`;
- `mcm_field_organism/asynchronous_audio_video_partition_probe.py`;
- `mcm_field_organism/neutral_asynchronous_field_runtime.py`;
- `mcm_field_organism/shared_mcm_field.py`;
- `mcm_field_organism/finite_audio_video_field_run.py`;
- `docs/forschung/094_VORREGISTRIERUNG_NASA_PASSIVER_GEMEINSAMER_VERLAUFSLAUF.md`;
- lokale Datei `sources/media/NASA Earthrise Realtime Apollo 8.mp4`.

Externe Quellen wurden nicht verwendet. Eine Zielabweichung ist nicht erkennbar.
