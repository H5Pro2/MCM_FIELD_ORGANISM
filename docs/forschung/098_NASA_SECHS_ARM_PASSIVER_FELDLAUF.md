# NASA-Sechs-Arm: passiver Feldlauf

## Freigabe und Grenze

Die Ausfuehrungssperre wurde ausschliesslich fuer den fest vorregistrierten
Sechs-Arm-Lauf mit `0,5 s` Dauer aufgehoben. Feldmechanik, Dockgeometrie,
Zeitteilung und Messrollen blieben unveraendert. Jeder Arm begann mit einem
frischen Feld.

## Befund

```text
Arm                         Ereignisse  Schritte
joint.coarse                56           1
joint.fine                  56          55
joint.fine.reproduction     56          55
joint.fine.permuted         56          55
auditory_only.fine          41          41
visual_only.fine            15          15
```

```text
joint_reproduction_exact:       true
permutation_activation_linf:    0.0
permutation_afterimage_linf:    0.0
coarse_fine_activation_linf:    7.008282842946301e-16
coarse_fine_afterimage_linf:    1.8908485888147197e-16
auditory_only_activation_linf:  0.03144900018938575
visual_only_activation_linf:    0.00013891079174982966
```

## Einordnung

Frische Wiederholung und vertauschte Sequenzdeklaration waren exakt invariant.
Die grob/fein-Abweichung liegt im Bereich der Gleitkommasummation. Beide
Einzelmodalitaetsarme unterscheiden sich vom gemeinsamen Arm. Das zeigt nur,
dass beide reduzierten Quellen im linearen gemeinsamen Feldbezug technisch
wirksam waren.

Der Lauf prueft keine spaetere Wahrnehmung, keine Rueckkopplung, keine
Stabilisierung ueber Weltwiederkehr und keine neu gebildete Organisation. Er
belegt daher weder Memory noch Bedeutung, Organisation oder eigenstaendige KI.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `mcm_field_organism/public_av_six_arm_field_runner.py`;
- `mcm_field_organism/public_av_field_preregistration.py`;
- `mcm_field_organism/neutral_asynchronous_field_runtime.py`;
- `mcm_field_organism/field_time_partition.py`;
- lokale Datei `sources/media/NASA Earthrise Realtime Apollo 8.mp4`.

Externe Quellen wurden nicht verwendet. Eine Zielabweichung ist nicht
erkennbar.
