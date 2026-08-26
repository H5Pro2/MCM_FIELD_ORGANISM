# Vorregistrierung: NASA zweistufige oeffentliche Weltwiederkehr

## Entscheidung

Der naechste begrenzte Schritt wird ausschliesslich vorregistriert. Es wird
kein Runner implementiert und kein Feldlauf ausgefuehrt.

Die auditierte NASA-Audio-Video-Sequenz von `0,5 s` soll spaeter zweimal
verarbeitet werden. Verglichen wird ein Arm mit Feldfortsetzung zwischen den
Stufen gegen eine Gegenbaseline, die vor Stufe zwei mit einem frischen Feld
beginnt.

## Fixierte Quelle

```text
source_id:
public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20

clock_id:
public.media.pts_ns

stage_duration_ticks:
500000000

auditory_sequence_digest:
501476111cdd3d17e9b5249b3774dc7918c8ffb8123264c16ce775ba5f6a175f

visual_sequence_digest:
86e9d1a2b1c01959f52d2446f855078dc313341f638bc8e23f43fcf79ea48d93
```

Beide Stufen verwenden dieselbe reduzierte Sequenz. Es werden keine neuen
Medieninhalte, Labels, Untertitel, Beschreibungen oder Metadaten als Eingang
zugelassen.

## Vorregistrierte Arme

```text
continued_field
fresh_stage_two_baseline
```

`continued_field`:

- Stufe eins beginnt mit frischem Feld;
- dieselbe `0,5 s`-Sequenz wird verarbeitet;
- danach folgt ein festes Zwischenintervall;
- der resultierende Feldzustand wird in Stufe zwei uebernommen;
- Stufe zwei verarbeitet dieselbe `0,5 s`-Sequenz erneut.

`fresh_stage_two_baseline`:

- Stufe eins ist technisch gleich registriert;
- fuer Stufe zwei wird jedoch ein frisches Feld verwendet;
- dieselbe `0,5 s`-Sequenz wird in Stufe zwei verarbeitet;
- die Stufe-zwei-Ausgabe dient als Gegenbaseline ohne Feldfortsetzung.

## Zwischenintervall und Aufloesungsphase

```text
intermediate_interval_ticks: 100000000
resolution_phase:           no_input_gap.step_time_only
```

Das Zwischenintervall ist eine technische Aufloesungsphase ohne neue
Rezeptoreingabe. Es darf keine Medien-, Label-, Bedeutungs- oder
Organisationsinformation einfuehren.

## Messrollen

Vorregistriert sind nur technische Differenzmessungen:

- Snapshot-Digest nach Stufe eins;
- Snapshot-Digest nach Aufloesungsphase;
- Snapshot- und Layer-Digest nach Stufe zwei;
- Aktivierungs- und Nachhallvektor nach Stufe zwei;
- L-inf-Differenz der Stufe-zwei-Aktivierung zwischen den Armen;
- L-inf-Differenz des Stufe-zwei-Nachhalls zwischen den Armen;
- Gleichheit von Stufe-zwei-Layer- und Snapshot-Digest.

Es wird keine Memory- oder Organisationsschwelle definiert.

## Invarianten

- dieselbe auditierte Quelle in beiden Stufen;
- dieselbe reduzierte Sequenz in beiden Stufen;
- identische Dockgeometrie und Feldparameter;
- identisches Zwischenintervall in allen Armen;
- identische Aufloesungsphase in allen Armen;
- keine Rezeptorrueckkopplung;
- keine Feld-zu-Medien-Rueckkopplung;
- keine Metadaten als Eingang;
- keine Rohsamples oder Pixel im Ergebnis;
- keine nachtraegliche Aenderung von Armen oder Messrollen.

## Freigabegrenze

```text
preregistration_complete:       true
runner_implementation_allowed:  false
field_run_allowed:              false
memory_threshold_defined:       false
organization_threshold_defined: false
memory_claim_allowed:           false
meaning_claim_allowed:          false
organization_claim_allowed:     false
ai_claim_allowed:               false
```

Diese Vorregistrierung erlaubt keine Behauptung ueber Memory, Bedeutung,
Organisation oder eigenstaendige KI.

## Naechster begrenzter Schritt

Separat zu pruefen ist, ob ein nicht ausfuehrbarer zweistufiger Runnervertrag
implementiert werden darf, der diese Vorregistrierung nur verdrahtet und eine
konstruktive Ausfuehrungssperre behaelt.

## Tatsaechlich verwendete Quellen

- aktueller Uebergabeauftrag;
- `mcm_field_organism/public_av_six_arm_field_execution.py`;
- `mcm_field_organism/public_av_six_arm_field_runner.py`;
- `mcm_field_organism/public_av_field_preregistration.py`;
- `mcm_field_organism/neutral_asynchronous_field_runtime.py`;
- `mcm_field_organism/field_time_partition.py`;
- `docs/forschung/077_AKTIVES_SHARED_MCM_FIELD_ZWEISTUFIGE_WELTRUECKKEHR_LAUF_180.md`;
- `docs/forschung/098_NASA_SECHS_ARM_PASSIVER_FELDLAUF.md`;
- lokale Datei `sources/media/NASA Earthrise Realtime Apollo 8.mp4`.

Externe Quellen wurden nicht verwendet. Eine Zielabweichung ist nicht
erkennbar.
