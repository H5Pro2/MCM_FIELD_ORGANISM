# Vorregistrierung: passiver gemeinsamer NASA-Verlaufslauf

## Entscheidung

Die Vorregistrierung eines auf `0,5 s` begrenzten passiven gemeinsamen
Verlaufslaufs ist technisch zulaessig. Sie fixiert nur Eingangsartefakte,
Vergleichsarme, Messrollen und Invarianten. Sie erteilt weder die Freigabe zur
Runnerimplementierung noch zur Feldausfuehrung.

## Fixierte Eingangsartefakte

```text
source_id:
public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20

clock_id:
public.media.pts_ns

duration_limit_ticks:
500000000

auditory_input_digest:
501476111cdd3d17e9b5249b3774dc7918c8ffb8123264c16ce775ba5f6a175f

visual_input_digest:
86e9d1a2b1c01959f52d2446f855078dc313341f638bc8e23f43fcf79ea48d93
```

## Vorregistrierte Arme

1. `joint.coarse`: beide Modalitaeten, ein grober Zeitschritt.
2. `joint.fine`: beide Modalitaeten, verlustfreie Teilung an Abschlussticks.
3. `joint.fine.reproduction`: frische Wiederholung des feinen Arms.
4. `joint.fine.permuted`: feine Teilung mit vertauschter Sequenzdeklaration.
5. `auditory_only.fine`: nur auditive Rezeptorereignisse.
6. `visual_only.fine`: nur visuelle Rezeptorereignisse.

Jeder Arm muss mit einem frischen, identisch konstruierten Feld beginnen. Es
gibt keine Zustandsuebernahme zwischen Armen.

## Vorregistrierte Messrollen

- Zahl der Quellenereignisse und Abschlussgruppen;
- Zahl gemischter Abschlussgruppen;
- Zahl der Feldvorschlagsschritte und letzter Abschlusstick;
- Aktivierungs- und Nachhallvektor;
- L-inf-Abstaende zwischen vorregistrierten Armen;
- Layer- und Snapshot-Digest.

Es werden keine Labels, Bedeutungen, Rewards, Zielantworten oder gewuenschten
Topologien definiert. Insbesondere wird kein Mindestabstand als positives
Erfolgskriterium vorgegeben.

## Invarianten

- identische Feldparameter und Dockgeometrie in allen Armen;
- frisches Feld pro Arm;
- keine Feld- oder Rezeptorrueckkopplung;
- keine Medienmetadaten als Eingang;
- keine Rohsamples oder Pixel im Ergebnis;
- keine nachtraegliche Aenderung von Armen oder Messrollen.

## Freigabegrenze

```text
preregistration_complete:             true
field_runner_implementation_allowed:  false
field_run_allowed:                    false
memory_claim_allowed:                 false
meaning_claim_allowed:                false
organization_claim_allowed:           false
ai_claim_allowed:                     false
```

Der urspruenglich vorgesehene vollstaendig zurueckgehaltene Kontrollarm wurde
nach dem Kompatibilitaetsaudit entfernt: Die bestehende Runtime verlangt
mindestens eine Rezeptorsequenz. Eine neue Nullereignis-Sonderbehandlung wird
nicht nur fuer diesen Versuch eingefuehrt.

Vor einer Ausfuehrung muss erneut geprueft werden, ob der vorhandene lineare
Feldpfad alle sechs Arme ohne Sonderbehandlung darstellen kann. Erst danach
darf ueber Runnerimplementierung und anschliessend nochmals gesondert ueber
die eigentliche Feldausfuehrung entschieden werden.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `mcm_field_organism/public_av_receptor_run.py`;
- `mcm_field_organism/asynchronous_audio_video_partition_probe.py`;
- `docs/forschung/062_ASYNCHRONE_AUDIO_VIDEO_RATEN_PARTITION_LAUF_164.md`;
- `docs/forschung/093_NASA_AUDIOVIDEO_REZEPTORLAUF_OHNE_FELD.md`.

Externe Quellen wurden nicht verwendet. Eine Zielabweichung ist nicht
erkennbar.
