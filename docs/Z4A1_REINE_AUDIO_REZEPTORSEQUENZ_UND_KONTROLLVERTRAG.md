# Z4-A1: Reine Audio-Rezeptorsequenz und Kontrollvertrag

Stand: 2026-08-06

Status:

- Referenzquelle, unabhaengige Kontrollquelle und Rezeptorreduktion statisch
  gebunden;
- Zeitabbildung und kanonisches Digestformat statisch gebunden;
- Kontrollquelle und Sequenzadapter implementiert;
- Referenz und Kontrolle jeweils frisch reproduziert und digestgebunden;
- fokussierte technische Tests bestanden;
- kein Feld und kein Forschungslauf ausgefuehrt.

## Zweck

Z4-A1 schliesst ausschliesslich die Spezifikationsluecke der reinen
Audiowelt W-A aus der
[Z4-A-Vorregistrierung](Z4A_MEHRWELT_FELDENCODER_VORREGISTRIERUNG_UND_AUSFUEHRUNGSSPERRE.md).
Der Vertrag entscheidet noch keine Feldencoderfunktion. Er legt fest, welche
Audioereignisse ein spaeterer technischer Adapter ohne Labels, Rohdatenablage
oder Ergebnisanpassung in `ReceptorTimeSequence` ueberfuehren muss.

## Gemeinsames technisches Budget

Referenz und unabhaengige Kontrolle verwenden unveraendert:

```text
sample_rate:              48000 Hz
source_frame_size:        480 samples
source_frame_duration:    0.01 s
source_frame_count:       6000
source_duration:          60 s
component_count:          3
component_amplitude:      0.2 je Komponente
summed_amplitude_bound:   0.6
phase_schedule:           contact 20 s, mute 20 s, contact 20 s
phase_frame_counts:       2000, 2000, 2000
initial_phase_per_tone:   0 rad
raw_sample_retention:     forbidden
```

Die Phasen-IDs sind nur Quellen- und Observermetadaten. Sie duerfen weder in
Rezeptorwerte noch in Feldzustaende geschrieben werden.

## W-A-Referenz

```text
world_id:                z4a.audio.sound-mute-sound.v1
source_factory:          sound_mute_sound_20s_source
frequencies_hz:          250, 1000, 4000
gains:                   1, 0, 1
source_clock:            audio.sample
```

Der zweite Kontakt ist eine exakte Wiederholung des ersten Kontakts. Die
bestehende Quelle setzt den lokalen Sampleindex am Beginn jeder Phase auf
null. Das ist Teil der gebundenen Quelle und wird nicht nachtraeglich
veraendert.

## W-A-unabhaengige Kontrolle

```text
world_id:                z4a.audio.shifted-sound-mute-sound.v1
source_factory_target:   shifted_sound_mute_sound_20s_source
frequencies_hz:          375, 1500, 6000
gains:                   1, 0, 1
source_clock:            audio.sample
```

Die Kontrolle verschiebt jede Referenzfrequenz um den vorab festen Faktor
`1.5`. Alle Frequenzen bleiben unter Nyquist und unterscheiden sich von den
Referenzfrequenzen. Dauer, Framezahl, Anzahl der Komponenten,
Komponentenamplitude, Gainfolge und Rezeptorgeometrie bleiben identisch.

Diese Kontrolle wurde gewaehlt, weil:

- reine Stille keinen gleichwertigen aktiven Weltverlauf bildet;
- eine Amplitudenaenderung das technische Anregungsbudget veraendern wuerde;
- eine reine Phaseninversion durch den Spektralrezeptor zusammenfallen kann;
- Zufallsrauschen eine zusaetzliche Generator- und Seedabhaengigkeit
  einfuehren wuerde.

Die Frequenzverschiebung ist keine Klasse und kein Zielsignal. Sie ist nur
eine vorab festgelegte andere Audioquelle derselben technischen Familie.

## Gebundener Rezeptorpfad

Beide Quellen verwenden einen jeweils frischen Pfad:

```text
receptor:                LogSpectralReceptor
path:                    BroadbandHearingPath
sample_rate:             48000 Hz
window_size:             4800 samples
hop_size:                480 samples
min_frequency:           50 Hz
max_frequency:           18000 Hz
band_count:              48
geometry_id:             auditory.log48.50-18000.w4800.h480.v1
warmup_hops:             10
receptor_state_count:    5991
snapshot_ids:            auditory.receptor.0 .. auditory.receptor.5990
carrier_order:           LogSpectralReceptor.channel_ids
```

Der rollende Rezeptor gibt nach dem zehnten Eingangsframe den ersten Zustand
aus. Der erste Zustand umfasst rezeptorseitig die Samples `0..4800`, der
letzte `2875200..2880000`. Die 48 Energiewerte werden unveraendert ueber
`from_auditory_receptor_state` in `ReceptorContactFrame.values` uebernommen.

## Zeitabbildung in `ReceptorTimeSequence`

Die Rezeptoranalysefenster ueberlappen absichtlich. Die aeusseren
Abschlussintervalle der `ReceptorTimeSequence` duerfen dagegen nicht
ueberlappen. Fuer Rezeptorzustand `i` mit `i = 0..5990` gilt daher:

```text
completion_end_sample(i)   = 4800 + 480 * i
completion_start_sample(i) = completion_end_sample(i) - 480

frame.clock_id:             audio.sample
frame.window_start_tick:    completion_end_sample(i) - 4800
frame.window_end_tick:      completion_end_sample(i)

sequence.clock_id:          z4a.audio.sample
field_time.start_tick:      completion_start_sample(i)
field_time.end_tick:        completion_end_sample(i)
ticks_per_second:           48000
```

Damit traegt `frame.window_*` das reale 100-ms-Analysefenster und
`field_time` ausschliesslich den 10-ms-Abschluss-Support des neuen Zustands.
Es wird keine zusaetzliche Zeitvariable und keine relative Feldzeit
eingefuehrt.

Gebundene Randwerte:

```text
first frame source window:       0..4800
first field completion support:  4320..4800
last frame source window:        2875200..2880000
last field completion support:   2879520..2880000
runner proposal horizon:         0..2880000
```

Ein spaeterer Runner muss den leeren technischen Vorlauf `0..4320` getrennt
von den echten 5991 Abschlussgruppen behandeln. Er darf ihn nicht als
Sachstuetzpunkt in die Trajektorienmetrik aufnehmen.

## Erwartete Kontaktverteilung

Die bestehende deterministische Kette bindet folgende strukturelle
Kontrollen fuer beide Quellen:

```text
contact.1 receptor states:  1991
mute receptor states:       2000
contact.2 receptor states:  2000
active_zero in mute:        1991
total receptor states:      5991
```

Die ersten neun Rezeptorzustaende nach Beginn der Mutephase enthalten noch
Anteile des vorherigen 100-ms-Analysefensters. Entsprechend erreicht die
Mutephase erst nach neun weiteren Hops `ACTIVE_ZERO`. Diese Uebergangswerte
duerfen nicht abgeschnitten, ersetzt oder als Fehler behandelt werden.

## Kanonische Digests

Der `source_contract_digest` verwendet je Quelle exakt folgende Payload;
`frequencies_hz` ist fuer die Kontrolle durch `[375.0,1500.0,6000.0]` und
`world_id` durch `z4a.audio.shifted-sound-mute-sound.v1` zu ersetzen:

```json
{
  "component_amplitude": 0.2,
  "frequencies_hz": [250.0, 1000.0, 4000.0],
  "phase_local_sample_reset": true,
  "phases": [
    {"duration_seconds": 20.0, "gain": 1.0, "phase_id": "contact.1"},
    {"duration_seconds": 20.0, "gain": 0.0, "phase_id": "mute"},
    {"duration_seconds": 20.0, "gain": 1.0, "phase_id": "contact.2"}
  ],
  "sample_rate": 48000,
  "source_frame_size": 480,
  "world_id": "z4a.audio.sound-mute-sound.v1"
}
```

Fuer Referenz und Kontrolle sind spaeter getrennt zu bilden:

1. `source_contract_digest`: SHA-256 ueber eine kanonische JSON-Darstellung
   der oben gebundenen Quellparameter;
2. `receptor_sequence_digest`: unveraenderte Funktion
   `mcm_f3_receptor_sequences_digest((sequence,))`;
3. `reproduction_sequence_digest`: dieselbe Funktion ueber eine zweite,
   vollstaendig frische Erzeugung;
4. `implementation_digest`: SHA-256 des spaeteren Adaptermoduls.

JSON verwendet `sort_keys=True`, `separators=(",", ":")`,
`ensure_ascii=True`, `allow_nan=False` und ASCII-Encoding. Rohsamples werden
weder Teil eines Ergebnisartefakts noch dauerhaft gespeichert.

Ein Digestwert wird erst eingetragen, nachdem der Adapter implementiert und
die identische frische Wiederholung technisch bestaetigt ist. In diesem
Dokument werden keine Werte vorausberechnet oder geraten.

## Technische Implementierung und Bindung

Implementiert:

```text
mcm_field_organism/controlled_audio_phase_source.py
mcm_field_organism/z4a_audio_receptor_source.py
tools/audit_z4a_audio_binding.py
tests/test_z4a_audio_receptor_source.py
```

Implementierungsdigests:

```text
controlled_audio_phase_source.py sha256:
0df2ac7eaff146644a51526f3e91c3481f138f68750054821e43831e932e6764

z4a_audio_receptor_source.py sha256:
b17d6627850959b4a39514dccd861b1204031cc71302df44ca2cbef173fde983
```

Finale Referenzbindung:

```text
source_contract_digest:
742ea506e8558e448470c7a7e07824ce4591d087ab71cf5dd39d93d720eae1df

receptor_sequence_digest:
b35631404e9c0873ebbe41e02cf06db0b2bfd15aabb8964fe504e51c04b088a5

reproduction_sequence_digest:
b35631404e9c0873ebbe41e02cf06db0b2bfd15aabb8964fe504e51c04b088a5
```

Finale unabhaengige Kontrollbindung:

```text
source_contract_digest:
e0fbdb2807ece7631ba323723d9ad96853d316563025c8b5e87da80bf1750840

receptor_sequence_digest:
cc2b84a75ccaa46392fba9e751a0d16b0c7fe8ba0eb15251a0229d3bf2d31951

reproduction_sequence_digest:
cc2b84a75ccaa46392fba9e751a0d16b0c7fe8ba0eb15251a0229d3bf2d31951
```

Beide Welten liefern:

```text
source_frames:              6000
receptor_states:            5991
active_zero:                1991
active_energy:              4000
first_completion_support:   4320..4800
last_completion_support:    2879520..2880000
raw_samples_retained:       false
receptor_sequences_retained:false
```

Alle fuenf Auditkontrollen bestanden. Referenz und Kontrolle sind intern
exakt reproduzierbar und untereinander verschieden.

## Abgeleitete Z4-A-Arme

Nach erfolgreicher technischer Bindung werden aus der Referenzsequenz ohne
erneute Rezeptoranalyse abgeleitet:

- `reference`: unveraenderte kanonische Sequenz;
- `reproduction`: frische Quelle und frischer Rezeptorpfad;
- `partitioned`: identische Ereignisse, nur leere Integrationsintervalle
  halbiert;
- `reversed`: die 5991 Wertevektoren in umgekehrter Reihenfolge auf denselben
  5991 Abschluss-Supports;
- `permuted`: vier zusammenhaengende Bloecke mit fester Reihenfolge
  `0,3,2,1`; die ersten drei Bloecke enthalten 1498 Zustande, der letzte 1497;
- `independent`: frisch erzeugte frequenzverschobene Kontrollsequenz.

Bei `reversed` und `permuted` bleiben Snapshot-IDs, Abschluss-Supports und
Carrierreihenfolge der Zielposition erhalten; nur der vollstaendige
48-Wertevektor wird aus der festgelegten Quellposition uebernommen. Die
Transformation darf Werte nicht kanalweise mischen.

## Abgeschlossene technische Z4-A1-Abnahme

Z4-A1 ist technisch implementiert und ohne Forschungsnummer abgenommen. Die
Abnahme hat gezeigt:

- exakt 6000 Eingangsframes und 5991 Rezeptorzustaende je Quelle;
- exakt 48 Werte je Zustand und die gebundene Geometrie;
- nur endliche Werte im normierten Rezeptorvertrag;
- nicht ueberlappende, streng geordnete Abschluss-Supports;
- erwartete Kontaktverteilung und exakte Nullwerte im stabilen Mutebereich;
- identische Referenz- und Wiederholungsdigests;
- voneinander verschiedene Referenz- und Kontrolldigests;
- unveraendertes Ereignis- und Werteinventar in Umkehrungs- und
  Permutationsarm;
- Observer an/aus veraendert keinen Zustandsdigest;
- keine Rohsamplepersistenz und keine Phasen-ID im Feldhandoff.

Jede Abweichung sperrt W-A mit `FIELD_ENCODER_NOT_TECHNICALLY_STABLE`. Es
werden dann keine Feldtrajektorien interpretiert.

## Aussagegrenze

Der Vertrag spezifiziert eine kontrollierte reine Audiowelt und ihre
technische Gegenquelle. Er belegt keine Wahrnehmung, Wiedererkennung,
Praegung, Semantik, Organisation, relative Feldzeit, Memory oder KI.

## Aktuelle Entscheidung

`Z4A1_TECHNICALLY_BOUND`

Spezifikation, Implementierung und Digestabnahme der reinen Audiowelt sind
geschlossen. Daraus folgt noch keine Feldencoder- oder Forschungsentscheidung.
Die Z4-A-Vollmatrix bleibt wegen der anderen offenen Scheiben gesperrt.

## Bester naechster Schritt

Die noch offene Z4-A2-Browserweltbindung implementieren. Z4-A1 bleibt dabei
unveraendert gebunden; keine Vier-Welten-Matrix und keinen Lauf 197 starten.
