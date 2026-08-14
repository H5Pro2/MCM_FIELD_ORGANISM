# Korrigierte NASA-Feld-Vorregistrierung

## Entscheidung

Der in Forschung 095 identifizierte Blocker wird durch Korrektur der
Vorregistrierung aufgeloest. Der Arm
`auditory_visual.withheld_control` wird entfernt.

Eine allgemeine Nullereignisfunktion wird nicht implementiert, weil sie fuer
die sechs durch den vorhandenen linearen Feldpfad bereits darstellbaren Arme
nicht erforderlich ist. Eine nur fuer diesen Vergleich eingefuehrte Ausnahme
waere eine Sonderregel und methodisch schwaecher als die Entfernung des nicht
darstellbaren Arms.

## Korrigierte Vergleichsmenge

```text
joint.coarse
joint.fine
joint.fine.reproduction
joint.fine.permuted
auditory_only.fine
visual_only.fine
```

Die Einzelmodalitaetsarme bleiben als Gegenbaselines erhalten. Grobe und feine
Zeitteilung, frische Reproduktion und vertauschte Sequenzdeklaration bleiben
ebenfalls erhalten.

## Struktureller Befund

```text
arm_count:                                               6
all_preregistered_arms_representable_by_existing_runtime: true
single_modality_arms_supported:                           true
synthetic_media_introduced:                               false
special_rules_introduced:                                 false
field_runner_implementation_allowed:                      false
field_run_allowed:                                        false
```

Die Korrektur beseitigt nur den Vorregistrierungswiderspruch. Sie erteilt
weder eine Runner- noch eine Feldfreigabe und begruendet keine Memory-,
Bedeutungs-, Organisations- oder KI-Aussage.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `mcm_field_organism/public_av_field_preregistration.py`;
- `mcm_field_organism/public_av_field_path_compatibility.py`;
- `docs/forschung/094_VORREGISTRIERUNG_NASA_PASSIVER_GEMEINSAMER_VERLAUFSLAUF.md`;
- `docs/forschung/095_NASA_PASSIVER_FELDPFAD_KOMPATIBILITAETSAUDIT.md`.

Externe Quellen wurden nicht verwendet. Eine Zielabweichung ist nicht
erkennbar.
