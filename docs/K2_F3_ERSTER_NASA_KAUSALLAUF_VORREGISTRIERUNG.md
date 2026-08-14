# K2/F3: Vorregistrierung des ersten NASA-Kausallaufs

Stand: 2026-08-06

Status:

- vor Einsicht in ein F3-Ergebnis gebunden;
- ausschliesslich kontrollierte oeffentliche AV-Datei;
- keine Kamera, kein Live-Mikrofon und keine physische Sensorik;
- kein Memory-, Organisations-, Topologie-, Semantik- oder KI-Claim.

## 1. Forschungsfrage

Erzeugt die aktive K2/F3-Kopplung unter einer bereits auditierten gemeinsamen
Audio-Video-Rezeptorfolge

1. eine M-Umverteilung gegen P0 und `kappa = 0`,
2. eine von `eta` abhaengige Rueckwirkung auf S/H und
3. eine mit n/2n/4n abnehmende numerische Verfeinerungsabweichung?

Dies ist eine erste Kausal- und Integrationspruefung. Sie untersucht keine
Praegung und kein Memory.

## 2. Gebundene Quelle

```text
source_id: public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20
path: sources/media/NASA Earthrise Realtime Apollo 8.mp4
size: 13547755 Byte
sha1: c63198a925ad227950cca597c4a8500656bacdfc
clock: public.media.pts_ns
interval: [0, 500000000)
```

Rezeptorreduktion:

```text
Audio: LogSpectralReceptor, 48000 Hz, Hop 480, Fenster 0,1 s
Video: LocalChannelGridReceptor, 320 x 240 BGR, Raster 10 x 8
auditory frames: 41
visual frames: 15
auditory digest: 501476111cdd3d17e9b5249b3774dc7918c8ffb8123264c16ce775ba5f6a175f
visual digest: 86e9d1a2b1c01959f52d2446f855078dc313341f638bc8e23f43fcf79ea48d93
```

Der Lauf bricht vor F3 ab, wenn Integritaet, Wiederholbarkeit, Framezahlen oder
Digests abweichen.

## 3. Gebundene Feld- und F3-Parameter

```text
Proposal-Partition: completion_fine
S response_time_seconds: 1.0
H time_constant_seconds: 0.5
Dissipation: keine
M initial_total_mass: 1.0, gleichfoermig
lambda_sm_per_second: 1.0
kappa: 0.5
eta: 1.0
```

`lambda_sm` entspricht der bestehenden S-Antwortrate von `1/s`. `kappa` nutzt
die bereits bewiesene zulaessige Grenze, damit die vorab gerichtete
Kraftkomponente im kurzen Intervall messbar bleibt. `eta = 1` bindet die
Rueckarbeit ohne zusaetzlichen Skalensweep an die normierte Gesamtmasse. Diese
Werte werden nach dem Ergebnis nicht korrigiert.

## 4. Gebundene Arme

```text
p0.exact
p1.n
p1.2n
p1.4n
b.eta-null
b.kappa-null
b.kappa-inverted
```

Alle Arme erhalten denselben einmal gebildeten Rezeptor-Handoff. Ablationen
und Vorzeicheninversion verwenden 4n.

## 5. Messungen

- M-Linf und M-L2 gegen die gleichfoermige Anfangsverteilung;
- S/H-Linf von P1-4n gegen P0;
- S/H-Linf von P1-4n gegen `eta-null`;
- M-Linf von P1-4n gegen `kappa-null` und `kappa-inverted`;
- Gesamtzustands-L2 zwischen n/2n und 2n/4n;
- M-Gesamtmassenfehler, kleinstes M, maximale S/H-Auslenkung;
- Snapshots und technische Subschrittdiagnosen je Arm.

## 6. Entscheidung und Stopplinien

Ein technisch verwertbarer enger Kausalbefund erfordert gleichzeitig:

- nichttriviale M-Verschiebung in P1;
- Trennung von `kappa-null` und der Vorzeicheninversion;
- nichttriviale S/H-Trennung zu `eta-null`;
- kleinere 2n/4n- als n/2n-Abweichung;
- eingehaltene M-, S- und H-Invarianten.

Scheitert eine Bedingung, wird der Befund als Nullbefund, Parametergrenze oder
numerisch unentschieden berichtet. Parameter werden nicht nachgestellt und
der Lauf wird nicht automatisch wiederholt.

Auch ein positiver enger Befund belegt nur Transport, gebundene Rueckwirkung
und numerische Verfeinerung unter einer einzelnen AV-Folge. Er belegt keine
Praegung, Feldzeitverdichtung, Loesung, Wiederpraegung, Memory, Organisation,
Topologie, Semantik oder KI.

## 7. Verwendete Projektquellen

- `docs/forschung/090_AUDITIERTE_NASA_AUDIOVIDEO_ROHQUELLEN.md`
- `docs/forschung/091_NASA_AUDIOVIDEO_ROHQUELLEN_INTERVALLAUDIT.md`
- `docs/forschung/092_NASA_AUDIOVIDEO_REZEPTOR_VORABNAHME.md`
- `docs/forschung/093_NASA_AUDIOVIDEO_REZEPTORLAUF_OHNE_FELD.md`
- `mcm_field_organism/public_av_six_arm_field_execution.py`
- `mcm_field_organism/mcm_f3_causal_runner.py`
- `docs/K2_MATHEMATISCHER_F3_MINIMALVERTRAG.md`

## 8. Laufnummer

Der letzte nachweislich ausgefuehrte Forschungsdurchlauf ist Lauf 187.
Dokumentnummern 188 ff. waren technische oder statische Dokumente und werden
nicht als Laufstand verwendet. Nur bei tatsaechlicher Ausfuehrung dieses
Vertrags entsteht Lauf 188.
