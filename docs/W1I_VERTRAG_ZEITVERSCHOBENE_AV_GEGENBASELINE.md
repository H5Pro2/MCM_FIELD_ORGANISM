# W1-I: Vertrag einer zeitverschobenen AV-Gegenbaseline

Stand: 2026-08-07

Entscheidung: `W1I_TIME_SHIFTED_AV_BASELINE_CONTRACT_BOUND_NOT_IMPLEMENTED`

Forschungslauf: nein

Browser gestartet: nein

## Forschungsfrage

Erzeugt dieselbe visuelle und auditive Eingangsmenge bei veraenderter
zeitlicher Kopplung einen anderen technischen Verlauf oder Endzustand im
gegenwaertigen neutralen S/H-Feld?

Diese Frage prueft nur zeitliche Eingangssensitivitaet der bestehenden
Feldmechanik. Sie prueft kein Lernen, keine Praegung, keine relative Feldzeit
und kein Memory.

## Warum keine Nullwelt

Eine stumme oder unbewegte Nullwelt wuerde gleichzeitig Eingangsenergie,
Aktivitaet und zeitliche Kopplung veraendern. Eine Differenz waere deshalb
nicht eindeutig der zeitlichen Beziehung zwischen Audio und Video
zuzuordnen.

W1-I verwendet stattdessen eine strukturzerstoerende, aber marginal
angeglichene Kontrolle. Die Bildfolge bleibt unveraendert. Derselbe
Tonabschnitt wird um genau 300 ms in eine spaetere statische Phase
verschoben. Damit ist die einzige beabsichtigte unabhaengige Variation die
zeitliche Audio-Video-Kopplung.

## Gemeinsame feste Welt

Beide Bedingungen verwenden vier Phasen mit je 300 ms:

```text
phase 0: rest.before       static
phase 1: change            moving
phase 2: rest.after.one    static
phase 3: rest.after.two    static
total_duration:            1200 ms
movement_cycles:           1
tone_frequency_hz:         440
```

Gemeinsame Quellenkonfiguration:

```text
canvas:                    120 x 80, device_scale_factor 1
visual_rate:               30 fps
visual_inventory:          36 PNGs
motion_axis:               horizontal
motion_amplitude_fraction: 0.2
foreground_size_fraction:  0.2
background_rgb:            16, 24, 32
foreground_rgb:            224, 232, 240
audio:                     mono sine, 8000 samples/s
audio_hop_size:            80
audio_inventory:           120 PCM-Hops / 9600 Samples
```

Die laengere Phase und 30 fps stellen sicher, dass die Bewegungsphase nicht
nur an ihrer Nullauslenkung abgetastet wird. Jede 300-ms-Phase enthaelt genau
neun visuelle Frames.

## Zwei Bedingungen

### A0: zeitlich gekoppelt

```text
tone_gain by phase:        0.0, 0.2, 0.0, 0.0
visual movement:           nur phase 1
```

Ton und Bewegung liegen im selben 300-ms-Intervall.

### C0: Ton um 300 ms verschoben

```text
tone_gain by phase:        0.0, 0.0, 0.2, 0.0
visual movement:           nur phase 1
```

Die Bildwelt bleibt exakt gleich. Tonfrequenz, Tondauer und Gain bleiben
gleich; nur der Tonbeginn liegt eine Phase spaeter. Die Verschiebung von
300 ms entspricht bei 440 Hz genau 132 Oszillatorzyklen und fuehrt daher
keine beabsichtigte Phasenlagenvariation des Sinussignals ein.

## Identische Rezeptor- und Feldgrenze

Beide Bedingungen muessen unveraendert verwenden:

```text
visual_grid:               3 x 2 x 3 Kanaele
auditory_window_size:      800 Samples
auditory_hop_size:         80 Samples
auditory_band_count:       8
auditory_frequency_range:  50 bis 3000 Hz
expected_visual_states:    36
expected_auditory_states:  111
expected_total_events:     147
field_config:              NeutralLocalFieldSubstrateConfig(1.0)
afterimage_config:         none
initial_field:             fresh and independently built
ticks_per_second:          1000000000
```

Die gegenwaertige W1-H-Konfiguration besitzt hier keine aktive
Afterimage-Konfiguration. Deshalb ist W1-I zunaechst ein Test der aktuellen
schnellen Feldlage S. Eine H-, Nachhall- oder Feldzeitwirkung darf daraus
nicht abgeleitet werden.

## Statischer Handoff-Befund

`advance_audio_video_receptor_sequences()` erzeugt derzeit einen aeusseren
Feldschritt ueber den gesamten Horizont. Dieser Schritt verwirft die innere
Zeitordnung jedoch nicht:

1. `handoff_receptor_completion_groups()` erhaelt alle Abschlussgruppen mit
   ihren gemessenen `completion_tick`-Werten.
2. `map_proposal_batch_to_transient_docks()` bewahrt diese Gruppen geordnet.
3. `project_transient_docks_to_neuron_inputs()` bewahrt pro lokalem Neuron
   die geordneten Kontakte.
4. `advance_neutral_shared_field_transient()` sortiert die Kontakte erneut
   nach Abschlusszeit und entwickelt das Feld zwischen den Zeitpunkten
   weiter.

Die eine aeussere Batchgrenze faltet die 147 Ereignisse daher nicht zu einem
zeitlosen Summenwert. W1-J muss diese Eigenschaft mit synthetischen Tests
absichern, bevor eine reale Paarwelt zulaessig wird.

## Pflichtinvarianten

Ein spaeteres Paar ist technisch ungueltig, sobald eine dieser Invarianten
nicht besteht:

- identische Runtime-, Binary- und Assetidentitaet;
- frischer isolierter Browserkontext je Bedingung;
- frisches, identisch aufgebautes Feld je Bedingung;
- identische Dauer, Geometrie, Raten, Rezeptoren und Ereignisanzahlen;
- exakt gleiche visuelle Rezeptorwertfolge A0/C0;
- gleiche PCM-Sampleanzahl, Tonfrequenz, aktive Tondauer und Gain;
- gleiche auditive Gesamtenergie innerhalb einer vorab implementierten
  numerischen Toleranz;
- genau 300 ms Differenz der auditiven Aktivitaetslage;
- keine externen Requests und keine Rohpayloadhaltung;
- vollstaendiger Audio-, Seiten-, Kontext- und Browserschluss.

Die numerische Energietoleranz muss W1-J aus der verwendeten Float64-
Berechnung begruenden und vor jeder realen Ausfuehrung festschreiben. Sie darf
nicht nach Sichtung eines realen Ergebnisses angepasst werden.

## Skalare Vergleichsgroessen

Ein Digestunterschied allein ist kein Messwert. W1-J muss mindestens folgende
skalare Rollen berechnen, ohne PNG, PCM, Rezeptorfolgen oder Feldtrajektorien
zu serialisieren:

```text
visual_sequence_exact_match
audio_total_energy_a0
audio_total_energy_c0
audio_total_energy_relative_error
activation_final_l1
activation_final_linf
afterimage_final_linf
field_snapshot_digest_a0
field_snapshot_digest_c0
all_input_invariants_hold
all_lifecycle_boundaries_closed
raw_payloads_retained=false
```

`activation_final_l1` und `activation_final_linf` vergleichen korrespondierende
Neuronen der zwei frisch aufgebauten Felder. `afterimage_final_linf` muss in
dieser Scheibe exakt null bleiben; ein anderer Wert zeigt Konfigurationsdrift.

Ein Unterschied groesser als die vorab gebundene numerische Toleranz bedeutet
nur `TECHNICAL_FIELD_INPUT_TIMING_SENSITIVITY_OBSERVED`. Exakte Gleichheit
bedeutet nur `TECHNICAL_FINAL_FIELD_STATE_INDIFFERENT_IN_THIS_CONTRACT`.
Keine der beiden Entscheidungen ist ein Memory-, Feldzeit- oder KI-Befund.

## Ausfuehrungsreihenfolge

W1-I gibt keine reale Paarwelt frei. Die naechsten Scheiben bleiben getrennt:

```text
W1-J: Paarvertrag und skalaren Comparator implementieren, nur Fakes
W1-K: genau ein technischer Realpaar-Smoke zur Quellen- und Kontrollabnahme
spaeter: eigene Vorregistrierung fuer Wiederholung und Forschungsbewertung
```

Ein einzelnes W1-K-Paar darf keine Wiederholbarkeit belegen. Fuer eine
spaetere Forschungsbewertung muessen Reihenfolge, Wiederholungszahl,
Toleranzen und Gegenhypothese vor dem ersten Forschungslauf separat gebunden
werden.

## Verbotene Auswertungen

- keine Objekt-, Ereignis- oder Bedeutungslabels;
- kein Reward und kein Zielzustand;
- keine gewuenschte Feldantwort;
- kein Training und keine Parameteranpassung;
- keine Auswahl einer Metrik nach Ergebnisansicht;
- kein Ableiten von Praegung, Memory, Feldzeit, Organisation, Semantik,
  Selbstregulation oder KI;
- keine Reaktivierung von Z4 oder Lauf 197.

## W1-I-Entscheidung

```text
Forschungsfrage:                 gebunden
unabhaengige Variation:          AV-Zeitkopplung, genau 300 ms
marginal angeglichene Kontrolle: C0 gebunden
visuelle Abtastbarkeit:          9 Frames in Bewegungsphase gebunden
zeitgeordneter Handoff:          statisch vorhanden
skalare Vergleichsrollen:        gebunden
Implementierung:                 nein
Browserstart:                    nein
Forschungslauf:                  nein
```

## Bester naechster Schritt

W1-J implementiert die zwei festen Weltvertraege, ihre gemeinsamen
Quellen-/Rezeptorfabriken und einen injizierbaren Paar-Comparator. Die erste
Abnahme verwendet ausschliesslich synthetische Payloads und Fake-Playwright-
Lifecycles. Ein realer Browserstart bleibt bis zu einer gesonderten W1-K-
Entscheidung gesperrt.
